# 已知问题与调试档案（v5，2026-10-09）

## 问题现象
线上问"deepseek2026年发布的新模型"，报告输出的是 DeepSeek 公司简介（答非所问）。
本地同样查询能搜到正经报道（V4.1 发布等）。

## 已排除的原因（都有日志证据）
1. ~~密钥缺失~~ → Secrets 已配好，链路全通
2. ~~JS 空壳页~~ → 已加过滤 + 摘要兜底（至少能出报告）
3. ~~Bing 给垃圾结果~~ → 已加两道质检（相关性 + 首页率）
4. ~~跳转链接没还原~~ → v5 已加 `_unwrap_bing()`，含 `&amp;` 实体还原

## 当前根因（待验证）
v5 日志显示：云端 Bing 对数据中心 IP 返回的 8 条全是 DeepSeek 官网页，
即便链接还原后首页率应=100% 触发换引擎 —— **若 v5 换 DuckDuckGo 后
仍输出公司简介，则问题在 DDG 结果的摘要内容也不含具体型号**，
或云端读取全挂后摘要兜底的素材本身太薄（917 字）。

## 下次接手时的三步
1. 让用户跑一次，**看 v5 日志**：
   - `Bing：...100% 是官网首页，换引擎` 有没有出现？
   - `DuckDuckGo：N 条` 的 URL 是不是文章链接（带路径）？
2. 若 DDG 也不给力 → 方案 B：**搜索结果里只留带路径的深链接**，
   或加第三个引擎（云上可访问 Google/Bing News）
3. 云端读取全挂的问题 → 可试：请求头更全（Referer/Accept）、
   或接受"只靠摘要"但把摘要数从 8 加到 12

## 关键代码位置
- `tools.py`：`_search_bing` / `_search_ddg` / `_unwrap_bing` / `_relevant`
  / `_homepage_rate` / `web_search`（质检调度）
- `pipeline.py`：`research()` 四人流水线 + 摘要兜底
- 页面版本号：`app.py` 里的 `st.caption`（每次改行为必更新）

## 环境备忘
- 本地 IP 已被 Bing 临时拉黑（返回酷家乐/B站垃圾），**调试以线上为准**
- 推送需 `GIT_SSL_NO_VERIFY=true git push`（代理证书问题，勿开全局）
- 本地跑代码用 `C:/Users/24554/AppData/Local/Python/pythoncore-3.14-64/python.exe`
