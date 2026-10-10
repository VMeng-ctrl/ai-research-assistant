# 🔍 AI 研究助手

输入一个问题，四个 AI 角色自动分工完成研究：搜资料 → 读网页 → 写报告 → 挑错。

## 🌐 在线试用

**https://ai-research-assistant-k9qetcuh3jbkw4tsslqy4j.streamlit.app/**

## 四人小队

| 角色 | 干什么 | 用什么工具 |
|---|---|---|
| 搜索员 | 把人话问题改写成搜索关键词（query rewriting） | Bing 搜索 |
| 资料整理员 | 读取网页、剔除空壳页、压缩成要点 | 自写网页正文提取 |
| 撰写员 | 把要点写成带来源的研究报告 | DeepSeek API |
| 审校员 | **对照原始资料**逐条挑错，不凭记忆下结论 | DeepSeek API |

## 设计要点

- **搜索关键词改写**：实测发现年份开头会毁掉 Bing 结果，规则写进了提示词
- **空壳页过滤**：JS 渲染的网页撕完标签不足 100 字，直接跳过
- **审校员对照证据**：把搜索到的原文一起喂给它，避免"用记忆冒充证据"

## 本地运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

命令行测试版（不启界面）：

```bash
python pipeline.py
```

## 技术栈

Python 3.14 · Streamlit · OpenAI SDK（DeepSeek 兼容接口）· Bing 网页抓取
