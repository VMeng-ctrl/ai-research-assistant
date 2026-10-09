# AI 研究助手 · Streamlit 界面
# 本地跑：  streamlit run app.py
# 线上跑：  Streamlit Cloud 会自动执行这一行
import os
import streamlit as st

# 线上没有本地 .env 文件，密钥从 Streamlit Cloud 的 Secrets 读；
# 本地则由 .env 提供（pipeline.py 负责），所以这段包在 try 里
if "DEEPSEEK_API_KEY" not in os.environ:
    try:
        os.environ["DEEPSEEK_API_KEY"] = st.secrets["DEEPSEEK_API_KEY"]
    except Exception:
        pass  # 本地：靠 pipeline.py 读 .env

from pipeline import research   # 只搬函数进来，__main__ 开关不会触发

st.set_page_config(page_title="AI 研究助手", page_icon="🔍", layout="wide")

st.title("🔍 AI 研究助手")
st.caption("四人小队：搜索员 → 整理员 → 撰写员 → 审校员 · 输入问题，自动搜资料、写报告、挑错")

问题 = st.text_input(
    "你想研究什么问题？",
    placeholder="例如：2026年 DeepSeek 发布了哪些新模型",
)

if st.button("🚀 开始研究", type="primary"):
    if not 问题.strip():
        st.warning("先输入一个问题再开始")
    else:
        with st.spinner("四人小队工作中…… 大约 30-60 秒"):
            out = research(问题, log=lambda m: st.write(f"⚙️ {m}"))
        st.success("研究完成！")

        st.subheader("📄 研究报告")
        st.markdown(out["报告"])

        st.subheader("🔍 审校员意见")
        with st.expander("展开审校意见（对照资料逐条挑错）"):
            st.markdown(out["审校意见"])

        with st.expander("📚 过程与来源"):
            st.write(f"**搜索关键词**：{out['关键词']}")
            for l in out["links"]:
                st.write(f"- [{l['title']}]({l['url']})")
            st.text_area("整理员的要点", out["要点"], height=200)
