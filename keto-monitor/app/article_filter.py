import os
import json
import time
from app.llm_client import call_openai

def filter_articles_batch(articles, company_name):
    """
    Filters a list of articles for relevance using OpenAI in batches.
    Uses OPENAI_API_KEY_SECONDARY if available to distribute load.
    
    Args:
        articles: List of dicts [{'title':..., 'content':..., 'url':...}]
        company_name: Name of the company
        
    Returns:
        List of relevant articles (subset of input).
    """
    # Prefer Secondary Key for Filtering to save Primary for Summaries
    api_key = os.getenv("OPENAI_API_KEY_SECONDARY") or os.getenv("OPENAI_API_KEY")
    
    relevant_articles = []
    BATCH_SIZE = 20
    
    print(f"  -> Filtering {len(articles)} articles for {company_name} (Batch Size: {BATCH_SIZE})...")
    
    # Chunking
    for i in range(0, len(articles), BATCH_SIZE):
        batch = articles[i:i + BATCH_SIZE]
        print(f"    -> Processing batch {i//BATCH_SIZE + 1} ({len(batch)} articles)...")
        
        system_prompt = (
            "Du bist ein Filter für Unternehmensnachrichten.\n"
            "Entscheide für jeden Artikel, ob er **konkretes, aktuelles Firmengeschehen** beschreibt.\n\n"
            "Relevant (true):\n"
            "- Neue Produkte, Services, Projekte\n"
            "- Übernahmen, Partnerschaften, Investitionen\n"
            "- Führungskräftewechsel, Strategieänderungen\n"
            "- Quartalszahlen, finanzielle Ankündigungen\n\n"
            "Irrelevant (false):\n"
            "- Allgemeine Branchentrends ohne Firmenfokus\n"
            "- Meinungsartikel, Analysten-Gerede\n"
            "- Alte News oder irrelevante Erwähnungen\n\n"
            "Antworte ausschließlich mit **gültigem JSON**:\n"
            "Eine Liste von Objekten: [{\"index\": 0, \"relevant\": true}, ...]"
        )
        
        user_prompt_lines = [f"Firma: {company_name}", "Artikel:"]
        for idx, art in enumerate(batch):
            content_excerpt = art.get('content', '')[:300].replace('\n', ' ')
            user_prompt_lines.append(f"- Index {idx}: Titel: \"{art['title']}\", Inhalt: \"{content_excerpt}\"")
            
        user_prompt = "\n".join(user_prompt_lines)
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # API Call
                response = call_openai(system_prompt, user_prompt, model="gpt-4o-mini", api_key=api_key)
                
                if response.startswith("Error:"):
                    raise Exception(f"API Call Failed: {response}")

                # Clean JSON
                if "```json" in response:
                    response = response.split("```json")[1].split("```")[0].strip()
                elif "```" in response:
                    response = response.split("```")[1].split("```")[0].strip()
                    
                results = json.loads(response)
                
                # Map results back to articles
                batch_relevant_count = 0
                for item in results:
                    idx = item.get("index")
                    is_rel = item.get("relevant")
                    
                    if idx is not None and 0 <= idx < len(batch):
                        if is_rel:
                            relevant_articles.append(batch[idx])
                            batch_relevant_count += 1
                        else:
                            # Log irrelevant (optional, verbose)
                            pass
                            
                print(f"      -> Batch result: {batch_relevant_count}/{len(batch)} relevant.")
                break # Success, exit retry loop
                
            except Exception as e:
                print(f"      -> Error in batch filter (Attempt {attempt+1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 * (attempt + 1))
                else:
                    print("      -> Skipping batch due to repeated errors.")
                    
        # Rate Limit Pause between batches
        time.sleep(1)

    return relevant_articles

# Keep single function for backward compatibility if needed, or just remove it.
# We will update news_fetcher to use the batch function.
