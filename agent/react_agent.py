from langchain.agents import create_agent
from model.factory import chat_model
from utils.prompt_loader import load_system_prompts
from agent.tools.agent_tools import (rag_summarize, get_weather, get_user_location, get_user_id,
                                     get_current_month, fetch_external_data, fill_context_for_report,detect_robot_fault)
from agent.tools.middleware import monitor_tool, log_before_model, report_prompt_switch


class ReactAgent:
    def __init__(self):
        self.agent = create_agent(
            model=chat_model,
            system_prompt=load_system_prompts(),
            tools=[rag_summarize, get_weather, get_user_location, get_user_id,
                   get_current_month, fetch_external_data, fill_context_for_report,detect_robot_fault],
            middleware=[monitor_tool, log_before_model, report_prompt_switch],
        )

    # ===================== 核心修改：支持历史消息，实现多轮对话 =====================
    def execute_stream(self, history_messages: list, query: str, image_path: str = None):
        # 保留你原有的图片故障检测逻辑（完全不变）
        if image_path is not None:
            # 调用多模态工具识别故障
            fault_result = detect_robot_fault.invoke(image_path)
            # 把故障结果拼入用户问题，联动RAG检索
            query = f"图片故障识别结果：{fault_result}\n用户问题：{query}"

        # ===================== 新增：拼接完整对话上下文（历史+当前提问） =====================
        input_messages = []
        # 1. 加载前端传递的历史对话消息
        for msg in history_messages:
            input_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        # 2. 追加当前用户最新提问（含图片识别结果）
        input_messages.append({"role": "user", "content": query})

        # 构造Agent输入（完整上下文）
        input_dict = {
            "messages": input_messages
        }

        # 保留你原有的流式输出、context上下文标记（完全不变）
        for chunk in self.agent.stream(input_dict, stream_mode="values", context={"report": False}):
            latest_message = chunk["messages"][-1]
            if latest_message.content:
                yield latest_message.content.strip() + "\n"


if __name__ == '__main__':
    agent = ReactAgent()
    # 修改本地测试调用方式，兼容新参数（传入空历史消息列表）
    for chunk in agent.execute_stream([], "给我生成我的使用报告"):
        print(chunk, end="", flush=True)