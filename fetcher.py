import urllib.request
import json
import xml.etree.ElementTree as ET
import logging

logging.basicConfig(level=logging.INFO)

def fetch_reddit_ai_hot(limit=5):
    """抓取 Reddit (r/MachineLearning, r/Artificial) 热门讨论（高赞/高评论）"""
    url = "https://www.reddit.com/r/MachineLearning/hot.json?limit=10"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    posts = []
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            for item in data.get('data', {}).get('children', []):
                post_data = item['data']
                # 过滤机制：只取评论数 > 30 或 赞数 > 50 的高质量热门讨论
                if post_data.get('num_comments', 0) > 30 or post_data.get('score', 0) > 50:
                    posts.append({
                        "title": post_data.get('title'),
                        "source": f"Reddit r/{post_data.get('subreddit')}",
                        "url": post_data.get('url'),
                        "discussion_count": post_data.get('num_comments'),
                        "upvotes": post_data.get('score'),
                        "type": "Community Hot Topic"
                    })
    except Exception as e:
        logging.error(f"Error fetching Reddit: {e}")
    return posts[:limit]

def fetch_tech_blogs():
    """抓取 HackerNews 上的高分前沿趋势与爆款"""
    hn_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    stories = []
    try:
        req = urllib.request.Request(hn_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            ids = json.loads(resp.read().decode('utf-8'))[:25]
            
        for item_id in ids:
            detail_url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
            with urllib.request.urlopen(detail_url, timeout=5) as d_resp:
                item = json.loads(d_resp.read().decode('utf-8'))
                title = item.get('title', '')
                # 只保留含有 AI、LLM、Model、Agent、OpenAI、Twitter/X 话题且分数高于 80 的爆款
                if item.get('score', 0) >= 80 and any(k in title.lower() for k in ['ai', 'llm', 'gpt', 'model', 'agent', 'claude', 'openai', 'deepseek']):
                    stories.append({
                        "title": title,
                        "source": "HackerNews",
                        "url": item.get('url', f"https://news.ycombinator.com/item?id={item_id}"),
                        "score": item.get('score'),
                        "type": "Viral Tech Discussion"
                    })
    except Exception as e:
        logging.error(f"Error fetching Tech Trends: {e}")
    return stories[:5]

def fetch_ai_intelligence(source_type="all"):
    """汇总抓取接口"""
    results = []
    results.extend(fetch_reddit_ai_hot())
    results.extend(fetch_tech_blogs())
    
    logging.info(f"成功抓取 {len(results)} 条符合预筛选条件的高质情报源数据。")
    return results

if __name__ == "__main__":
    data = fetch_ai_intelligence()
    print(json.dumps(data, indent=2, ensure_ascii=False))
