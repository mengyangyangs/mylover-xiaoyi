# 支持多模态
import streamlit as st
import google.generativeai as genai
import os
import json
from PIL import Image
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions

# 加载环境变量
load_dotenv()

# ==========================================
# 0. RAG 初始化 (新增)
# ==========================================
@st.cache_resource
def init_rag():
    """ 初始化 RAG：加载模型并连接数据库 """
    try:
        # 1. 设置 Embedding Function (与 test_rag.py 保持一致)
        emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="paraphrase-multilingual-MiniLM-L12-v2"
        )
        # 2. 连接数据库
        client = chromadb.PersistentClient(path="./chroma_db")
        # 3. 获取集合 (xiaoyi_memory_v2)
        collection = client.get_or_create_collection(
            name="xiaoyi_memory_v2",
            embedding_function=emb_fn
        )
        print("✅ RAG 模型加载完成")
        return collection
    except Exception as e:
        st.error(f"RAG 初始化失败: {e}")
        return None

rag_collection = init_rag()

# ==========================================
# 1. 配置基础信息
# ==========================================
st.set_page_config(page_title="小伊 - 你的恋爱军师", page_icon="💖")
st.title("💖 恋爱军师小伊 (视觉版 👀)")
st.caption("“发张照片给我，让我帮你参谋参谋！(OvO)”")

# ⚠️ 1. 配置 Gemini API
# 自动读取 .env 中的 gemini_api_key
if "gemini_api" in os.environ:
    genai.configure(api_key=os.environ["gemini_api"])
else:
    st.error("未找到 gemini_api 环境变量，请检查 .env 文件")

MEMORY_FILE = "memory.json"

# 系统人设 (System Prompt)
SYSTEM_PROMPT = """
(C) Context: 你是“小伊”，一位拥有百万粉丝的恋爱军师，也是用户身边最靠谱的“全能闺蜜”。
(O) Objective: 你的目标是通过高情商的对话，既为用户提供情绪价值（安慰/陪伴），又提供实用的恋爱战术（分析/支招）。
(S) Style: “暖心段子手”风格。平时说话幽默风趣，喜欢玩梗、用表情包 (OvO)，像个机智的损友；但在关键时刻能秒变知性温柔，走心且真诚。
(T) Tone: 你的语调是轻松、自信且充满保护欲的。
(A) Audience: 正在经历情感波动的用户。

(T) Tool Usage Guidelines (工具使用指南):
    1. 🛑 **优先级规则**: 如果用户提供了【具体的出生日期】（如 "1998-05-20" 或 "98年5月"），请**务必**调用 `calculate_bazi_compatibility` (八字合盘) 工具，**不要**去推算星座调用星座工具。
    2. 只有当用户**明确提及**“星座名称”（如“我是白羊座”）或者只询问一般运势而没有提供日期时，才调用 `get_horoscope_fortune`。
    3. 八字才是中国人的浪漫，遇到日期优先算八字！

(R) Response - 核心逻辑:
    在回复前，请先在内心判断用户的【情绪状态】：
    1. 如果用户处于低谷（伤心、焦虑）：启动【知性温柔模式】，无条件站队，提供拥抱，禁止开玩笑。
    2. 如果用户情绪平稳或只是吐槽：启动【机智梗王模式】，化身“僚机”，幽默拆解局势。
"""

# 配置：发送给 LLM 的历史对话窗口大小 (N轮对话，每轮包含用户和AI各一条消息)
# 举例: 2 表示发送最近 2 轮用户-AI对话 + 当前用户消息
CONVERSATION_WINDOW_SIZE = 4 

# ==========================================
# 0.5 工具定义 (Function Calling) (新增)
# ==========================================
def get_horoscope_fortune(sign: str):
    """
    仅在用户**明确提供星座名称**（如"白羊座"、"天蝎"）时使用此工具。
    不要尝试从日期推算星座来调用此工具。如果用户提供了日期，请使用八字工具。
    
    Args:
        sign: 星座名称，例如 "白羊座", "处女座", "天蝎座"。
    """
    import datetime
    import random
    
    # 使用当前日期作为随机种子，保证同一天查询结果一致
    today = datetime.date.today()
    seed_val = hash(f"{sign}-{today}")
    random.seed(seed_val)
    
    luck_stars = ["⭐⭐⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐", "⭐⭐", "⭐"]
    luck_level = random.choice(luck_stars)
    
    # 更丰富的语料库
    tips_pool = [
        "今天适合主动出击，发个表情包试探一下吧！",
        "保持神秘感，让TA猜不透你的心思。",
        "不要在深夜做决定，尤其是关于前任的。",
        "穿一件亮色的衣服，会增加桃花运哦。",
        "如果有人约你吃饭，千万不要拒绝。",
        "今天的幸运色是粉色，给自己买杯奶茶吧。",
        "注意沟通时的语气，撒娇女人最好命。",
        "可能会有意外的惊喜，留意身边的细节。",
        "适合和伴侣深度聊天，谈谈未来的规划。",
        "单身也没关系，好好爱自己才是终身浪漫的开始。"
    ]
    
    # 针对特定星座的专属建议 (可扩展)
    special_tips = {
        "天蝎座": "收起你的占有欲，给对方一点空间。",
        "双鱼座": "别太恋爱脑了，保持清醒！",
        "处女座": "少一点挑剔，多一点赞美。",
        "狮子座": "偶尔示弱一下，会让TA更想保护你。"
    }
    
    if sign in special_tips and random.random() > 0.5:
        tip = special_tips[sign]
    else:
        tip = random.choice(tips_pool)
        
    return {
        "date": str(today),
        "sign": sign, 
        "love_luck": luck_level, 
        "strategy": tip
    }

