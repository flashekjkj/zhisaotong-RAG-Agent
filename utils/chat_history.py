import json
import os
import uuid
from datetime import datetime

# 会话数据存储路径（项目根目录）
SESSION_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chat_sessions.json")

# 初始化JSON文件（不存在则创建空文件）
def init_session_file():
    if not os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)

# 读取所有会话数据
def load_all_sessions() -> dict:
    init_session_file()
    with open(SESSION_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# 保存所有会话数据到JSON
def save_all_sessions(sessions: dict):
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)

# 新建会话：生成UUID会话ID，返回session_id
def create_new_session() -> str:
    sessions = load_all_sessions()
    session_id = str(uuid.uuid4())
    # 单条会话结构：会话名、创建时间、对话消息、关联图片路径
    sessions[session_id] = {
        "session_name": f"会话{datetime.now().strftime('%m-%d %H:%M')}",
        "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "messages": [],  # 对话历史：[{"role":"user/assistant", "content":"xxx"}]
        "image_paths": []  # 该会话上传的图片路径
    }
    save_all_sessions(sessions)
    return session_id

# 删除指定会话
def delete_session(session_id: str):
    sessions = load_all_sessions()
    if session_id in sessions:
        del sessions[session_id]
        save_all_sessions(sessions)

# 获取单个会话的历史消息
def get_session_messages(session_id: str) -> list:
    sessions = load_all_sessions()
    return sessions.get(session_id, {}).get("messages", [])

# 追加单条消息到指定会话（多轮对话核心）
def append_session_message(session_id: str, role: str, content: str):
    sessions = load_all_sessions()
    if session_id not in sessions:
        return
    sessions[session_id]["messages"].append({
        "role": role,
        "content": content
    })
    save_all_sessions(sessions)

# 为会话追加图片路径
def append_session_image(session_id: str, image_path: str):
    sessions = load_all_sessions()
    if session_id not in sessions:
        return
    if image_path not in sessions[session_id]["image_paths"]:
        sessions[session_id]["image_paths"].append(image_path)
    save_all_sessions(sessions)