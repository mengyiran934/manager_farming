import requests
import os

# 模拟添加商品请求
add_product_url = 'http://localhost:5000/add_product'

# 准备测试商品数据
products = [
    {
        'seller_uid': 1,
        'price': 25.9,
        'origin': '山东寿光',
        'product_type': '蔬菜',
        'image_path': r'../static/uploads/fruit_11.png'
    },
    {
        'seller_uid': 2,
        'price': 38.5,
        'origin': '黑龙江五常',
        'product_type': '谷物',
        'image_path': r'../static/uploads/fruit_11.png'
    }
]

for product in products:
    try:
        with open(product['image_path'], 'rb') as f:
            files = {'image': (os.path.basename(product['image_path']), f, 'image/jpeg')}
            response = requests.post(
                add_product_url,
                data={
                    'seller_uid': product['seller_uid'],
                    'price': product['price'],
                    'product_type': product['product_type'],
                    'origin': product['origin']
                },
                files=files
            )
            print(f'添加商品 {product["product_type"]} 响应状态码: {response.status_code}')
            # print(f'响应内容: {response.text}\n')
    except FileNotFoundError:
        print(f'图片文件 {product["image_path"]} 未找到，跳过该商品测试')
    except Exception as e:
        print(f'发生异常: {str(e)}')