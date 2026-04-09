from flask import Flask, request, jsonify
from flask_cors import CORS
from rag_with_qwen import get_recommendation   # 注意：这里是你写好的推荐函数
import pandas as pd
import os

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)  # 允许所有跨域请求，方便前端调试

# 读取 Excel 数据构建商品库
def load_products_from_excel():
    products = []
    try:
        if os.path.exists('object.xlsx'):
            df = pd.read_excel('object.xlsx')
            # 过滤出纹样数据
            patterns = df[df['type'] == '纹样']
            for index, row in patterns.iterrows():
                # 根据纹样生成对应的虚拟商品
                products.append({
                    "id": 1000 + index,
                    "name": f"彝绣{row['name']}手工定制品",
                    "pattern_name": row['name'],
                    "price": 198.0 + (index * 10),
                    "image_url": row['图片链接'] if pd.notna(row['图片链接']) else "",
                    "meaning": row['寓意'] if pd.notna(row['寓意']) else "传统彝绣纹样",
                    "scenario": row['适用场景'] if pd.notna(row['适用场景']) else "日常使用"
                })
    except Exception as e:
        print(f"Error loading excel: {e}")
    
    # 如果没读到数据，给个默认的
    if not products:
        products = [
            {"id": 1001, "name": "马樱花手工刺绣抱枕", "pattern_name": "马樱花", "price": 128.0, "image_url": "", "meaning": "象征爱情与热情", "scenario": "家居"},
            {"id": 1002, "name": "虎纹辟邪挂件", "pattern_name": "虎纹", "price": 68.0, "image_url": "", "meaning": "辟邪纳福", "scenario": "家居/车内"}
        ]
    return products

PRODUCTS_DB = load_products_from_excel()

# 模拟数据库
MOCK_DB = {
    "cart": [],
    "orders": [],
    "favorites": []
}

@app.route('/api/cart', methods=['GET'])
def get_cart():
    """获取购物车列表"""
    return jsonify({'code': 0, 'data': MOCK_DB['cart'], 'message': 'success'})

@app.route('/api/cart/add', methods=['POST'])
def add_cart():
    """添加商品到购物车"""
    data = request.get_json()
    product_id = data.get('product_id')
    if not product_id:
         return jsonify({'code': 400, 'message': '缺少商品ID'}), 400
    
    new_item = {
        "id": len(MOCK_DB['cart']) + 1,
        "product_id": product_id,
        "name": data.get('name', '彝绣精选商品'),
        "price": data.get('price', 198.0),
        "quantity": data.get('quantity', 1),
        "sku": data.get('sku', '默认规格')
    }
    MOCK_DB['cart'].append(new_item)
    return jsonify({'code': 0, 'data': new_item, 'message': '已加入购物车'})

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """获取订单列表"""
    return jsonify({'code': 0, 'data': MOCK_DB['orders'], 'message': 'success'})

@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    """获取收藏列表"""
    return jsonify({'code': 0, 'data': MOCK_DB['favorites'], 'message': 'success'})

@app.route('/api/favorite', methods=['POST'])
def toggle_favorite():
    """收藏/取消收藏"""
    data = request.get_json()
    product_id = data.get('product_id')
    if not product_id:
         return jsonify({'code': 400, 'message': '缺少商品ID'}), 400
    
    exists = any(f['product_id'] == product_id for f in MOCK_DB['favorites'])
    if exists:
        MOCK_DB['favorites'] = [f for f in MOCK_DB['favorites'] if f['product_id'] != product_id]
        action = 'removed'
    else:
        MOCK_DB['favorites'].append({
            "product_id": product_id,
            "name": data.get('name', '新收藏商品'),
            "price": data.get('price', 198.0)
        })
        action = 'added'
        
    return jsonify({'code': 0, 'data': {'action': action}, 'message': 'success'})

@app.route('/api/products', methods=['GET'])
def get_products():
    """获取商品列表，用于发现好物页面"""
    return jsonify({'code': 0, 'data': PRODUCTS_DB, 'message': 'success'})

@app.route('/recommend', methods=['POST'])
def recommend():
    """接收用户需求，返回推荐语及相关商品"""
    # 获取前端传来的 JSON 数据
    data = request.get_json()
    user_query = data.get('query', '')
    
    # 校验
    if not user_query:
        return jsonify({'error': '请输入需求'}), 400
    
    # 调用你的推荐函数
    try:
        recommendation = get_recommendation(user_query)
        
        # 解析大模型返回的 [推荐纹样: xxx, xxx]
        recommended_products = []
        import re
        match = re.search(r'\[推荐纹样:\s*(.*?)\]', recommendation)
        if match:
            patterns = [p.strip() for p in match.group(1).split(',')]
            # 从商品库中匹配包含这些纹样的商品
            for p in patterns:
                for prod in PRODUCTS_DB:
                    if p in prod['pattern_name'] or p in prod['name']:
                        if prod not in recommended_products:
                            recommended_products.append(prod)
            # 移除这段标记文本，让给用户的回复更干净
            recommendation = recommendation.replace(match.group(0), '').strip()
            
        return jsonify({
            'recommendation': recommendation,
            'products': recommended_products[:2] # 最多推荐两个相关商品
        })
    except Exception as e:
        # 如果出错，返回错误信息
        return jsonify({'error': str(e)}), 500

# 可选：添加一个首页路由，方便测试
@app.route('/')
def home():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)