import json, sys
sys.path.insert(0, r'C:\Users\Administrator\.qclaw\workspace\cargo-slot-app')
from app import hash_password, load_users, save_users
import datetime

users = load_users()
username = 'lhclx'
if any(u.get('username') == username for u in users):
    print('用户已存在，跳过创建')
else:
    new_id = max([u['id'] for u in users], default=0) + 1
    new_user = {
        'id': new_id,
        'username': username,
        'password_hash': hash_password('lhclx1981'),
        'role': 'admin',
        'nickname': '管理员',
        'permissions': ['all'],
        'created_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    users.append(new_user)
    save_users(users)
    print(f'已创建管理员账号: {username}')
    print(f'当前用户数量: {len(users)}')
