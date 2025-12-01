# 💖 MyLover Xiaoyi - 你的 AI 恋爱军师 (RAG + Bazi Edition)

> "发张照片给我，让我帮你参谋参谋！(OvO)"

**MyLover Xiaoyi** 是一个基于 **Gemini 2.5 Flash** 模型的智能恋爱助手。她不仅拥有知性温柔与机智玩梗并存的双重人格，更装备了 **RAG (检索增强生成)** 记忆系统和 **玄学 (八字/星座)** 工具，致力于成为你身边最靠谱的“全能闺蜜”。

---

## ✨ 核心功能

1.  **🧠 长期记忆 (RAG)**
    *   使用 `ChromaDB` 向量数据库存储对话和背景信息。
    *   小伊能记住你的喜好、前任的故事以及你们之前的聊天内容，让对话更有连贯性和温度。

2.  **🔮 玄学恋爱军师 (Function Calling)**
    *   **八字合盘**: 只要提供具体的出生日期，小伊会调用专业的 `lunar_python` 库进行八字排盘，基于五行生克原理分析你和TA的匹配度。
    *   **星座运势**: 提供每日恋爱运势播报，给你最俏皮的约会建议。
    *   **智能触发**: 只需要自然聊天（如“我是98年5月20日的，跟我女朋友合不合？”），模型会自动判断并调用相应的玄学工具。

3.  **👀 视觉能力**
    *   支持图片上传。你可以发给小伊一张聊天截图或穿搭照片，让她帮你分析局势或提供建议。

4.  **🎭 双重人格引擎**
    *   **机智梗王模式**: 当你情绪平稳时，她是你爱玩梗的损友。
    *   **知性温柔模式**: 当你情绪低落时，她会秒变知心姐姐，提供无条件的情绪支持。

---

## 🛠️ 技术栈

*   **LLM**: Google Gemini 2.5 Flash
*   **Web Framework**: Streamlit
*   **Vector DB**: ChromaDB (配合 `sentence-transformers` 生成 Embeddings)
*   **Tools**:
    *   `lunar_python`: 用于高精度的中国农历和八字计算。
    *   Function Calling: 实现自然语言到工具函数的自动映射。

---

## 🚀 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/mengyangyangs/mylover-xiaoyi.git
cd mylover-xiaoyi
```

### 2. 创建并激活虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
# 注意: 本项目依赖 lunar_python, chromadb, streamlit, google-generativeai 等库
```
*(注: 如果还没有 requirements.txt，请参考代码中的 import 手动安装)*

### 4. 配置环境变量
在项目根目录下创建一个 `.env` 文件，并填入你的 Gemini API Key：
```ini
gemini_api="你的_Gemini_API_Key"
deepseek_api_key="你的_Deepseek_Key" # (可选，仅旧版代码使用)
base_url="你的_API_Base_URL"       # (可选)
```

### 5. 运行应用
```bash
streamlit run new_app.py
```

---

## 📂 文件结构说明

*   **`new_app.py`**: **[主程序]** 包含最新的 Streamlit 界面、RAG 逻辑、Gemini 模型初始化及八字/星座工具定义。
*   `chroma_db/`: 向量数据库的持久化存储目录。
*   `memory.json`: 简单的对话历史记录文件。
*   `test_rag.py`: RAG 功能的独立测试脚本。
*   `test_real_bazi.py`: 八字计算功能的独立测试脚本。
*   `app.py` / `main.py`: 旧版本的程序入口（供参考）。

---

## ⚠️ 注意事项

*   **API Key 安全**: 请确保不要将含有真实 Key 的 `.env` 文件上传到 GitHub。本项目已配置 `.gitignore` 进行保护。
*   **RAG 初始化**: 首次运行时，系统会自动下载 Embedding 模型（`paraphrase-multilingual-MiniLM-L12-v2`），可能会消耗一定时间，请耐心等待。

---

Made with ❤️ by [mengyangyangs](https://github.com/mengyangyangs)
