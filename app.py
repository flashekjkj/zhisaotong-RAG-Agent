import streamlit as st
import requests

# ===================== 【核心】暗色主题 + 固定底部输入框 CSS =====================
st.markdown("""
<style>
/* Streamlit 原生暗色背景 */
.stApp {
    background-color: #0e1117;
}
/* 主容器：防止内容被底部输入框遮挡 */
.main-container {
    max-width: 900px;
    margin: 0 auto;
    padding-bottom: 100px;
}
/* 标题样式 */
.main-title {
    text-align: center;
    color: #ffffff;
    font-weight: 700;
    margin: 10px 0 20px 0;
}
/* 聊天消息全局样式 */
.user-message {
    display: flex;
    justify-content: flex-end;
    margin: 12px 0;
}
.assistant-message {
    display: flex;
    justify-content: flex-start;
    margin: 12px 0;
}
/* 用户气泡：右侧蓝色（暗色主题适配） */
.user-bubble {
    background-color: #0066cc;
    color: white;
    padding: 12px 18px;
    border-radius: 20px 20px 5px 20px;
    max-width: 75%;
    box-shadow: 0 1px 3px rgba(0,0,0,0.3);
}
/* 助手气泡：左侧深灰色 */
.assistant-bubble {
    background-color: #262730;
    color: #f0f0f0;
    padding: 12px 18px;
    border-radius: 20px 20px 20px 5px;
    max-width: 75%;
    box-shadow: 0 1px 3px rgba(0,0,0,0.3);
}
/* 固定底部输入区域：核心！永远贴在页面最下方 */
.bottom-input-area {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: #0e1117;
    padding: 10px 20px 15px 20px;
    z-index: 999;
    border-top: 1px solid #262730;
}
/* 隐藏上传组件标签 */
label[for="file-uploader"] {
    display: none !important;
}
/* 滚动条美化 */
::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-thumb {
    background-color: #262730;
    border-radius: 3px;
}
</style>
""", unsafe_allow_html=True)

# ===================== 页面配置 =====================
st.set_page_config(
    page_title="智扫通多模态智能客服",
    page_icon="🤖",
    layout="wide"
)

# 标题
st.markdown('<h1 class="main-title">🤖 智扫通机器人智能客服</h1>', unsafe_allow_html=True)
st.divider()

# 初始化聊天记录
if "message" not in st.session_state:
    st.session_state["message"] = []

# ===================== 聊天内容展示区域 =====================
st.markdown('<div class="main-container">', unsafe_allow_html=True)
for message in st.session_state["message"]:
    if message["role"] == "user":
        st.markdown(f'''
        <div class="user-message">
            <div class="user-bubble">{message["content"]}</div>
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
        <div class="assistant-message">
            <div class="assistant-bubble">{message["content"]}</div>
        </div>
        ''', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ===================== 【核心】固定在页面最底部的输入栏 =====================
st.markdown('<div class="bottom-input-area">', unsafe_allow_html=True)
# 三栏紧凑布局：输入框 | 上传按钮 | 对齐占位
col1, col2, col3 = st.columns([8, 1.5, 0.5])
with col1:
    prompt = st.chat_input("请输入问题...")
with col2:
    uploaded_file = st.file_uploader(
        "",
        type=["png", "jpg", "jpeg"],
        key="file-uploader",
        label_visibility="collapsed"
    )
with col3:
    st.write("")
st.markdown('</div>', unsafe_allow_html=True)

# ===================== 侧边栏：图片预览 + 清空记录 =====================
with st.sidebar:
    st.subheader("🖼️ 故障图片")
    if uploaded_file is not None:
        st.image(uploaded_file, use_container_width=True)
    
    st.divider()
    if st.button("🗑️ 清空聊天记录", use_container_width=True):
        st.session_state["message"] = []
        st.rerun()
    
    st.divider()
    st.caption("✅ 文字提问 + 图片故障检测")
    st.caption("🤖 多模态 Agent + RAG混合检索")

# ===================== 核心业务逻辑（无修改） =====================
API_CHAT_URL = "http://localhost:8000/api/chat"

if prompt:
    # 渲染用户消息
    st.session_state["message"].append({"role": "user", "content": prompt})
    
    with st.spinner("🔍 多模态智能体思考中..."):
        try:
            data = {"query": prompt}
            files = {}
            if uploaded_file is not None:
                files = {
                    "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
                }
            
            response = requests.post(
                API_CHAT_URL,
                data=data,
                files=files,
                timeout=60
            )
            ai_answer = response.json()["answer"]
        except Exception as e:
            ai_answer = f"服务异常：{str(e)}"

    # 渲染助手消息
    st.session_state["message"].append({"role": "assistant", "content": ai_answer})
    st.rerun()