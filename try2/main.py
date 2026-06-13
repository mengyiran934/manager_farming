from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os
import json
import psutil
from datetime import datetime, timedelta
import random
from collections import deque

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = r'static/uploads'

# 用户数据库配置
USER_DB = 'app.db'

# 关于查询email的接口
@app.route('/api/user')
def api_user():
    email = request.args.get('email')
    if not email:
        return jsonify({'error': 'Missing email parameter'}), 400
    
    conn = sqlite3.connect(USER_DB)
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email=?', (email,))
        user = cursor.fetchone()
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify({
            'uid': user[0],
            'username': user[1],
            'email': user[2],
            'is_active': bool(user[3])
        })
    finally:
        conn.close()

@app.route('/api/purchase', methods=['POST'])
def purchase_product():
    data = request.get_json()
    if not data or 'pid' not in data:
        return jsonify({'error': 'Missing product ID'}), 400

    conn = sqlite3.connect(PRODUCT_DB)
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET sold_quantity = sold_quantity + 1 WHERE pid=?", (data['pid'],))
        if cursor.rowcount == 0:
            return jsonify({'error': 'Product not found'}), 404
        conn.commit()
        return jsonify({'success': True, 'pid': data['pid']})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/product/<int:pid>')
def api_product(pid):
    conn = sqlite3.connect(PRODUCT_DB)
    try:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.*, u.*
            FROM products p
            JOIN users u ON p.seller_uid = u.uid
            WHERE p.pid=?
        ''', (pid,))
        product = cursor.fetchone()
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
            
        return jsonify({
            'pid': product[0],
            'price': product[1],
            'type': product[2],
            'image_url': url_for('static', filename=product[3]) if product[3] else None,
            'seller': {
                'uid': product[4],
                'username': product[5],
                'email': product[6]
            }
        })
    finally:
        conn.close()
# 商品数据库配置
PRODUCT_DB = 'app.db'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search_users')
def search_users():
    uid = request.args.get('uid')
    phone = request.args.get('phone')
    email = request.args.get('email')

    query = 'SELECT * FROM users WHERE 1=1'
    params = []

    if uid:
        query += ' AND uid=?'
        params.append(uid)
    if phone:
        query += ' AND phone=?'
        params.append(phone)
    if email:
        query += ' AND email=?'
        params.append(email)

    conn = sqlite3.connect(USER_DB)
    cursor = conn.cursor()
    cursor.execute(query, params)
    users = cursor.fetchall()
    conn.close()
    return render_template('users.html', users=users)

@app.route('/users')
def user_management():
    conn = sqlite3.connect(USER_DB)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    return render_template('users.html', users=users)

@app.route('/add_user', methods=['POST'])
def add_user():
    # 检测表单数据结构
    if 'username' in request.form:
        # 直接获取字段模式
        username = request.form['username']
        password = request.form.get('password', '')
        email = request.form['email']
        phone = request.form.get('phone', '')
    else:
        # 处理JSON字符串模式
        form_data = request.form
        json_str = list(form_data.keys())[0]
        data = json.loads(json_str)
        username = str(data['username'])
        password = str(data.get('password', ''))
        email = str(data['email'])
        phone = str(data.get('phone', ''))

    if not all([username, email]):
        return "缺少用户名或邮箱", 400
    
    # 设置默认密码（如果未提供）
    password = password or 'default_password'


    conn = sqlite3.connect(USER_DB)
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, email, phone) VALUES (?, ?, ?, ?)",
                     (username, password, 
                      email, phone))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        return "用户名或邮箱已存在", 400
    finally:
        conn.close()
    
    return redirect(url_for('user_management'))

@app.route('/add_product', methods=['POST'])
def add_product():
    seller_uid = request.form['seller_uid']
    price = request.form['price']
    product_type = request.form['product_type']
    origin = request.form.get('origin', '未知产地')  # 添加默认值避免KeyError
    
    # 处理图片上传
    image_file = request.files['image']
    if image_file:
        import uuid
                # 生成临时文件名并保存
        temp_filename = f"temp_{uuid.uuid4().hex[:6]}.jpg"
        temp_save_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        image_file.save(temp_save_path)
        
        # 获取商品数据库连接
        conn = sqlite3.connect(PRODUCT_DB)
        cursor = conn.cursor()
        
        # 验证用户UID有效性
        cursor.execute("SELECT uid FROM users WHERE uid=?", (seller_uid,))
        if not cursor.fetchone():
            conn.close()
            if os.path.exists(temp_save_path):
                os.remove(temp_save_path)
            return "用户UID不存在，新增失败"
        
        # 插入商品数据并获取pid
        cursor.execute("INSERT INTO products (seller_uid, price, product_type, origin) VALUES (?, ?, ?, ?)",
                     (seller_uid, price, product_type, origin))
        pid = cursor.lastrowid
        
        # 对应文件命名
        type_mapping = {
            '蔬菜': 'veg',
            '谷物': 'grain',
            '水果': 'fruit',
            '肉类': 'meat',
            '海鲜': 'seafood',
            '调料': 'condiment',
            '饮品': 'drink',
            '零食': 'snack',
            '速食': 'instant_food',
            '乳制品': 'dairy',
            '冷冻食品': 'frozen_food',
            '其他': 'others'
        }
        english_type = type_mapping.get(product_type, 'other')
        new_filename = f"{english_type}_{pid}.png"
        new_save_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
        os.rename(temp_save_path, new_save_path)
        
        # 更新图片路径
        image_path = os.path.join('uploads', new_filename).replace('\\', '/')
# 统一使用正斜杠路径格式
        cursor.execute("UPDATE products SET image_path=? WHERE pid=?", 
                     (image_path, pid))
        conn.commit()
    else:
        image_path = None
    
    conn = sqlite3.connect(PRODUCT_DB)
    cursor = conn.cursor()
    
    conn.commit()
    conn.close()
    return redirect(url_for('product_management'))


@app.route('/delete_user/<int:uid>', methods=['POST'])
def delete_user(uid):
    try:
        conn = sqlite3.connect(USER_DB)
        cursor = conn.cursor()
        # 先删除关联商品
        cursor.execute("DELETE FROM products WHERE seller_uid=?", (uid,))
        cursor.execute("DELETE FROM users WHERE uid=?", (uid,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return f"删除失败: {str(e)}", 500
    finally:
        conn.close()
    return redirect(url_for('user_management'))

@app.route('/delete_product/<int:pid>')
def delete_product(pid):
    try:
        conn = sqlite3.connect(PRODUCT_DB)
        cursor = conn.cursor()
        
        # 先获取图片路径
        cursor.execute("SELECT image_path FROM products WHERE pid=?", (pid,))
        image_path = cursor.fetchone()[0]
        
        # 删除数据库记录
        cursor.execute("DELETE FROM products WHERE pid=?", (pid,))
        conn.commit()
        
        # 删除图片文件
        if image_path:
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], image_path)
            if os.path.exists(full_path):
                os.remove(full_path)
    except Exception as e:
        conn.rollback()
        return f"删除失败: {str(e)}", 500
    finally:
        conn.close()
    return redirect(url_for('product_management'))

@app.route('/search_products')
def search_products():
    seller = request.args.get('seller')
    price_cond = request.args.get('price')

    base_query = '''
        SELECT p.pid, u.username, p.price, p.product_type, p.origin, p.sold_quantity, p.image_path
        FROM products p 
        JOIN users u ON p.seller_uid = u.uid
        WHERE 1=1
    '''
    params = []

    # 处理卖家查询条件
    if seller:
        if seller.isdigit():
            base_query += ' AND p.seller_uid=?'
            params.append(int(seller))
        else:
            base_query += ' AND (u.username LIKE ? OR u.email LIKE ?)'
            params.extend([f'%{seller}%', f'%{seller}%'])

    # 处理价格条件
    if price_cond:
        import re
        match = re.match(r'(<|>|<=|>=|=)?\s*([\d.]+)', price_cond)
        if match:
            operator, value = match.groups()
            operator = operator or '='
            base_query += f' AND p.price {operator} ?'
            params.append(float(value))

    conn = sqlite3.connect(PRODUCT_DB)
    cursor = conn.cursor()
    cursor.execute(base_query, params)
    products = cursor.fetchall()
    conn.close()
    return render_template('products.html', products=products)

@app.route('/products')
def product_management():
    conn = sqlite3.connect(PRODUCT_DB)
    cursor = conn.cursor()
    # 使用表联结查询商品和卖家信息
    cursor.execute('''
        SELECT p.pid, u.username, p.price, p.product_type, p.origin, p.sold_quantity, p.image_path, u.email, u.is_active
        FROM products p 
        JOIN users u ON p.seller_uid = u.uid
    ''')
    products = cursor.fetchall()
    conn.close()
    return render_template('products.html', products=products)


# 性能监控数据缓存
performance_history = deque(maxlen=60)

@app.route('/server_status')
def api_server_status():
    # 性能数据接口

    # 获取实时数据
    cpu_percent = psutil.cpu_percent()
    mem_info = psutil.virtual_memory()


    online_users = random.randint(50, 200) 
    
    # 记录历史数据
    performance_history.append({
        'time': datetime.now().isoformat(),
        'cpu': cpu_percent,
        'mem': mem_info.percent,
        'users': online_users
    })
    
    return jsonify({
        'cpu_usage': cpu_percent,
        'mem_usage': mem_info.percent,
        'online_users': online_users,
        'history': [{
            'time': item['time'],
            'value': (item['cpu'] + item['mem'])/2
        } for item in performance_history]
    })

@app.route('/server_monitor')
def server_status():
    # 监控页面渲染
    return render_template('server_status.html')

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)