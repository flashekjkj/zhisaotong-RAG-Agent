import streamlit as st
from agent.react_agent import ReactAgent

# 页面配置（可选，优化体验）
st.set_page_config(page_title="智扫通机器人智能客服", page_icon="🤖")

# 标题
st.title("智扫通机器人智能客服")
st.divider()

# 初始化会话状态
if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()

if "message" not in st.session_state:
    st.session_state["message"] = []

# 渲染历史对话
for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])

# 用户输入提示词
prompt = st.chat_input()

if prompt:
    # 展示用户消息
    st.chat_message("user").write(prompt)
    st.session_state["message"].append({"role": "user", "content": prompt})

    # 流式生成回答（官方标准写法，无前端BUG）
    with st.chat_message("assistant"):
        with st.spinner("智能客服思考中..."):
            # 直接调用原生流式输出，去掉手动打字和rerun
            res_stream = st.session_state["agent"].execute_stream(prompt)
            # 原生write_stream，无任何自定义封装
            response = st.write_stream(res_stream)

    # 将完整回答存入历史记录
    st.session_state["message"].append({"role": "assistant", "content": response})