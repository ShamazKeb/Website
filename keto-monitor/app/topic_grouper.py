import json
from datetime import datetime
from app.models import Article, Topic, TopicArticle, Company
from app.llm_client import call_openai

def chunk_list(lst, size):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

def assign_topics_to_new_articles(session):
    """
    Real AI Implementation (Refined):
    1. Finds articles not yet linked to any topic.
    2. Groups them by Company.
    3. Sends batches (max 20) to OpenAI to get topic assignments (JSON).
    4. Creates/Updates Topics and links Articles.
    """
    print("--- Starting Topic Grouper (OpenAI) ---")
    
    # 1. Find unassigned articles
    unassigned_articles = session.query(Article).outerjoin(TopicArticle).filter(TopicArticle.id == None).all()
    
    if not unassigned_articles:
        print("No new articles to group.")
        return 0

    print(f"Found {len(unassigned_articles)} unassigned articles.")

    # 2. Group by Company
    articles_by_company = {}
    for article in unassigned_articles:
        if article.company_id not in articles_by_company:
            articles_by_company[article.company_id] = []
        articles_by_company[article.company_id].append(article)

    total_new_topics = 0
    total_links = 0
    BATCH_SIZE = 20

    # 3. Process per Company
    for company_id, articles in articles_by_company.items():
        company = session.query(Company).get(company_id)
        if not company:
            continue
            
        print(f"Processing {len(articles)} articles for {company.name}...")
        
        # Batching
        for batch_idx, batch in enumerate(chunk_list(articles, BATCH_SIZE)):
            print(f"  -> Batch {batch_idx + 1} with {len(batch)} articles...")
            
            # Prepare Prompt
            system_prompt = (
                "Du gruppierst Nachrichtenartikel einer Firma thematisch.\n"
                "Artikel, die dieselbe Neuigkeit behandeln, erhalten denselben \"topic_key\" und \"topic_title\".\n"
                "Achte auf Konsistenz bei der Benennung: gleiche Ereignisse → identischer Key und Titel.\n\n"
                "Antworte ausschließlich mit **gültigem JSON** (UTF-8, keine Kommentare, keine Erklärungen).\n"
                "Jeder Artikel muss ein Objekt mit folgenden Feldern enthalten:\n"
                "- article_id (int)\n"
                "- topic_key (string, maschinenlesbar: lowercase, snake_case, prägnant)\n"
                "- topic_title (string, menschlich lesbar: max. 10 Wörter)\n\n"
                "Format:\n"
                "[\n"
                "  {\n"
                "    \"article_id\": 123,\n"
                "    \"topic_key\": \"keto_ai_dashboard_launch\",\n"
                "    \"topic_title\": \"Keto veröffentlicht KI-Dashboard\"\n"
                "  },\n"
                "  ...\n"
                "]"
            )

            
            user_prompt_lines = [f"Firma: {company.name} ({company.slug})", "Artikel:"]
            for art in batch:
                # Content Excerpt (max 400 chars)
                content_text = art.content if art.content else "No content available."
                content_excerpt = (content_text[:400] + "...") if len(content_text) > 400 else content_text
                
                user_prompt_lines.append(f"- ID: {art.id}, Titel: \"{art.title}\", Content-Excerpt: \"{content_excerpt}\"")
            
            user_prompt = "\n".join(user_prompt_lines)
            
            try:
                # Call OpenAI
                response_text = call_openai(system_prompt, user_prompt)
                
                # Clean response
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                    
                # Parse JSON
                assignments = json.loads(response_text)
                
                batch_new_topics = 0
                batch_links = 0
                
                # Process Assignments
                for item in assignments:
                    art_id = item.get("article_id")
                    t_key = item.get("topic_key")
                    t_title = item.get("topic_title")
                    
                    if not all([art_id, t_key, t_title]):
                        print(f"Skipping invalid item: {item}")
                        continue
                    
                    # Find or Create Topic
                    topic = session.query(Topic).filter_by(company_id=company_id, topic_key=t_key).first()
                    if not topic:
                        topic = Topic(
                            company_id=company_id,
                            topic_key=t_key,
                            title=t_title,
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                        session.add(topic)
                        session.flush() # get ID
                        batch_new_topics += 1
                        total_new_topics += 1
                    else:
                        # Update timestamp
                        topic.updated_at = datetime.utcnow()
                    
                    # Create Link (if not exists)
                    link = session.query(TopicArticle).filter_by(topic_id=topic.id, article_id=art_id).first()
                    if not link:
                        link = TopicArticle(topic_id=topic.id, article_id=art_id)
                        session.add(link)
                        batch_links += 1
                        total_links += 1
                
                session.commit()
                print(f"    -> Batch complete. New Topics: {batch_new_topics}, Assignments: {batch_links}")
                
            except json.JSONDecodeError as e:
                print(f"ERROR: Failed to parse JSON from OpenAI for {company.name}: {e}")
                print(f"Response was: {response_text}")
            except Exception as e:
                print(f"ERROR processing batch for {company.name}: {e}")
                session.rollback()

    print(f"--- Finished. Created {total_new_topics} new topics, linked {total_links} articles. ---")
    return total_new_topics
