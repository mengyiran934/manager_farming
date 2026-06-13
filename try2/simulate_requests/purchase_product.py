import requests
import sys
#打开终端 运行 python purchase_product.py 1
# 配置后端地址
BASE_URL = 'http://localhost:5000'

# 获取商品ID参数
if len(sys.argv) < 2:
    print("请指定商品ID，例如: python purchase_product.py 123")
    sys.exit(1)

try:
    pid = int(sys.argv[1])
except ValueError:
    print("商品ID必须是数字")
    sys.exit(1)

# 构造请求数据
data = {'pid': pid}

try:
    response = requests.post(
        f"{BASE_URL}/api/purchase",
        json=data,
        headers={'Content-Type': 'application/json'}
    )

    if response.status_code == 200:
        result = response.json()
        print(f"购买成功！商品ID: {result['pid']}")
    else:
        error = response.json().get('error', '未知错误')
        print(f"购买失败({response.status_code}): {error}")

except requests.exceptions.RequestException as e:
    print(f"请求失败: {str(e)}")
except KeyError:
    print("响应数据格式异常")