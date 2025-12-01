import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# 1. 复制 new_app.py 中的工具定义
def get_horoscope_fortune(sign: str):
    """
    查询指定星座的今日恋爱运势，获取恋爱建议。
    
    Args:
        sign: 星座名称，例如 "白羊座", "处女座", "天蝎座"。
    """
    print(f"--- 🔮 正在调用工具 get_horoscope_fortune, 参数: {sign} ---")
    # 模拟数据
    import random
    luck_level = random.choice(["⭐⭐⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐", "⭐⭐"])
    
    tips = {
        "白羊座": "今天冲动是魔鬼，表白要慎重，建议先从朋友做起！",
        "金牛座": "也许会在转角遇到爱哦，记得穿得好看点！",
        # ... (其他星座省略)
        "双鱼座": "今天适合浪漫的烛光晚餐，氛围感拉满！"
    }
    
    tip = tips.get(sign, "只要心诚，每天都是好日子！")
    return {"sign": sign, "love_luck": luck_level, "strategy": tip}

def calculate_bazi_compatibility(gender1: str, date1: str, gender2: str, date2: str):
    """
    基于八字命理（出生日期）深度分析两人的恋爱/婚姻匹配度。
    """
    print(f"--- ☯️ 正在调用工具 calculate_bazi_compatibility, 参数: {gender1}/{date1} & {gender2}/{date2} ---")
    # 模拟玄学计算
    seed = hash(date1 + date2) % 100
    score = abs(seed)
    if score < 60: score += 30 
    
    if score > 90:
        verdict = "天干地支六合，命中注定的正缘！赶紧领证！"
    elif score > 80:
        verdict = "五行互补，虽然偶尔有小摩擦，但越吵越恩爱。"
    else:
        verdict = "八字略有相冲，相处可能需要更多的智慧和耐心哦。"
        
    return {
        "compatibility_score": score, 
        "elemental_analysis": f"{gender1}方{date1} 与 {gender2}方{date2} 的五行气场分析...",
        "master_comment": verdict
    }

# 2. 配置工具列表
tools_list = [get_horoscope_fortune, calculate_bazi_compatibility]

# 3. 初始化模型
if "gemini_api" in os.environ:
    genai.configure(api_key=os.environ["gemini_api"])
    
    print("正在初始化 Gemini 军师...")
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        tools=tools_list,
        # 加上 system_instruction 确保它知道自己是小伊
        system_instruction="你是小伊，恋爱军师。如果用户问运势或合盘，请使用工具查询，并根据结果给出风趣的建议。" 
    )
    
    # 4. 启动聊天
    chat = model.start_chat(enable_automatic_function_calling=True)
    
    # 5. 测试场景 1: 星座运势
    print("\n>>> 测试场景 1: 询问星座运势")
    user_input_1 = "小伊，我是双鱼座，今天适合去约会吗？"
    print(f"用户: {user_input_1}")
    response1 = chat.send_message(user_input_1)
    print(f"小伊: {response1.text}")
    
    # 6. 测试场景 2: 八字合盘
    print("\n>>> 测试场景 2: 询问八字合盘")
    user_input_2 = "我男朋友是1998年5月20日生的，我是1999年9月9日生的女生，帮我算算我们要不要结婚？"
    print(f"用户: {user_input_2}")
    response2 = chat.send_message(user_input_2)
    print(f"小伊: {response2.text}")

else:
    print("Error: gemini_api not found in env.")
