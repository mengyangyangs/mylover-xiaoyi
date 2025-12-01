import google.generativeai as genai
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# 1. 配置 API Key (⚠️ 记得替换为你自己的 Gemini Key)
os.environ["GOOGLE_API_KEY"] = os.environ["gemini_api"]
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# 2. 选择支持视觉的模型
# 'gemini-1.5-flash' 是一个速度快且支持多模态的模型
model = genai.GenerativeModel('gemini-2.5-flash')

# 3. 准备图像数据
image_path = "test_image.jpg"
if not os.path.exists(image_path):
    print(f"❌ 错误：找不到图片文件 {image_path}，请确认文件位置。")
    exit()

# 读取图片文件
# Gemini 的库可以直接处理读取好的二进制数据
image_data = {
    'mime_type': 'image/jpeg', # 或者 'image/png'
    'data': Path(image_path).read_bytes()
}

# 4. 发送请求（文本 + 图片）
prompt = "请仔细看看这张图片，然后用那种'暖心段子手'的语气，告诉我你看到了什么？"

print(f"正在让 Gemini 看图片：{image_path} ...")

try:
    # generate_content 可以接收一个列表，里面混合放文本和图片数据
    response = model.generate_content([prompt, image_data])
    
    print("\n--- Gemini 的视觉反馈 ---")
    print(response.text)
    print("-----------------------")

except Exception as e:
    print(f"⚠️ 发生错误: {e}")