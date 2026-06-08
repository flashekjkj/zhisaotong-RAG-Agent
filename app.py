import streamlit as st
import requests
import json

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

# ===================== 全局接口地址 =====================
BASE_URL = "http://localhost:8000"
API_CHAT = f"{BASE_URL}/api/chat"
API_SESSION_LIST = f"{BASE_URL}/api/session/list"
API_SESSION_CREATE = f"{BASE_URL}/api/session/create"
API_SESSION_DELETE = f"{BASE_URL}/api/session/delete"

# ===================== 会话状态初始化 =====================
if "current_session_id" not in st.session_state:
    st.session_state["current_session_id"] = ""
if "session_list" not in st.session_state:
    st.session_state["session_list"] = []
if "message" not in st.session_state:
    st.session_state["message"] = []

# 标题
st.markdown('<h1 class="main-title">🤖 智扫通机器人智能客服</h1>', unsafe_allow_html=True)
st.divider()

# ===================== 工具函数 =====================
def refresh_session_list():
    """刷新会话列表"""
    try:
        resp = requests.get(API_SESSION_LIST, timeout=10)
        res = resp.json()
        if res["code"] == 200:
            st.session_state["session_list"] = res["data"]
    except Exception:
        st.warning("会话加载失败，请检查后端")

def switch_session(session_id: str):
    """切换会话，加载历史消息"""
    st.session_state["current_session_id"] = session_id
    # 从本地持久化加载历史消息
    from utils.chat_history import get_session_messages
    st.session_state["message"] = get_session_messages(session_id)
    st.rerun()

# ===================== 聊天内容展示区域 =====================
st.markdown('<div class="main-container">', unsafe_allow_html=True)
# 无会话提示
if not st.session_state["current_session_id"]:
    st.info("👈 请在左侧新建/选择会话后开始对话")
else:
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
col1, col2, col3 = st.columns([8, 1.5, 0.5])
with col1:
    prompt = st.chat_input("请输入问题...")
with col2:
    uploaded_file = st.file_uploader(
        "上传图片",
        type=["png", "jpg", "jpeg"],
        key="file-uploader",
        label_visibility="collapsed"
    )
with col3:
    st.write("")
st.markdown('</div>', unsafe_allow_html=True)

# ===================== 侧边栏：会话管理 + 图片预览 =====================
with st.sidebar:
    st.subheader("📁 会话管理")
    # 新建会话
    if st.button("➕ 新建会话", use_container_width=True):
        try:
            resp = requests.post(API_SESSION_CREATE, timeout=10)
            res = resp.json()
            if res["code"] == 200:
                new_sid = res["session_id"]
                refresh_session_list()
                switch_session(new_sid)
                st.success("新会话创建成功")
        except Exception:
            st.error("创建会话失败")

    st.divider()
    st.subheader("历史会话")
    # 加载会话列表
    if not st.session_state["session_list"]:
        refresh_session_list()
    
    # 渲染会话列表
    for sess in st.session_state["session_list"]:
        sid = sess["session_id"]
        sname = sess["session_name"]
        is_active = sid == st.session_state["current_session_id"]
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(sname, key=f"btn_{sid}", use_container_width=True, type="primary" if is_active else "secondary"):
                switch_session(sid)
        with col2:
            if st.button("🗑️", key=f"del_{sid}"):
                requests.delete(API_SESSION_DELETE, params={"session_id": sid})
                refresh_session_list()
                if st.session_state["session_list"]:
                    switch_session(st.session_state["session_list"][0]["session_id"])
                else:
                    st.session_state["message"] = []
                    st.session_state["current_session_id"] = ""
                st.rerun()

    st.divider()
    st.subheader("🖼️ 故障图片预览")
    if uploaded_file is not None:
        st.image(uploaded_file, use_container_width=True)

    st.divider()
    st.caption("✅ 文字提问 + 图片故障检测")
    st.caption("✅ 多会话管理 + 持久化")
    st.caption("✅ 多轮上下文追问")
    st.caption("🤖 多模态 Agent + RAG混合检索")

# ===================== 核心对话逻辑（支持会话+多轮+多模态） =====================
if prompt and st.session_state["current_session_id"]:
    # 追加用户消息
    st.session_state["message"].append({"role": "user", "content": prompt})
    
    with st.spinner("thinking..."):
        try:
            # 构造请求参数：会话ID + 历史消息 + 当前问题
            data = {
                "session_id": st.session_state["current_session_id"],
                "query": prompt,
                "history_msg": json.dumps(st.session_state["message"], ensure_ascii=False)
            }
            files = {}
            if uploaded_file is not None:
                files = {
                    "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
                }
            
            response = requests.post(
                API_CHAT,
                data=data,
                files=files,
                timeout=60
            )
            ai_answer = response.json()["answer"]
        except Exception as e:
            ai_answer = f"服务异常：{str(e)}"

    # 追加AI回答
    st.session_state["message"].append({"role": "assistant", "content": ai_answer})
    st.rerun()