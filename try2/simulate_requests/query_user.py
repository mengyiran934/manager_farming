import requests

# 模拟用户查询请求
email = 'user1@example.com'
response = requests.get('http://localhost:5000/api/user', params={'email': email})
print(f'用户查询响应（{email}）:\n{response.json()}')

email = 'admin@example.com'
response = requests.get('http://localhost:5000/api/user', params={'email': email})
print(f'用户查询响应（{email}）:\n{response.json()}')