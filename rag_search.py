import pandas as pd
import os

class MotifRetriever:
    def __init__(self, excel_path="object.xlsx"):
        # 读取 Excel 数据，避免依赖 Neo4j 数据库或本地大模型（解决崩溃问题）
        self.df = pd.DataFrame()
        if os.path.exists(excel_path):
            self.df = pd.read_excel(excel_path)
            self.df = self.df[self.df['type'] == '纹样'].copy()
            self.df = self.df.fillna('')

    def search(self, query, top_k=3):
        if self.df.empty:
            return []
            
        # 简单的关键字匹配打分算法，代替容易崩溃的 SentenceTransformer
        # 计算每个纹样的文本与查询语句的字符重合度
        def calculate_score(row):
            text = str(row['name']) + " " + str(row['寓意']) + " " + str(row['适用场景'])
            score = 0
            # 基础单字匹配
            for char in query:
                if char in text:
                    score += 1
            # 关键词额外加分 (提取长度为2的词)
            for i in range(len(query) - 1):
                word = query[i:i+2]
                if word in text:
                    score += 5
            return score
            
        # 复制一份以避免警告
        temp_df = self.df.copy()
        temp_df['score'] = temp_df.apply(calculate_score, axis=1)
        
        # 按得分排序
        temp_df = temp_df.sort_values(by='score', ascending=False)
        top_patterns = temp_df.head(top_k)
        
        results = []
        for _, row in top_patterns.iterrows():
            results.append({
                'node.id': str(row['id']),
                'node.name': str(row['name']),
                'node.meaning': str(row['寓意']),
                'node.scenario': str(row['适用场景']),
                'score': float(row['score'])
            })
            
        return results

if __name__ == "__main__":
    retriever = MotifRetriever()
    test_query = "想送给长辈一件寓意健康长寿的礼物"
    results = retriever.search(test_query)
    for r in results:
        print(f"纹样：{r['node.name']}，相似度分数：{r['score']}")
        print(f"寓意：{r['node.meaning']}")
        print(f"适用场景：{r['node.scenario']}\n")