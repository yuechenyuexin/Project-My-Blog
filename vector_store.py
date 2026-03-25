import os
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

# ====================== 配置项 ======================
# 模型名称（选轻量级的all-MiniLM-L6-v2，速度快、效果够用）
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
# Chroma持久化存储路径（项目根目录下的chroma_db文件夹）
CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
# 向量集合名称（相当于数据库的表，专门存储博客文章的向量）
CHROMA_COLLECTION_NAME = "blog_articles"

# ====================== 全局变量 ======================
# 加载Embedding模型（首次运行会自动下载，后续复用）
# 这个模型的作用：把 文字 → 数字向量
# embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

# 初始化Chroma客户端（持久化存储）
# PersistentClient = 持久化客户端：向量数据会保存到电脑里，重启项目不会丢
chroma_client = chromadb.PersistentClient(
    path=CHROMA_PERSIST_DIR,
    settings=Settings(
        anonymized_telemetry=False,  # 关闭匿名统计
        allow_reset=True  # 允许重置集合（测试用）
    )
)

# 创建/获取文章向量集合（指定自定义Embedding函数）  如果集合不存在就创建，存在就直接用
article_collection = chroma_client.get_or_create_collection(
    name=CHROMA_COLLECTION_NAME,    # 集合名：blog_articles
    embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL_NAME     # 指定用刚才的AI模型转向量
    ),
    metadata={"hnsw:space": "cosine"}  # 余弦相似度（语义搜索常用）
)

# ====================== 核心函数 ======================
def get_article_text(article: Dict) -> str:
    """
    拼接文章标题+描述+内容，生成用于向量转换的文本
    """
    # 修复：内外引号统一（外单内单/外双内单），简化拼接无冗余
    title = article.get('title', '').strip()  # strip()去首尾空格，避免空字符
    desc = article.get('description', '').strip()
    content = article.get('content', '').strip()
    # 拼接：用|分隔，过滤空字段（避免多个|连在一起，影响模型）
    text_parts = [part for part in [title, desc, content] if part]
    return " | ".join(text_parts)


def add_article_to_vector_db(article: Dict):
    """
    将单篇文章存入向量库
    :param article: 文章字典（需包含id、title、content、category_id、author_id等字段）
    """
    # 1. 生成向量文本
    text = get_article_text(article)
    # 2. 构造向量库的ID（必须是字符串）
    article_id = str(article["id"])     # Chroma的向量库的 `ids` 强制要求字符串
    # 3. 构造元数据（方便后续筛选，比如按分类/作者过滤）
    metadata = {
        "article_id": article_id,   # title 是文章必填字段！数据库里每篇文章都一定有，所以用 []，不怕报错
        "title": article["title"],  # category_id / author_id 是可选字段！可能为空，所以用 get()，避免程序崩了
        "category_id": str(article.get("category_id")) if article.get("category_id") else None,
        "author_id":  str(article.get("author_id")) if article.get("author_id") else None,
        "author_name": article.get("author")        # 这里的
    }
    # 4. 存入向量库（先删除旧的，避免重复）
    article_collection.delete(ids=[article_id])
    article_collection.add(
        ids=[article_id],
        documents=[text],
        metadatas=[metadata]    # 附加信息
    )

def delete_article_from_vector_db(article_id: int):
    """
    从向量库删除指定文章
    :param article_id: 文章ID
    """
    article_collection.delete(ids=[str(article_id)])
    # 同步清理向量垃圾，和 MySQL 保持一致。


def search_similar_articles(
    query: str,
    top_k: int = 10,
    category_id: Optional[int] = None   # 可选：按分类筛选
) -> List[Dict]:
    """
    语义搜索相似文章
    :param query: 搜索关键词
    :param top_k: 返回最相似的前N篇
    :param category_id: 可选，按分类筛选
    :return: 相似文章列表（包含article_id、score、metadata）
    """
    # 1. 构造筛选条件（可选按分类）
    where = None
    # where 是一个「筛选条件变量」，None 表示「空、什么都没有、不设置任何条件」
    # 一开始，我不设置任何筛选条件，默认查询向量库里的【所有文章】
    if category_id:
        where = {"category_id": str(category_id)}  # Chroma的metadata筛选值需为字符串

    # 2. 语义搜索
    results = article_collection.query(
        query_texts=[query],
        n_results=top_k,
        where=where,
        include=["metadatas", "distances"]  # 返回元数据和相似度距离（越小越相似） metadatas前面定义了
    )   # include = 定制搜索返回的内容 去除无用的其他信息  这里include的[]就是导致了下面for需要的[0]的去掉外层的[]的原因

    # 3. 格式化结果（转换为易读的结构 转换成前端能看懂的格式）
    similar_articles = []
    for idx, metadata in enumerate(results["metadatas"][0]):
        # 相似度分数：distance是余弦距离（0-2），转换为相似度（1 - distance/2），范围0-1
        distance = results["distances"][0][idx]
        similarity = round(1 - (distance / 2), 4)

        # 安全转换category_id，避免int(None)报错
        cate_id = metadata.get("category_id")
        category_id_int = int(cate_id) if cate_id else None

        similar_articles.append({
            "article_id": int(metadata["article_id"]),
            "title": metadata["title"],
            "category_id": category_id_int,
            "similarity": similarity,  # 相似度（越高越匹配）
            "distance": round(distance, 4)  # 原始距离（仅供参考）
        })
    return similar_articles

def reset_vector_db():
    """重置向量库（测试用，谨慎使用）"""
    chroma_client.delete_collection(CHROMA_COLLECTION_NAME)
    global article_collection
    article_collection = chroma_client.get_or_create_collection(
        name=CHROMA_COLLECTION_NAME,
        embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL_NAME
        ),
        metadata={"hnsw:space": "cosine"}  # 余弦相似度（语义搜索常用）
    )
    print("向量库已重置！")