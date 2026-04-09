from py2neo import Graph, Node, Relationship
import pandas as pd

# 连接 Neo4j（修改密码）
graph = Graph("bolt://localhost:7687", auth=("neo4j", "dzy3fczUC2i"))

# 读取实体表
df_entity = pd.read_excel("object.xlsx")
print(f"实体表共 {len(df_entity)} 行")

# 第一步：创建所有节点
for idx, row in df_entity.iterrows():
    node_id = str(row['id']).strip()
    node_type = str(row['type']).strip()
    node_name = str(row['name']).strip()
    
    if node_type == "纹样":
        label = "Motif"
        meaning_text = str(row.get('寓意', ''))
        scenario_text = str(row.get('适用场景', ''))
        image_link = str(row.get('图片链接', ''))
        node = Node(label, id=node_id, name=node_name,
                    meaning=meaning_text, scenario=scenario_text, image=image_link)
    elif node_type == "寓意":
        label = "Meaning"
        node = Node(label, id=node_id, name=node_name)
    elif node_type == "适用场景":
        label = "Scenario"
        node = Node(label, id=node_id, name=node_name)
    else:
        continue
    
    graph.merge(node, label, "id")
    if idx % 50 == 0:
        print(f"已处理 {idx} 条实体")

print("节点创建完成")

# 读取关系表
df_rel = pd.read_excel("relationship.xlsx")
print(f"关系表共 {len(df_rel)} 行")

# 第二步：创建关系
for idx, row in df_rel.iterrows():
    start_id = str(row['起点id']).strip()
    end_id = str(row['终点id']).strip()
    rel_type = str(row['关系类型']).strip()
    
    # 根据 id 查找节点（不限定标签，因为 id 全局唯一）
    start_node = graph.nodes.match(id=start_id).first()
    end_node = graph.nodes.match(id=end_id).first()
    
    if start_node and end_node:
        # 避免重复创建关系
        existing = graph.match((start_node, end_node), r_type=rel_type).first()
        if not existing:
            rel = Relationship(start_node, rel_type, end_node)
            graph.create(rel)
        else:
            print(f"关系已存在：{start_id} -> {end_id}")
    else:
        print(f"跳过关系：{start_id} -> {end_id}，节点不存在")
    
    if idx % 50 == 0:
        print(f"已处理 {idx} 条关系")

print("关系创建完成")