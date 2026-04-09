import requests
from rag_search import MotifRetriever

# ========== 智谱 API 配置 ==========
API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
API_KEY = "API key"          # 替换为你实际的 Key
MODEL_NAME = "glm-4.7"               # 你测试成功的模型名称
MOCK_MODE = False                    # 关闭模拟模式
# ==================================

def call_zhipu(prompt):
    """调用智谱大模型 API"""
    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "glm-4.7",           # 确保与你测试成功的模型名一致
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        print("API 状态码:", resp.status_code)
        print("API 响应原文:", resp.text)   # 查看原始响应

        if resp.status_code == 200:
            result = resp.json()
            # 智谱返回格式: {"choices":[{"message":{"content":"..."}}]}
            content = result['choices'][0]['message']['content']
            print("API 返回内容长度:", len(content))
            return content
        else:
            return f"API 返回错误：{resp.status_code} - {resp.text}"
    except Exception as e:
        return f"请求失败：{e}"

def get_recommendation(user_input):
    print("1. 开始检索知识图谱...")
    retriever = MotifRetriever()
    kg_results = retriever.search(user_input, top_k=3)
    print(f"2. 检索到 {len(kg_results)} 个纹样")
    
    if not kg_results:
        return "抱歉，未找到匹配的彝绣纹样。"
    
    context = ""
    motif_names = []
    for r in kg_results:
        context += f"纹样：{r['node.name']}\n"
        context += f"寓意：{r['node.meaning']}\n"
        context += f"适用场景：{r['node.scenario']}\n\n"
        motif_names.append(r['node.name'])
    
    print("3. 构造提示词完毕，准备调用大模型...")
    
    prompt = f"""用户需求：{user_input}\n\n彝绣文化知识库检索结果：\n{context}\n\n请根据以上知识，为用户推荐1-2件彝绣纹样，并说明推荐理由。要求：
1. 推荐必须结合文化寓意与用户需求，语言亲切、有文化底蕴。
2. 回答控制在150字以内。
3. 请在回答的最后，严格按照以下格式附上推荐的纹样名称（用于前端匹配商品）：
[推荐纹样: 纹样1, 纹样2]"""
    
    result = call_zhipu(prompt)
    
    # 如果大模型没有按格式返回，强制追加检索到的纹样，以保证前端能匹配出商品
    if "[推荐纹样:" not in result and motif_names:
        result += f"\n[推荐纹样: {', '.join(motif_names[:2])}]"

    print(f"4. 大模型返回结果长度：{len(result)}")
    return result

if __name__ == "__main__":
    user_input = "想送一件寓意保护家人的礼物"
    result = get_recommendation(user_input)
    print("🧵 彝绣文化推荐：")
    print(result)