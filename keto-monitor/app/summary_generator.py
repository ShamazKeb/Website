from datetime import datetime
from app.models import Topic, Summary, TopicArticle, Article
from app.llm_client import call_openai

def update_summaries_for_recent_topics(session):
    """
    Real AI Implementation:
    1. Iterates over all topics.
    2. Checks if summary is missing or outdated (more articles now than at generation time).
    3. Generates new summary via OpenAI.
    4. Updates/Creates Summary record.
    """
    print("--- Starting Summary Generator (OpenAI) ---")
    
    all_topics = session.query(Topic).all()
    updated_count = 0
    
    for topic in all_topics:
        # 1. Get current articles
        # Join TopicArticle -> Article to get article details
        articles = session.query(Article).join(TopicArticle).filter(TopicArticle.topic_id == topic.id).all()
        current_article_count = len(articles)
        
        if current_article_count == 0:
            continue

        # 2. Check existing summary
        summary = session.query(Summary).filter_by(topic_id=topic.id).first()
        
        should_generate = False
        reason = ""
        
        if not summary:
            should_generate = True
            reason = "No summary exists"
        elif current_article_count > summary.article_count_at_generation:
            should_generate = True
            reason = f"New articles detected ({summary.article_count_at_generation} -> {current_article_count})"
        
        if not should_generate:
            print(f"Skipping Topic '{topic.title}': Up-to-date.")
            continue
            
        print(f"Generating Summary for '{topic.title}' ({reason})...")
        
        # 3. Construct Prompt
        system_prompt = (
            "Du bist ein professioneller Nachrichteneditor und verfasst kurze, präzise Zusammenfassungen von Artikeln zu Unternehmensnachrichten.\n"
            "Anforderungen:\n"
            "- maximal 6 Sätze\n"
            "- sachlich, neutral, ohne Marketing-Sprache\n"
            "- keine Wiederholungen\n"
            "- fokussiere dich auf die zentrale Neuigkeit (Was? Wer? Wann?)\n"
            "- keine Einleitung, keine Aufzählungen, keine Meta-Kommentare\n"
            "Antworte ausschließlich mit der fertigen Fließtext-Zusammenfassung."
)
        
        user_prompt_lines = [
            f"Firma: {topic.company.name}",
            f"Topic: {topic.title}",
            "\nArtikel:"
        ]
        
        for idx, art in enumerate(articles, 1):
            content_text = art.content if art.content else "No content available."
            excerpt = (content_text[:500] + "...") if len(content_text) > 500 else content_text
            
            user_prompt_lines.append(f"{idx}) Titel: {art.title}")
            user_prompt_lines.append(f"   Quelle: {art.source_name}")
            user_prompt_lines.append(f"   Inhalt (Auszug): {excerpt}")
        
        user_prompt_lines.append("\nBitte schreibe eine kurze, sachliche Zusammenfassung auf Deutsch.")
        user_prompt = "\n".join(user_prompt_lines)
        
        try:
            # 4. Call OpenAI
            summary_text = call_openai(system_prompt, user_prompt)
            
            # 5. Save/Update
            if not summary:
                summary = Summary(topic_id=topic.id)
                session.add(summary)
            
            summary.summary_text = summary_text
            summary.generated_at = datetime.utcnow()
            summary.article_count_at_generation = current_article_count
            
            session.commit()
            updated_count += 1
            print(f"  -> Summary updated.")
            
        except Exception as e:
            print(f"ERROR generating summary for topic {topic.id}: {e}")
            session.rollback()
            
    print(f"--- Finished. Updated/Created {updated_count} summaries. ---")
    return updated_count
