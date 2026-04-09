from sentence_transformers import SentenceTransformer
from py2neo import Graph

# 连接 Neo4j（修改密码）
graph = Graph("bolt://localhost:7687", auth=("neo4j", "dzy3fczUC2i"))

# 加载多语言模型（支持中文）
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 查询所有纹样节点
result = graph.run("MATCH (m:Motif) RETURN m.id as id, m.name as name, m.meaning as meaning").data()

for item in result:
    # 组合文本：名称 + 寓意
    text = f"{item['name']} {item['meaning']}".strip()
    if not text:
        continue
    # 生成向量（384维）
    vector = model.encode(text).tolist()
    # 存储到节点属性
    graph.run("""
        MATCH (m:Motif {id: $id})
        SET m.embedding = $vector
    """, id=item['id'], vector=vector)
    print(f"已处理：{item['name']}")

print("向量生成完成")