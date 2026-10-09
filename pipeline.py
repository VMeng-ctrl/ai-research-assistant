# AI 研究助手 · 主程序（流水线：搜索员 -> 整理员 -> 撰写员 -> 审校员）
# 两种用法：
#   命令行测试：python pipeline.py            （走最下面的 __main__ 开关）
#   界面调用：  from pipeline import research  （开关不触发，只把函数搬走）
import os
from openai import OpenAI
from dotenv import load_dotenv

from tools import web_search, read_page

# 本地有 .env 就读；线上（Streamlit Cloud）没有这个文件，密钥从环境变量来
if os.path.exists(r"C:\Users\24554\Projects\AI-Study\代码练习\.env"):
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


def research(问题, log=print):
    """完整跑一遍研究流水线，return 各阶段产物的字典"""
    # ========== 搜索员：人话问题 -> 关键词 -> 搜索 ==========
    searcher = {
        "role": "搜索员",
        "goal": "把用户的问题变成能搜出好结果的关键词",
        "backstory": "你懂搜索引擎的脾气，知道它只吃短、准、名词化的词",
    }
    关键词 = run(searcher,
        f"把下面的问题改写成搜索引擎关键词（3-6个词，空格分隔，只留名词和动词）。"
        f"规则：核心主体必须放开头，绝对不要把年份放在第一个词：\n{问题}")
    关键词 = 关键词.strip().strip("“”\"")
    log(f"搜索员改写为：{关键词}")

    results = web_search(关键词, count=3)
    log(f"搜索员找到 {len(results)} 条")
    for item in results:
        log(f" - {item['title'][:50]}")

    # ========== 整理员（第1步）：把网页正文收回来 ==========
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
                log(f"跳过空页 ← {item['title'][:30]}")
                continue
            contents.append(f"【来源：{item['title']}】\n{正文}")
            log(f"读取成功 {len(正文)} 字 ← {item['title'][:30]}")
        except Exception as e:
            log(f"读取失败 {item['url'][:50]} | {type(e).__name__}")

    doc = "\n\n".join(contents)
    if not doc:
        return {"关键词": 关键词, "links": [], "要点": "",
                "报告": "没有搜到可用资料，换个问法再试。", "审校意见": ""}
    log(f"资料袋共 {len(doc)} 字")

    # ========== 整理员（第2步）：长资料压成要点 ==========
    要点 = run(collector, f"把下面的资料压缩成要点列表，保留关键事实和数据，注明来源：\n{doc}")
    log("整理员：资料已压缩成要点")

    # ========== 撰写员：要点 -> 报告 ==========
    writer = {
        "role": "撰写员",
        "goal": "把要点写成流畅、有条理的研究报告",
        "backstory": "你文笔好，擅长用大白话讲清楚技术的事",
    }
    报告 = run(writer, f"根据下面的要点写一篇400字研究报告，结尾列出信息来源：\n{要点}")
    log("撰写员：报告写完")

    # ========== 审校员：对照资料挑错（不靠记忆） ==========
    reviewer = {
        "role": "审校员",
        "goal": "对照参考资料挑出报告里的错误和无来源的说法",
        "backstory": "你严格，但讲证据：只依据参考资料判断，参考资料没写的才标注'待核实'，不凭自己的记忆下结论",
    }
    审校意见 = run(reviewer,
        f"【报告】\n{报告}\n\n【参考资料（搜索来的原文）】\n{doc}\n\n"
        f"请对照参考资料挑出报告的问题和修改建议，注明出处。")
    log("审校员：检查完毕")

    return {
        "关键词": 关键词,
        "links": [{"title": i["title"], "url": i["url"]} for i in results],
        "要点": 要点,
        "报告": 报告,
        "审校意见": 审校意见,
    }


if __name__ == "__main__":
    # 只有直接运行本文件才执行；被 import 时跳过
    out = research("2026年 DeepSeek 发布了哪些新模型")
    print("\n===== 报告 =====\n", out["报告"])
    print("\n===== 审校意见 =====\n", out["审校意见"])
