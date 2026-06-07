import os
import requests
import base64
from PIL import Image  # 用于图片压缩

# ===================== 配置项 =====================
ENV_API_KEY_NAME = "DASHSCOPE_API_KEY"
TEST_IMAGE_PATH = "image.png"  # 你的测试图片
MODEL_NAME = "qwen-vl-plus"        # 官方正确模型
# ==================================================

def get_api_key() -> str:
    api_key = os.getenv(ENV_API_KEY_NAME)
    if not api_key:
        raise ValueError(f"❌ 环境变量 {ENV_API_KEY_NAME} 未配置！")
    return api_key

def compress_image(image_path: str, max_size=(1280, 1280), quality=85) -> str:
    """
    自动压缩图片：降低分辨率+质量，适配多模态API大小限制
    返回压缩后的临时图片路径
    """
    img = Image.open(image_path)
    # 等比例缩放
    img.thumbnail(max_size)
    # 保存为临时压缩图片
    compressed_path = "compressed_temp.jpg"
    # 转换为RGB（避免PNG透明通道报错）
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.save(compressed_path, "JPEG", quality=quality, optimize=True)
    return compressed_path

def image_to_base64(image_path: str) -> str:
    """图片转base64"""
    # 先压缩图片！核心修复
    compressed_path = compress_image(image_path)
    with open(compressed_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def qwen_vl_image_detect(image_path: str) -> str:
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
    headers = {
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type": "application/json"
    }

    img_base64 = image_to_base64(image_path)

    prompt = "你是专业的扫地机器人维修工程师，请分析图片中机器人的故障，简单回答（只回答机器人的故障即可）"

    data = {
        "model": MODEL_NAME,
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image", "image": f"data:image/jpeg;base64,{img_base64}"}
                    ]
                }
            ]
        }
    }

    try:
        res = requests.post(url, headers=headers, json=data, timeout=30)
        result = res.json()
        
        if result.get("output") and result["output"]["choices"]:
            return result["output"]["choices"][0]["message"]["content"][0]["text"]
        else:
            return f"识别失败：{result}"

    except Exception as e:
        return f"请求失败：{str(e)}"

if __name__ == "__main__":
    print("===== 多模态模型测试=====")
    try:
        print(f"✅ 成功读取环境变量：{ENV_API_KEY_NAME}")
        result = qwen_vl_image_detect(TEST_IMAGE_PATH)
        print("\n🎉 识别结果：")
        print(result)
    except Exception as e:
        print(f"\n❌ 测试失败：{str(e)}")