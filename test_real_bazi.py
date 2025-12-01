import google.generativeai as genai
import os
from dotenv import load_dotenv
from lunar_python import Solar
import datetime
import random

load_dotenv()

# --- 复制 new_app.py 中最新的工具函数进行测试 ---

def get_horoscope_fortune(sign: str):
    today = datetime.date.today()
    seed_val = hash(f"{sign}-{today}")
    random.seed(seed_val)
    
    luck_stars = ["⭐⭐⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐", "⭐⭐", "⭐"]
    luck_level = random.choice(luck_stars)
    
    # 简化版测试用
    tips_pool = ["今天运势测试A", "今天运势测试B", "今天运势测试C"]
    tip = random.choice(tips_pool)
        
    return {
        "date": str(today),
        "sign": sign, 
        "love_luck": luck_level, 
        "strategy": tip
    }

def calculate_bazi_compatibility(gender1: str, date1: str, gender2: str, date2: str):
    print(f"Calculating bazi for {date1} and {date2}...")
    from lunar_python import Solar
    try:
        d1 = date1.split("-")
        d2 = date2.split("-")
        solar1 = Solar.fromYmd(int(d1[0]), int(d1[1]), int(d1[2]))
        solar2 = Solar.fromYmd(int(d2[0]), int(d2[1]), int(d2[2]))
        lunar1 = solar1.getLunar()
        lunar2 = solar2.getLunar()
        
        TIAN_GAN_WUXING = {
            "甲": "木", "乙": "木", "丙": "火", "丁": "火",
            "戊": "土", "己": "土", "庚": "金", "辛": "金",
            "壬": "水", "癸": "水"
        }
        
        gan1 = lunar1.getEightChar().getDayGan()
        gan2 = lunar2.getEightChar().getDayGan()
        
        wuxing1 = TIAN_GAN_WUXING.get(gan1, "?")
        wuxing2 = TIAN_GAN_WUXING.get(gan2, "?")
        
        return {
            "user1": f"{lunar1.getYearInGanZhi()}年 ({wuxing1}命)",
            "user2": f"{lunar2.getYearInGanZhi()}年 ({wuxing2}命)",
            "wuxing_check": f"{wuxing1} vs {wuxing2}",
            "status": "success"
        }
    except Exception as e:
        return {"error": str(e)}

# --- 开始测试 ---

# 1. 测试八字计算库是否安装成功
print(">>> 1. Testing local Bazi calculation...")
result = calculate_bazi_compatibility("男", "1990-01-01", "女", "1992-02-02")
print(f"Bazi Result: {result}")

# 2. 测试 Gemini 调用 (如果 Key 存在)
if "gemini_api" in os.environ:
    print("\n>>> 2. Testing Gemini Function Calling with Real Bazi Tool...")
    genai.configure(api_key=os.environ["gemini_api"])
    
    tools_list = [calculate_bazi_compatibility]
    model = genai.GenerativeModel('gemini-2.5-flash', tools=tools_list)
    chat = model.start_chat(enable_automatic_function_calling=True)
    
    prompt = "我(男)是1998-05-20出生的，我女朋友是1999-09-09出生的，帮我算算八字合不合？"
    print(f"User Prompt: {prompt}")
    response = chat.send_message(prompt)
    print(f"Gemini Response: {response.text}")
else:
    print("Skipping Gemini test (no API key)")