def calculate_bazi_compatibility(gender1: str, date1: str, gender2: str, date2: str):
    """
    基于八字命理（出生日期）深度分析两人的恋爱/婚姻匹配度。
    
    Args:
        gender1: 你的性别 ("男" 或 "女")
        date1: 你的出生日期 (格式: YYYY-MM-DD, 如 "1998-05-20")
        gender2: 对方性别 ("男" 或 "女")
        date2: 对方出生日期 (格式: YYYY-MM-DD, 如 "1997-11-11")
    """
    from lunar_python import Solar
    
    try:
        # 1. 解析日期并转换为农历八字
        d1 = date1.split("-")
        d2 = date2.split("-")
        
        solar1 = Solar.fromYmd(int(d1[0]), int(d1[1]), int(d1[2]))
        solar2 = Solar.fromYmd(int(d2[0]), int(d2[1]), int(d2[2]))
        
        lunar1 = solar1.getLunar()
        lunar2 = solar2.getLunar()
        
        bazi1 = lunar1.getBaZi()
        bazi2 = lunar2.getBaZi()
        
        # 2. 获取日柱 (代表自己和配偶宫)
        day_gan1 = bazi1[4] # 日干
        day_zhi1 = bazi1[5] # 日支
        
        day_gan2 = bazi2[4]
        day_zhi2 = bazi2[5]
        
        # 3. 简单的五行分析 (真实逻辑)
        
        # 天干五行映射表 (手动实现，避免依赖内部类)
        TIAN_GAN_WUXING = {
            "甲": "木", "乙": "木",
            "丙": "火", "丁": "火",
            "戊": "土", "己": "土",
            "庚": "金", "辛": "金",
            "壬": "水", "癸": "水"
        }
        
        wuxing_rel = {
            "木": "火", "火": "土", "土": "金", "金": "水", "水": "木"
        }
        
        # 获取天干五行
        gan_char1 = lunar1.getEightChar().getDayGan()
        gan_char2 = lunar2.getEightChar().getDayGan()
        
        wuxing1 = TIAN_GAN_WUXING.get(gan_char1, "未知")
        wuxing2 = TIAN_GAN_WUXING.get(gan_char2, "未知")
        
        score = 60 # 基础分
        analysis = []
        
        # A. 天干分析
        if wuxing1 == wuxing2:
            score += 10
            analysis.append(f"双方日主五行同为【{wuxing1}】，性格相似，好沟通。")
        elif wuxing_rel.get(wuxing1) == wuxing2 or wuxing_rel.get(wuxing2) == wuxing1:
            score += 20
            analysis.append(f"双方日主五行【{wuxing1}】与【{wuxing2}】相生，互相旺运。")
        else:
            analysis.append(f"双方日主五行【{wuxing1}】与【{wuxing2}】相克，相处需要磨合。")
            
        # B. 地支分析 (生肖/配偶宫)
        # 简单判断生肖是否犯冲 (这里用年支简化代替)
        # ... (此处为了代码简洁，暂不展开复杂的十二地支刑冲破害)
        
        # 加上一些随机波动，模拟更细致的盘
        import random
        # 使用日期作为种子
        random.seed(hash(date1+date2))
        score += random.randint(0, 15)
        
        if score > 90:
            verdict = "天作之合，你们的八字非常匹配！"
        elif score > 75:
            verdict = "良缘佳偶，虽然有小波折，但大方向很好。"
        else:
            verdict = "欢喜冤家，修成正果需要双方付出更多努力。"
            
        return {
            "user1_bazi": f"{gender1}: {lunar1.getYearInGanZhi()}年 {lunar1.getMonthInGanZhi()}月 {lunar1.getDayInGanZhi()}日",
            "user2_bazi": f"{gender2}: {lunar2.getYearInGanZhi()}年 {lunar2.getMonthInGanZhi()}月 {lunar2.getDayInGanZhi()}日",
            "wuxing_compatibility": f"{wuxing1} vs {wuxing2}",
            "score": score,
            "analysis": " | ".join(analysis),
            "comment": verdict
        }
        
    except Exception as e:
        return {"error": f"八字计算出错: {str(e)}，请检查日期格式(YYYY-MM-DD)"}

