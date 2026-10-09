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


def _fetch(url, timeout=15):
    """下载一个 URL 的 HTML"""
    req = urllib.request.Request(url, headers={
        "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0 Safari/537.36"),
        "Accept-Language": "zh-CN,zh;q=0.9"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")


def _search_bing(query, count=8):
    """Bing 搜索（本地住宅 IP 效果好；云服务器数据中心 IP 可能拿到垃圾）"""
    import urllib.parse
    body = _fetch("https://www.bing.com/search?q="
                  + urllib.parse.quote(query) + f"&setlang=zh-CN&count={count}")
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


def _search_ddg(query, count=8):
    """DuckDuckGo 搜索（云服务器在美国能用；本地国内不通）"""
    import urllib.parse
    body = _fetch("https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query),
                  timeout=10)
    clean = lambda s: html.unescape(re.sub(r"<[^>]+>", "", s)).strip()
    # 标题链接：class 里带 result__a / result-link 的 <a>
    links = []
    for attrs, text in re.findall(r"<a\s+([^>]+)>(.*?)</a>", body, re.S):
        if "result__a" not in attrs and "result-link" not in attrs:
            continue
        h = re.search(r'href="([^"]+)"', attrs)
        if not h:
            continue
        href = h.group(1)
        # DDG 的跳转链接：//duckduckgo.com/l/?uddg=真实地址
        if "uddg=" in href:
            qs = urllib.parse.parse_qs(urllib.parse.urlparse("https:" + href).query)
            href = qs.get("uddg", [href])[0]
        elif href.startswith("//"):
            href = "https:" + href
        links.append({"title": clean(text), "url": href})
    # 摘要：class 里带 result__snippet / result-snippet 的 <a>
    snippets = []
    for attrs, text in re.findall(r"<a\s+([^>]+)>(.*?)</a>", body, re.S):
        if "result__snippet" in attrs or "result-snippet" in attrs:
            snippets.append(clean(text))
    for i, item in enumerate(links[:count]):
        item["snippet"] = snippets[i] if i < len(snippets) else ""
    return links[:count]


def _relevant(results, query):
    """结果相关性校验：问题的相邻字组至少命中2个，否则判定为垃圾结果"""
    if not results or len(query) < 2:
        return bool(results)
    grams = [query[i:i+2] for i in range(len(query)-1)
             if not query[i].isspace() and not query[i+1].isspace()]
    blob = " ".join(r["title"] + " " + r["snippet"] for r in results)
    hits = sum(1 for g in grams if g in blob)
    return hits >= 2


def web_search(query, count=8, log=print):
    """双引擎搜索：先 Bing，结果与问题不相关（如云服务器IP被降级）则换 DuckDuckGo。
    都失败/都垃圾时 return []（调用方给用户友好提示）。"""
    for name, engine in (("Bing", _search_bing), ("DuckDuckGo", _search_ddg)):
        try:
            rs = engine(query, count)
        except Exception as e:
            log(f"{name} 搜索异常：{type(e).__name__}")
            rs = []
        if not rs:
            log(f"{name}：0 条结果")
            continue
        if _relevant(rs, query):
            log(f"{name}：{len(rs)} 条，相关性检查通过")
            return rs
        log(f"{name}：拿到 {len(rs)} 条但与问题对不上（疑似降级/垃圾结果），换引擎")
    return []


if __name__ == "__main__":
    t = read_page("https://www.deepseek.com/")
    print(f"读到 {len(t)} 字：")
    print(t[:600])
