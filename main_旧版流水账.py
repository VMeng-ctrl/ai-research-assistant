# AI 研究助手 · 主程序
# 流水线：搜索员 -> 整理员 -> 撰写员 -> 审校员
import os
from openai import OpenAI
from dotenv import load_dotenv

from tools import web_search, read_page

load_dotenv(r"C:\Users\24554\Projects\AI-Study\代码练习\.env")
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)


def run(agent, task_instruction):
    """让某个 Agent 去干一件 Task，return 干完的结果"""
    prompt = f"""你是：{agent['role']}
你的目标：{agent['goal']}
你的风格：{agent['backstory']}

本次任务：{task_instruction}

请直接输出结果。"""
    resp = client.chat.completions.create(
        model="deepseek-flash",
        messages=[{"role": "user", "content": prompt}],
        extra_body={"thinking": {"type": "disabled"}},
    )
    return resp.choices[0].message.content


# ========== 研究问题 ==========
问题 = "2026年 DeepSeek 发布了哪些新模型"

# ========== 搜索员 ==========
# 第1步：人话问题 -> 搜索关键词（query rewriting）
searcher = {
    "role": "搜索员",
    "goal": "把用户的问题变成能搜出好结果的关键词",
    "backstory": "你懂搜索引擎的脾气，知道它只吃短、准、名词化的词",
}
关键词 = run(searcher,
    f"把下面的问题改写成搜索引擎关键词（3-6个词，空格分隔，只留名词和动词）。"
    f"规则：核心主体必须放开头，绝对不要把年份放在第一个词：\n{问题}")
关键词 = 关键词.strip().strip("“”\"")      # 防止AI多加引号
print("搜索员改写为：", 关键词)

# 第2步：拿关键词去搜
results = web_search(关键词, count=3)
print(f"搜索员找到 {len(results)} 条：")
for item in results:
    print(" -", item["title"][:50])

# ========== 整理员（第1步：把网页正文收回来） ==========
collector = {
    "role": "资料整理员",
    "goal": "把网页里有用的文字收进资料袋，垃圾和空页直接扔掉",
    "backstory": "你严谨细心，知道空壳网页混进来会污染资料",
}
contents = []
for item in results:
    try:
        正文 = read_page(item["url"])
        if len(正文) < 100:                      # 空壳页（JS渲染的）跳过
            print(f"跳过空页 ← {item['title'][:30]}")
            continue
        contents.append(f"【来源：{item['title']}】\n{正文}")
        print(f"读取成功 {len(正文)} 字 ← {item['title'][:30]}")
    except Exception as e:
        print(f"读取失败 {item['url'][:50]} | {type(e).__name__}")

doc = "\n\n".join(contents)
print(f"\n资料袋共 {len(doc)} 字")

# ========== 整理员（第2步：把长资料压成要点） ==========
要点 = run(collector, f"把下面的资料压缩成要点列表，保留关键事实和数据，注明来源：\n{doc}")
print("\n===== 整理员的要点 =====\n", 要点)

# ========== 撰写员 ==========
writer = {
    "role": "撰写员",
    "goal": "把要点写成流畅、有条理的研究报告",
    "backstory": "你文笔好，擅长用大白话讲清楚技术的事",
}
报告 = run(writer, f"根据下面的要点写一篇400字研究报告，结尾列出信息来源：\n{要点}")
print("\n===== 撰写员的报告 =====\n", 报告)

# ========== 审校员（对照资料挑错，不靠记忆） ==========
reviewer = {
    "role": "审校员",
    "goal": "对照参考资料挑出报告里的错误和无来源的说法",
    "backstory": "你严格，但讲证据：只依据参考资料判断，参考资料没写的才标注'待核实'，不凭自己的记忆下结论",
}
审校意见 = run(reviewer,
    f"【报告】\n{报告}\n\n【参考资料（搜索来的原文）】\n{doc}\n\n"
    f"请对照参考资料挑出报告的问题和修改建议，注明出处。")
print("\n===== 审校员的意见 =====\n", 审校意见)
