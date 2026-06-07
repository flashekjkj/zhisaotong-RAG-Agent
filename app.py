import streamlit as st
# 新增：用于请求后端API
import requests

# 页面配置（可选，优化体验）
st.set_page_config(page_title="智扫通机器人智能客服", page_icon="🤖")

# 标题
st.title("智扫通机器人智能客服")
st.divider()

# ===================== 核心修改：删除本地Agent初始化 =====================
# 注释/删除原有Agent代码，不再本地加载智能体
# if "agent" not in st.session_state:
#     st.session_state["agent"] = ReactAgent()
# ==========================================================================

# 初始化会话状态（仅保留消息历史）
if "message" not in st.session_state:
    st.session_state["message"] = []

# 渲染历史对话
for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])

# 用户输入提示词
prompt = st.chat_input()

# 后端API接口地址（固定，与FastAPI对应）
API_CHAT_URL = "http://localhost:8000/api/chat"

if prompt:
    # 展示用户消息
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})

    # 流式生成回答（保留你原有的UI交互）
    with st.chat_message("assistant"):
        with st.spinner("智能客服思考中..."):
            # ===================== 核心修改：调用后端API =====================
            # 发送GET请求到FastAPI后端，获取答案
            try:
                response = requests.get(
                    url=API_CHAT_URL,
                    params={"query": prompt},
                    timeout=30
                )
                # 解析后端返回的JSON数据
                result = response.json()
                ai_answer = result["answer"]
            except Exception as e:
                ai_answer = f"服务异常：{str(e)}\n请检查FastAPI后端是否启动！"
            # =================================================================

            # 保持原有的流式展示效果
            st.write_stream(iter([ai_answer]))

    # 将完整回答存入历史记录
    st.session_state["message"].append({"role": "assistant", "content": ai_answer})