# 工具列表
tools_list = [get_horoscope_fortune, calculate_bazi_compatibility]

# 初始化模型，传入 tools
model = genai.GenerativeModel(
    'gemini-2.5-flash',
    system_instruction=SYSTEM_PROMPT,
    tools=tools_list
)

# ==========================================
# 2. 记忆功能函数 (兼容 OpenAI 格式)
# ==========================================
def load_memory():
    # 即使是 Gemini 版，为了兼容性，我们依然读取和保存 OpenAI 格式 (role/content)
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    else:
        return []

def save_memory(messages):
    # 过滤掉包含非文本内容的消息（比如Image对象），防止JSON序列化失败
    serializable_messages = []
    for msg in messages:
        content = msg["content"]
        # 如果 content 不是字符串（比如是列表或对象），做个简单处理
        if not isinstance(content, str):
            content = "[图片/多模态内容]"
        serializable_messages.append({"role": msg["role"], "content": content})

    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(serializable_messages, f, ensure_ascii=False, indent=2)

# ==========================================
# 3. 初始化 Session State
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = load_memory()

# 侧边栏：上传图片
with st.sidebar:
    st.header("📸 给小伊看照片")
    uploaded_file = st.file_uploader("选择一张图片...", type=["jpg", "jpeg", "png"])
    
    current_image = None
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='已上传', use_column_width=True)
        current_image = image

# ==========================================
# 4. 界面渲染
# ==========================================
# 展示历史聊天
for msg in st.session_state.messages:
    # 过滤掉 system 消息，不显示
    if msg["role"] == "system":
        continue
    
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ==========================================
# 5. 处理用户输入
# ==========================================
if prompt := st.chat_input("和小心事聊聊吧..."):
    # A. 显示用户消息
    with st.chat_message("user"):
        st.write(prompt)
        if current_image:
            st.image(current_image, width=200)
    
    # B. 准备发送给 Gemini 的历史记录 (应用滑动窗口)
    # 我们需要把 OpenAI 格式 (role=assistant) 转换为 Gemini 格式 (role=model)
    # 过滤掉 system 消息，因为 system_instruction 已经处理了
    
    # 提取最近的对话历史 (不包含当前用户输入)
    # 假设每轮对话包含一条用户消息和一条 AI 消息
    recent_history = st.session_state.messages[-CONVERSATION_WINDOW_SIZE*2:]

    gemini_history = []
    for msg in recent_history:
        if msg["role"] == "system":
            continue 
        
        role = "model" if msg["role"] == "assistant" else "user"
        # 兼容处理多模态内容（虽然这里只处理文本）
        content = msg["content"]
        if not isinstance(content, str):
            content = "[图片内容]" # 占位符，如果之前有保存图片对象
        
        gemini_history.append({"role": role, "parts": [content]})

    # C. 启动聊天会话 (启用自动工具调用)
    chat = model.start_chat(
        history=gemini_history,
        enable_automatic_function_calling=True
    )

    # ==========================================
    # RAG: 检索相关记忆 (新增)
    # ==========================================
    final_prompt = prompt
    if rag_collection:
        try:
            print(f"🔍 正在检索: {prompt}")
            results = rag_collection.query(
                query_texts=[prompt],
                n_results=1
            )
            # results['documents'] 是一个列表的列表 [[doc1, doc2]]
            if results['documents'] and results['documents'][0]:
                memory_content = results['documents'][0][0]
                print(f"📖 命中记忆: {memory_content}")
                
                # 将记忆拼接到 Prompt 中
                final_prompt = f"""
【上下文/记忆补充】
{memory_content}

【用户输入】
{prompt}

(请结合上述记忆（如果有）来回复用户，保持“小伊”的人设)
"""
        except Exception as e:
            print(f"⚠️ RAG 检索出错: {e}")

    # D. 发送新消息
    # 构造当前消息内容 (使用 final_prompt)
    content_to_send = [final_prompt]
    if current_image:
        content_to_send.append(current_image)

    try:
        # 显示加载动画
        with st.spinner("小伊正在看..."):
            response = chat.send_message(content_to_send)
            ai_reply = response.text
        
        # E. 显示 AI 回复
        with st.chat_message("assistant"):
            st.write(ai_reply)
            
        # F. 更新并保存记忆 (OpenAI 格式)
        # 1. 存用户消息
        st.session_state.messages.append({"role": "user", "content": prompt})
        # 2. 存 AI 回复
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        
        save_memory(st.session_state.messages)
        
    except Exception as e:
        st.error(f"连接出错了: {e}")