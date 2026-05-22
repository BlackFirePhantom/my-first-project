import os
import sys

# Add project root to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from novel_sources import linovelib

def test_search_by_id():
    print("\n=== Testing Search by ID (1) ===")
    try:
        res = linovelib.search("1")
        print("Success!")
        print("Results:", res)
        assert len(res) == 1
        assert "恶魔高校" in res[0]["name"]
        assert "石踏一荣" in res[0]["author"]
        assert res[0]["url"] == "https://www.linovelib.com/novel/1.html"
    except Exception as e:
        print("Failed:", e)
        assert False

def test_search_by_url():
    print("\n=== Testing Search by URL (bilinovel) ===")
    try:
        res = linovelib.search("https://www.bilinovel.com/novel/1.html")
        print("Success!")
        print("Results:", res)
        assert len(res) == 1
        assert "恶魔高校" in res[0]["name"]
        assert "石踏一荣" in res[0]["author"]
        assert res[0]["url"] == "https://www.bilinovel.com/novel/1.html"
    except Exception as e:
        print("Failed:", e)
        assert False

def test_search_blocked_keyword():
    print("\n=== Testing Search with keyword (blocked) ===")
    try:
        linovelib.search("无职转生")
        print("Error: Keyword search should have raised an exception but succeeded instead.")
        assert False
    except Exception as e:
        print("Success: Raised expected exception!")
        print("Exception message:\n", e)
        assert "无法直接进行关键词搜索" in str(e)

def test_get_chapters():
    print("\n=== Testing Get Chapters ===")
    try:
        chapters = linovelib.get_chapters("https://www.linovelib.com/novel/1.html", force_refresh=True)
        print("Success!")
        print("Total chapters found:", len(chapters))
        assert len(chapters) > 0
        
        # Print first few chapters
        for i, c in enumerate(chapters[:5]):
            print(f"  {i+1}: {c['title']} -> {c['url']}")
            
        # Check volume title prefixing
        assert "旧校舍的恶魔" in chapters[1]["title"]
        assert "[" in chapters[1]["title"]
        assert "]" in chapters[1]["title"]
    except Exception as e:
        print("Failed:", e)
        assert False

def test_get_content():
    print("\n=== Testing Get Content ===")
    try:
        # Chapter 2 is multi-page: 2.html and 2_2.html
        content = linovelib.get_content("https://www.linovelib.com/novel/1/2.html")
        print("Success!")
        print("Content length:", len(content))
        print("Content preview (first 300 chars):")
        print(content[:300])
        print("...")
        assert len(content) > 1000
        
        # Verify pagination works by checking text from both page 1 and page 2
        # Page 1: "和那个人的发色一样"
        # Page 2: "我原本也以为这是不是什么整人企划"
        assert "和那个人的发色一样" in content
        assert "兵藤一诚" in content
        
        # Verify <rt> tag decomposition
        # Original: <ruby>神器<rt>sacred gear</rt></ruby>
        # Cleaned: 神器 (no "sacred gear" adjacent or merged incorrectly)
        assert "神器" in content
        assert "sacred gear" not in content
    except Exception as e:
        print("Failed:", e)
        assert False

if __name__ == "__main__":
    test_search_by_id()
    test_search_by_url()
    test_search_blocked_keyword()
    test_get_chapters()
    test_get_content()
    print("\nALL AUTOMATED TESTS PASSED!")
