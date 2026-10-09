# AI 研究助手 · 工具箱
import urllib.request
import re
import html


def read_page(url, max_chars=3000):
    """读取一个网页，撕掉标签，返回纯文字（最多 max_chars 字）"""
    req = urllib.request.Request(url, headers={
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0 Safari/537.36"),
        "Accept-Language": "zh-CN,zh;q=0.9",
    })
    body = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "ignore")

    # 1) 先整段干掉 script / style（它们肚里全是代码和样式，不是文章）
    body = re.sub(r"<script.*?</script>|<style.*?</style>", "", body, flags=re.S)
    # 2) 再把剩下的标签换成空格（防止字黏在一起）
    text = re.sub(r"<[^>]+>", " ", body)
    # 3) HTML 实体转回正常字符（&amp; → & 等）
    text = html.unescape(text)
    # 4) 连续空白压成一个空格，去首尾
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]


def web_search(query, count=5):
    """用 Bing 搜网页，返回 [{title, url, snippet}]"""
    import urllib.parse
    url = (f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
           f"&setlang=zh-CN&count={count}")
    req = urllib.request.Request(url, headers={
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0 Safari/537.36"),
        "Accept-Language": "zh-CN,zh;q=0.9"})
    body = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "ignore")
    clean = lambda s: html.unescape(re.sub(r"<[^>]+>", "", s)).strip()
    results = []
    for block in re.split(r'<li class="b_algo"', body)[1:count+1]:
        m = re.search(r'<h2[^>]*><a[^>]*href="([^"]+)"[^>]*>(.*?)</a></h2>', block, re.S)
        if not m:
            continue
        s = re.search(r'<p[^>]*>(.*?)</p>', block, re.S)
        results.append({"title": clean(m.group(2)), "url": m.group(1),
                        "snippet": clean(s.group(1)) if s else ""})
    return results


if __name__ == "__main__":
    t = read_page("https://www.deepseek.com/")
    print(f"读到 {len(t)} 字：")
    print(t[:600])
