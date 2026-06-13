import sqlite3
import os

# 用户数据库初始化
conn_user = sqlite3.connect('app.db')
cursor_user = conn_user.cursor()

# 创建用户表
cursor_user.execute('''
CREATE TABLE IF NOT EXISTS users (
    uid INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    is_active BOOLEAN DEFAULT 1
)
''')


# 插入10个测试用户
for i in range(1, 11):
    cursor_user.execute("INSERT INTO users (username, password, email, phone) VALUES (?, ?, ?, ?)",
                        (f'user{i}', f'pass{i}123', f'user{i}@example.com', f'13800138{i:03d}'))

# 插入管理员用户
cursor_user.execute("INSERT INTO users (username, password, email,phone) VALUES ('admin', 'admin123', 'admin@example.com','12345678')")

conn_user.commit()
conn_user.close()

# 商品数据库初始化
conn_product = sqlite3.connect('app.db')
cursor_product = conn_product.cursor()

# 创建商品表
cursor_product.execute('''
CREATE TABLE IF NOT EXISTS products (
    pid INTEGER PRIMARY KEY AUTOINCREMENT,
    seller_uid INTEGER NOT NULL,
    price REAL NOT NULL,
    product_type TEXT NOT NULL,
    origin TEXT NOT NULL,
    sold_quantity INTEGER DEFAULT 0,
    image_path TEXT,
    FOREIGN KEY(seller_uid) REFERENCES users(uid)
)
''')

# 插入测试商品（每个用户插入2个商品）
products = [
    (1, 15.5, '蔬菜', '三亚市', 'uploads/blm.png'),
    (1, 28.0, '谷物', '浙江', 'uploads/doulei.png'),
    (2, 45.0, '水果', '浙江', 'uploads/egg.png'),
    (3, 32.0, '肉类', '广西', 'uploads/li.png'),
    (4, 19.9, '海鲜', '四川', 'uploads/mht.png'),
    (5, 22.5, '调料', '福建', 'uploads/tea.png'),
    (6, 36.0, '饮品', '云南', 'uploads/xg.png'),
    (7, 27.5, '零食', '河北', 'uploads/ymm.png'),
    (8, 40.0, '速食', '浙江', 'uploads/xlh.png'),
    (9, 18.0, '乳制品', '福建', 'uploads/xia.png'),
]

for product in products:
    cursor_product.execute("INSERT INTO products (seller_uid, price, product_type, origin, image_path) VALUES (?, ?, ?, ?, ?)", product)

# 创建上传目录
if not os.path.exists(r'static/uploads'):
    os.makedirs(r'static/uploads')

conn_product.commit()
conn_product.close()

print('数据库初始化完成！')