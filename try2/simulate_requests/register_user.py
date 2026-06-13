import requests
import os

# 模拟注册请求
register_url = 'http://localhost:5000/add_user'

# 准备测试数据
users = [
    {'username': 'test_user1', 'password': 'Test@123', 'email': 'test11@example.com','phone': '1234567890'},
    {'username': 'test_user2', 'password': 'Test@456', 'email': 'test2@example.com','phone': '1234567890'}
]

for user in users:
    response = requests.post(
        register_url,
        data={
            'username': user['username'],
            'password': user['password'],
            'email': user['email'],
            'phone': user['phone']
        }
    )
    print(f'注册用户 {user["username"]} 响应状态码: {response.status_code}')
    # print(f'响应内容: {response.text}\n')