# 路径补全
import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from agent.react_agent import ReactAgent

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

# 多模态接口：支持文本+图片
@app.post("/api/chat")
async def chat(
    query: str = Form(...),
    file: UploadFile = File(None)  # 可选图片
):
    image_path = None
    # 保存上传的图片
    if file is not None:
        image_path = f"uploads/{file.filename}"
        with open(image_path, "wb") as f:
            f.write(await file.read())

    try:
        # 调用Agent，传递图片路径
        ai_answer = ""
        for chunk in agent.execute_stream(query, image_path=image_path):
            ai_answer += chunk
        
        # 删除临时压缩图（清理）
        if os.path.exists("compressed_temp.jpg"):
            os.remove("compressed_temp.jpg")
            
        return {"code": 200, "answer": ai_answer.strip()}
    except Exception as e:
        return {"code": 500, "answer": f"服务异常：{str(e)}"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)