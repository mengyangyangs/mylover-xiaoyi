# 不支持多模态
import streamlit as st
from openai import OpenAI
import os
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ==========================================
# 1. 配置基础信息
# ==========================================
st.set_page_config(page_title="小伊 - 恋爱军师",page_icon="❤️")
st.title("小伊 - 你的恋爱军师 ❤️")
st.caption("难过时给肩膀，快乐时跟你分享～")

api_key = os.environ["deepseek_api_key"]
url = os.environ["base_url"]

client = OpenAI(
    api_key=api_key,
    base_url=url
)

MEMORY_FILE = "memory.json"

# 系统人设 (保持不变)
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

# ==========================================
# 2. 记忆功能函数
# ==========================================
def load_memory():
    """ 启动时加载记忆 """
    if os.path.exists(MEMORY_FILE):
        try:    
            with open(MEMORY_FILE,"r",encoding="utf-8") as f:
                print("小伊记起来啦！")
                return json.load(f)
        except json.JSONDecodeError:
            return [{"role":"system","content":SYSTEM_PROMPT}]
    else:
        return [{"role":"system","content":SYSTEM_PROMPT}]
    
def save_memory(messages):
    """ 保存记忆到JSON文件 """
    with open(MEMORY_FILE,"w",encoding="utf-8") as f:
        print("记忆保存中...")
        json.dump(messages,f,ensure_ascii=False,indent=2)

# ==========================================
# 3. 初始化 Session State (Streamlit 的短期记忆)
# ==========================================
if "messages" not in st.session_state:
    # 启动时，先从文件加载长期记忆
    st.session_state.messages = load_memory()

# ==========================================
# 4. 界面渲染
# ==========================================
# 展示历史聊天记录 (跳过第一条 System Prompt)
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# ==========================================
# 5. 处理用户输入
# ==========================================
if prompt := st.chat_input("和小心事聊聊吧..."):
    # A.显示用户信息
    with st.chat_message("user"):
        st.write(prompt)

    # B.加入内存
    st.session_state.messages.append({"role":"user","content":prompt})

    # C.调用大脑
    try:
        # # 旧代码：非流式调用
        # response = cilent.chat.completions.create(
        #     model = "deepseek-chat",
        #     messages = st.session_state.messages,
        #     stream = False
        # )
        # ai_reply = response.choices[0].message.content

        # # D.显示AI回复 (旧)
        # with st.chat_message("assistant"):
        #     st.write(ai_reply)
        
        # # E.保存回复并写入硬盘 (旧)
        # st.session_state.messages.append({"role":"assistant","content":ai_reply})
        # save_memory(st.session_state.messages)

        # 新代码：流式调用
        full_response = ""
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            for chunk in client.chat.completions.create(
                model="deepseek-chat",
                messages=st.session_state.messages,
                stream=True,
            ):
                full_response += (chunk.choices[0].delta.content or "")
                message_placeholder.markdown(full_response + "▌") # 使用 | 作为光标

            message_placeholder.markdown(full_response) # 显示最终完整回复
        
        ai_reply = full_response
        st.session_state.messages.append({"role":"assistant","content":ai_reply})
        save_memory(st.session_state.messages)

    except Exception as e:
        st.error(f"连接出错:{e}")