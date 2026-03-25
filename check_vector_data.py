from vector_store import article_collection

# 打印向量库里所有数据
print("="*50)
print("向量库总文章数：", article_collection.count())
print("="*50)

# 获取所有文章
all_data = article_collection.get(include=["documents", "metadatas"])

for i in range(len(all_data["ids"])):
    art_id = all_data["ids"][i]
    title = all_data["metadatas"][i]["title"]
    text = all_data["documents"][i][:100]  # 打印前100字
    print(f"ID: {art_id} | 标题: {title}")
    print(f"文本: {text}...")
    print("-"*50)