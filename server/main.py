# 路径补全
import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from fastapi import FastAPI, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from agent.react_agent import ReactAgent
# 导入会话持久化工具（核心新增）
from utils.chat_history import (
    load_all_sessions, create_new_session, delete_session,
    append_session_message, append_session_image
)

app = FastAPI(title="智扫通多模态Agent后端")

# 跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化Agent
agent = ReactAgent()

# 创建临时文件夹存图片
os.makedirs("uploads", exist_ok=True)

# ===================== 新增：会话管理接口 =====================
# 1. 获取所有会话列表
@app.get("/api/session/list")
def get_session_list():
    try:
        sessions = load_all_sessions()
        session_list = []
        for sid, info in sessions.items():
            session_list.append({
                "session_id": sid,
                "session_name": info["session_name"],
                "create_time": info["create_time"]
            })
        session_list.reverse()
        return {"code": 200, "data": session_list}
    except Exception as e:
        return {"code": 500, "msg": str(e)}

# 2. 新建会话
@app.post("/api/session/create")
def api_create_session():
    try:
        new_sid = create_new_session()
        return {"code": 200, "session_id": new_sid}
    except Exception as e:
        return {"code": 500, "msg": str(e)}

# 3. 删除会话
@app.delete("/api/session/delete")
def api_delete_session(session_id: str = Query(...)):
    try:
        delete_session(session_id)
        return {"code": 200, "msg": "删除成功"}
    except Exception as e:
        return {"code": 500, "msg": str(e)}

# ===================== 改造：多模态+会话+多轮对话 核心接口 =====================
@app.post("/api/chat")
async def chat(
    session_id: str = Form(...),       # 新增：会话ID（必传）
    query: str = Form(...),            # 用户提问
    history_msg: str = Form("[]"),     # 新增：历史对话消息
    file: UploadFile = File(None)      # 可选图片
):
    image_path = None
    # 保存上传的图片
    if file is not None:
        image_path = f"uploads/{file.filename}"
        with open(image_path, "wb") as f:
            f.write(await file.read())
        # 图片关联到当前会话
        append_session_image(session_id, image_path)

    try:
        # 解析历史消息
        history_messages = json.loads(history_msg)
        # 调用Agent：传递 历史消息+当前问题+图片路径（适配多轮对话）
        ai_answer = ""
        for chunk in agent.execute_stream(history_messages, query, image_path):
            ai_answer += chunk
        
        # 持久化：保存本轮对话到会话
        append_session_message(session_id, "user", query)
        append_session_message(session_id, "assistant", ai_answer.strip())

        # 删除临时压缩图（原有清理逻辑，保留）
        if os.path.exists("compressed_temp.jpg"):
            os.remove("compressed_temp.jpg")
            
        return {"code": 200, "answer": ai_answer.strip()}
    except Exception as e:
        return {"code": 500, "answer": f"服务异常：{str(e)}"}

if __name__ == "__main__":
    uvicorn.run("main.py", host="0.0.0.0", port=8000, reload=True)