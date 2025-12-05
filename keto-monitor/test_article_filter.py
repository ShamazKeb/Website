from app.article_filter import is_article_relevant

def main():
    print("--- Test: AI Article Filter ---")
    
    company = "Keto Software"
    
    test_cases = [
        {
            "title": "Keto Software launches new AI Portfolio Manager",
            "content": "Today, Keto Software announced the release of their new AI-driven tool...",
            "expected": True,
            "desc": "Relevant (New Product)"
        },
        {
            "title": "Why Project Management Software is growing",
            "content": "The market for PM software is expected to grow by 10%...",
            "expected": False,
            "desc": "Irrelevant (General Trend)"
        },
        {
            "title": "Keto Software appoints new CEO",
            "content": "John Doe has been named the new CEO of Keto Software...",
            "expected": True,
            "desc": "Relevant (Leadership Change)"
        },
        {
            "title": "Top 10 Tools for 2025",
            "content": "Here is a list of tools including Jira, Asana, and others...",
            "expected": False,
            "desc": "Irrelevant (Listicle/Mention)"
        }
    ]
    
    passed = 0
    for i, case in enumerate(test_cases):
        print(f"\nCase {i+1}: {case['desc']}")
        print(f"Title: {case['title']}")
        
        result = is_article_relevant(case['title'], case['content'], company)
        print(f"  -> AI Result: {result}")
        
        if result == case['expected']:
            print("  -> PASS")
            passed += 1
        else:
            print(f"  -> FAIL (Expected {case['expected']})")
            
    print(f"\n--- Result: {passed}/{len(test_cases)} passed ---")

if __name__ == "__main__":
    main()
