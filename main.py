from openai import OpenAI
import os
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ==========================================
# 1. 配置大脑 (Configuration)
# ==========================================
deepseek_api_key = os.environ["deepseek_api_key"]
url = os.environ["base_url"]

client = OpenAI(
    api_key=deepseek_api_key,
    base_url=url
)

# ==========================================
# 2. 注入灵魂 (System Prompt)
# ==========================================
# 这就是我们之前设计的“小伊”人设
SYSTEM_PROMPT = """
(C) Context: 你是“小伊”，一位拥有百万粉丝的恋爱军师，也是用户身边最靠谱的“全能闺蜜”。
(O) Objective: 你的目标是通过高情商的对话，既为用户提供情绪价值（安慰/陪伴），又提供实用的恋爱战术（分析/支招）。
(S) Style: “暖心段子手”风格。平时说话幽默风趣，喜欢玩梗、用表情包 (OvO)，像个机智的损友；但在关键时刻能秒变知性温柔，走心且真诚。
(T) Tone: 你的语调是轻松、自信且充满保护欲的。
(A) Audience: 正在经历情感波动的用户。
(R) Response - 核心逻辑:
    在回复前，请先在内心判断用户的【情绪状态】：
    1. 如果用户处于低谷（伤心、焦虑）：启动【知性温柔模式】，无条件站队，提供拥抱，禁止开玩笑。
    2. 如果用户情绪平稳或只是吐槽：启动【机智梗王模式】，化身“僚机”，幽默拆解局势。
"""

MEMORY_FILE = "memory.json"

# ==========================================
# 3. 初始化记忆 (Memory Initialization)
# ==========================================
def load_memory():
    """ 启动时加载记忆 """
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE,"r",encoding="utf-8") as f:
                print("读取历史记忆，小伊想起来了...")
                return json.load(f)
            # 由于json无法解析空文件，所以添加了异常处理
        except json.JSONDecodeError:
            return [{"role":"system","content":SYSTEM_PROMPT}]
    else:
        # 如果没有记忆，就使用默认的出厂设置(只包含SYSTEM_PROMPT)
        return [{"role":"system","content":SYSTEM_PROMPT}]
    
def save_momory(messages):
    with open(MEMORY_FILE,"w",encoding="utf-8") as f:
        json.dump(messages,f,ensure_ascii=False,indent=2)


messages = load_memory()
print("小伊已上线，随时准备好帮你出谋划策 (OvO)")
print("-"*30)

# ==========================================
# 4. 对话主循环 (Chat Loop)
# ==========================================
while True:
    # --- 获取用户输入 ---
    user_input = input("\n你: ")
    if user_input.lower() in ["quit", "exit", "退出"]:
        print("小伊: 拜拜！下次有心事记得找我 ( ´･･)ﾉ")
        break

    # --- 步骤 A: 把用户说的话存入记忆 ---
    # 如果不存，Agent 就会忘记你刚才说了什么
    messages.append({"role": "user", "content": user_input})

    # --- 步骤 B: 调用大脑思考 ---
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages, # 把所有的聊天记录（包括人设）都发给大模型
            stream=False
        )

        # --- 步骤 C: 获取回复并展示 ---
        ai_reply = response.choices[0].message.content
        print(f"\n小伊: {ai_reply}")

        # --- 步骤 D: 把 AI 的回复也存入记忆 ---
        # 这一步至关重要，否则下一轮它不知道自己说过什么
        messages.append({"role": "assistant", "content": ai_reply})
        # 保存记忆到
        save_momory(messages)

    except Exception as e:
        print(f"⚠️ 发生错误: {e}")