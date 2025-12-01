import chromadb
from chromadb.utils import embedding_functions # 导入 embedding_functions

# 1. 设置 Embedding Function (使用支持中文的本地模型)
# 使用 sentence-transformers 的多语言模型
# 这个模型会自动下载到本地，支持中文语义匹配
emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="paraphrase-multilingual-MiniLM-L12-v2"
)

# 2. 连接数据库
client = chromadb.PersistentClient(path="./chroma_db")

# 3. 创建集合
# ⚠️ 注意：我们换了个新名字 "xiaoyi_memory_v2"，因为不同模型的向量维度不一样，
# 不能混用在同一个集合里。
collection = client.get_or_create_collection(
    name="xiaoyi_memory_v2",
    embedding_function=emb_fn
)

# 4. 存入记忆
print("正在用 Gemini 大脑存入记忆...")
collection.add(
    documents=[
        "小伊最喜欢的食物是麻辣火锅，特别是毛肚。",
        "小伊讨厌下雨天，因为会弄湿鞋子。",
        "小伊的口头禅是'本军师掐指一算'。"
    ],
    ids=["food", "weather", "catchphrase"]
)

# 5. 检索记忆
question = "小伊爱吃啥？"
print(f"🤔 提问: {question}")

results = collection.query(
    query_texts=[question],
    n_results=1
)

print("-" * 30)
print("📚 检索到的记忆:")
print(results['documents'][0])