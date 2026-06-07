# ========== 1. 补全项目路径（必须放第一行，解决模块找不到） ==========
import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
# =================================================================

# ========== 2. 导入依赖 ==========
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 导入你原生的 Agent（严格匹配你的代码）
from agent.react_agent import ReactAgent

# ========== 3. 初始化 FastAPI 应用 ==========
app = FastAPI(title="智扫通Agent后端", version="2.0")

# 解决跨域（前端必用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== 4. 初始化 原生ReactAgent（加载所有工具！） ==========
# 直接实例化你写的智能体，自动加载：天气/定位/报告/RAG工具
agent = ReactAgent()

# ========== 5. 核心接口：Agent 对话入口 ==========
@app.get("/api/chat")
def chat(query: str):
    try:
        # 调用你原生的 agent.execute_stream 流式方法
        # 拼接所有流式输出，返回完整答案
        ai_answer = ""
        for chunk in agent.execute_stream(query):
            ai_answer += chunk

        return {
            "code": 200,
            "query": query,
            "answer": ai_answer.strip(),
            "status": "success"
        }
    except Exception as e:
        return {
            "code": 500,
            "answer": f"Agent服务异常：{str(e)}",
            "status": "error"
        }

# ========== 6. 启动服务 ==========
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)