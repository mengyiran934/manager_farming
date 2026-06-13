import sqlite3
import argparse
from tabulate import tabulate

def view_users(conn):
    cursor = conn.cursor()
    cursor.execute('SELECT uid, username, email, is_active FROM users')
    headers = ['UID', '用户名', '邮箱', '激活状态']
    return tabulate(cursor.fetchall(), headers=headers, tablefmt='grid')

def view_products(conn):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.pid, u.username, p.price, p.product_type, p.origin, p.sold_quantity, p.image_path
        FROM products p
        JOIN users u ON p.seller_uid = u.uid
    ''')
    headers = ['商品ID', '卖家', '价格', '商品类型', '产地', '销量', '图片路径']
    return tabulate(cursor.fetchall(), headers=headers, tablefmt='grid')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='数据库查看工具')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--users', action='store_true', help='查看用户表')
    group.add_argument('--products', action='store_true', help='查看商品表')
    
    args = parser.parse_args()
    
    try:
        with sqlite3.connect('app.db') as conn:
            if args.users:
                print(view_users(conn))
            elif args.products:
                print(view_products(conn))
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
    except ModuleNotFoundError:
        print("请先安装依赖库: pip install tabulate")

# python db_viewer.py --users  # 查看用户表
# python db_viewer.py --products  # 查看商品表