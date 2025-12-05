from app.article_filter import filter_articles_batch
from unittest.mock import patch, MagicMock

def test_batch_filter():
    print("--- Test: Batch Article Filter ---")
    
    articles = [
        {"title": "Relevant 1", "content": "New Product Launch", "url": "u1"},
        {"title": "Irrelevant 1", "content": "Opinion Piece", "url": "u2"},
        {"title": "Relevant 2", "content": "Merger Announced", "url": "u3"},
        {"title": "Irrelevant 2", "content": "Top 10 list", "url": "u4"},
    ]
    
    # Mock OpenAI Response
    mock_response = """
    ```json
    [
        {"index": 0, "relevant": true},
        {"index": 1, "relevant": false},
        {"index": 2, "relevant": true},
        {"index": 3, "relevant": false}
    ]
    ```
    """
    
    with patch('app.article_filter.call_openai', return_value=mock_response) as mock_call:
        filtered = filter_articles_batch(articles, "Test Corp")
        
        print(f"Input: {len(articles)} articles")
        print(f"Output: {len(filtered)} articles")
        
        assert len(filtered) == 2
        assert filtered[0]['title'] == "Relevant 1"
        assert filtered[1]['title'] == "Relevant 2"
        
        print("-> Batch Logic PASS")

if __name__ == "__main__":
    test_batch_filter()
