import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# 1. 定义工具函数
def get_current_weather(city: str):
    """
    获取指定城市的当前天气情况。
    
    Args:
        city: 城市名称，例如 "北京", "上海", "New York"。
    """
    print(f"--- 正在调用工具 get_current_weather, 参数: {city} ---")
    # 模拟返回数据
    if "北京" in city:
        return {"weather": "晴朗", "temperature": 25, "tips": "适合约会"}
    elif "上海" in city:
        return {"weather": "小雨", "temperature": 20, "tips": "记得带伞"}
    else:
        return {"weather": "多云", "temperature": 22, "tips": "天气不错"}

def love_compatibility_calculator(name1: str, name2: str):
    """
    计算两个人的恋爱契合度。
    
    Args:
        name1: 第一个人的名字。
        name2: 第二个人的名字。
    """
    print(f"--- 正在调用工具 love_compatibility_calculator, 参数: {name1}, {name2} ---")
    return {"compatibility": "98%", "comment": "天作之合！"}

# 2. 配置工具列表
tools_list = [get_current_weather, love_compatibility_calculator]

# 3. 初始化模型
if "gemini_api" in os.environ:
    genai.configure(api_key=os.environ["gemini_api"])
    
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        tools=tools_list
    )
    
    # 4. 启动聊天 (启用自动函数调用)
    chat = model.start_chat(enable_automatic_function_calling=True)
    
    # 5. 测试调用
    print("用户: 北京今天天气怎么样？")
    response1 = chat.send_message("北京今天天气怎么样？")
    print(f"小伊: {response1.text}")
    
    print("\n用户: 我(小明)和校花(小红)合适吗？")
    response2 = chat.send_message("帮我算算小明和小红的恋爱契合度")
    print(f"小伊: {response2.text}")

else:
    print("Error: gemini_api not found in env.")
