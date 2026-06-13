import requests

# 模拟商品查询请求
pid = 1
response = requests.get(f'http://localhost:5000/api/product/{pid}')
print(f'商品{pid}查询响应:\n{response.json()}')

pid = 2
response = requests.get(f'http://localhost:5000/api/product/{pid}')
print(f'商品{pid}查询响应:\n{response.json()}')