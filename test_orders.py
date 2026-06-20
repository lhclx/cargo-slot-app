#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
订单管理模块 - 权限测试脚本
测试不同角色对订单的访问权限
"""
import requests
import json
import sys

BASE_URL = 'http://127.0.0.1:5000'

def test_orders_permissions():
    """测试订单权限控制"""
    print('=' * 60)
    print('  订单管理模块 - 权限测试')
    print('=' * 60)
    
    # 登录凭证
    admin_creds = {'username': 'admin', 'password': 'admin123'}
    operator_creds = {'username': 'operator', 'password': 'operator123'}
    viewer_creds = {'username': 'viewer', 'password': 'viewer123'}
    
    # 1. 创建测试用户 (如果不存在)
    print('\n[1] 准备测试用户...')
    
    # 先登录admin
    admin_session = requests.Session()
    resp = admin_session.post(f'{BASE_URL}/api/auth/login', json=admin_creds)
    if resp.ok:
        print('  ✓ Admin 登录成功')
    else:
        print(f'  ✗ Admin 登录失败: {resp.json().get("error")}')
        return
    
    # 检查是否有operator和viewer用户，没有则创建
    users_resp = admin_session.get(f'{BASE_URL}/api/users')
    users = users_resp.json() if users_resp.ok else []
    
    operator_id = None
    viewer_id = None
    
    for u in users:
        if u['username'] == 'operator':
            operator_id = u['id']
        elif u['username'] == 'viewer':
            viewer_id = u['id']
    
    # 创建operator用户
    if not operator_id:
        print('  创建 operator 用户...')
        resp = admin_session.post(f'{BASE_URL}/api/auth/register', json={
            'username': 'operator',
            'password': 'operator123',
            'role': 'operator',
            'nickname': '测试操作员'
        })
        if resp.ok:
            operator_id = resp.json()['user']['id']
            print(f'  ✓ 创建 operator 成功 (id={operator_id})')
        else:
            print(f'  ✗ 创建 operator 失败: {resp.json().get("error")}')
    
    # 创建viewer用户
    if not viewer_id:
        print('  创建 viewer 用户...')
        resp = admin_session.post(f'{BASE_URL}/api/auth/register', json={
            'username': 'viewer',
            'password': 'viewer123',
            'role': 'viewer',
            'nickname': '测试查看者'
        })
        if resp.ok:
            viewer_id = resp.json()['user']['id']
            print(f'  ✓ 创建 viewer 成功 (id={viewer_id})')
        else:
            print(f'  ✗ 创建 viewer 失败: {resp.json().get("error")}')
    
    # 2. 测试不同用户的权限
    print('\n[2] 测试订单权限...')
    
    # 登录operator
    operator_session = requests.Session()
    resp = operator_session.post(f'{BASE_URL}/api/auth/login', json=operator_creds)
    if resp.ok:
        print('  ✓ Operator 登录成功')
    else:
        print(f'  ✗ Operator 登录失败: {resp.json().get("error")}')
        return
    
    # 登录viewer
    viewer_session = requests.Session()
    resp = viewer_session.post(f'{BASE_URL}/api/auth/login', json=viewer_creds)
    if resp.ok:
        print('  ✓ Viewer 登录成功')
    else:
        print(f'  ✗ Viewer 登录失败: {resp.json().get("error")}')
        return
    
    # 3. 测试 GET /api/orders (scope=all)
    print('\n[3] 测试 GET /api/orders?scope=all ...')
    
    # Admin 可以看到所有订单
    resp = admin_session.get(f'{BASE_URL}/api/orders?scope=all')
    if resp.ok:
        data = resp.json()
        print(f'  ✓ Admin 查看全部订单: {data["total"]} 条')
    else:
        print(f'  ✗ Admin 查看全部订单失败: {resp.status_code}')
    
    # Operator 请求 scope=all 应该只能看到自己的
    resp = operator_session.get(f'{BASE_URL}/api/orders?scope=all')
    if resp.ok:
        data = resp.json()
        print(f'  ✓ Operator 查看订单(请求all): {data["total"]} 条 (应该只看到自己的)')
    else:
        print(f'  ✗ Operator 查看订单失败: {resp.status_code}')
    
    # Viewer 请求 scope=all 应该被强制改为 own
    resp = viewer_session.get(f'{BASE_URL}/api/orders?scope=all')
    if resp.ok:
        data = resp.json()
        print(f'  ✓ Viewer 查看订单(请求all): {data["total"]} 条 (应该只看到自己的或0)')
    else:
        print(f'  ✗ Viewer 查看订单失败: {resp.status_code}')
    
    # 4. 测试创建订单
    print('\n[4] 测试创建订单 (POST /api/orders)...')
    
    test_order = {
        'job_no': 'TEST001',
        'direction': '出口',
        'consignee': 'Test Consignee',
        'client': 'Test Client',
        'carrier': 'MSC',
        'port_loading': 'NINGBO',
        'port_discharge': 'SYDNEY',
        'etd': '2026-07-01',
        'eta': '2026-07-15'
    }
    
    # Admin 创建订单
    resp = admin_session.post(f'{BASE_URL}/api/orders', json=test_order)
    if resp.ok:
        admin_order = resp.json()
        admin_order_id = admin_order['id']
        print(f'  ✓ Admin 创建订单成功: id={admin_order_id}')
    else:
        print(f'  ✗ Admin 创建订单失败: {resp.json().get("error")}')
        admin_order_id = None
    
    # Operator 创建订单
    resp = operator_session.post(f'{BASE_URL}/api/orders', json={**test_order, 'job_no': 'TEST002'})
    if resp.ok:
        operator_order = resp.json()
        operator_order_id = operator_order['id']
        print(f'  ✓ Operator 创建订单成功: id={operator_order_id}')
    else:
        print(f'  ✗ Operator 创建订单失败: {resp.json().get("error")}')
        operator_order_id = None
    
    # Viewer 创建订单 (应该失败)
    resp = viewer_session.post(f'{BASE_URL}/api/orders', json={**test_order, 'job_no': 'TEST003'})
    if resp.status_code == 403:
        print('  ✓ Viewer 创建订单被拒绝 (403 Forbidden) - 符合预期')
    else:
        print(f'  ✗ Viewer 创建订单: {resp.status_code} (应该返回403)')
    
    # 5. 测试编辑订单
    print('\n[5] 测试编辑订单 (PUT /api/orders/<id>)...')
    
    if admin_order_id:
        # Admin 编辑自己的订单
        resp = admin_session.put(f'{BASE_URL}/api/orders/{admin_order_id}', 
                                json={'consignee': 'Updated by Admin'})
        if resp.ok:
            print(f'  ✓ Admin 编辑自己的订单成功')
        else:
            print(f'  ✗ Admin 编辑自己的订单失败: {resp.json().get("error")}')
        
        # Admin 编辑 Operator 的订单
        if operator_order_id:
            resp = admin_session.put(f'{BASE_URL}/api/orders/{operator_order_id}', 
                                    json={'consignee': 'Updated by Admin'})
            if resp.ok:
                print('  ✓ Admin 编辑 Operator 的订单成功 (admin有权限)')
            else:
                print(f'  ✗ Admin 编辑 Operator 的订单失败: {resp.json().get("error")}')
    
    if operator_order_id:
        # Operator 编辑自己的订单
        resp = operator_session.put(f'{BASE_URL}/api/orders/{operator_order_id}', 
                                json={'consignee': 'Updated by Operator'})
        if resp.ok:
            print(f'  ✓ Operator 编辑自己的订单成功')
        else:
            print(f'  ✗ Operator 编辑自己的订单失败: {resp.json().get("error")}')
        
        # Operator 编辑 Admin 的订单 (应该失败)
        if admin_order_id:
            resp = operator_session.put(f'{BASE_URL}/api/orders/{admin_order_id}', 
                                    json={'consignee': 'Hacked by Operator'})
            if resp.status_code == 403:
                print('  ✓ Operator 编辑 Admin 的订单被拒绝 (403 Forbidden) - 符合预期')
            else:
                print(f'  ✗ Operator 编辑 Admin 的订单: {resp.status_code} (应该返回403)')
    
    # Viewer 编辑订单 (应该失败)
    if admin_order_id:
        resp = viewer_session.put(f'{BASE_URL}/api/orders/{admin_order_id}', 
                                json={'consignee': 'Hacked by Viewer'})
        if resp.status_code == 403:
            print('  ✓ Viewer 编辑订单被拒绝 (403 Forbidden) - 符合预期')
        else:
            print(f'  ✗ Viewer 编辑订单: {resp.status_code} (应该返回403)')
    
    # 6. 测试删除订单
    print('\n[6] 测试删除订单 (DELETE /api/orders/<id>)...')
    
    # 创建一个新订单用于测试 viewer 删除权限
    test_order_for_viewer = {
        'job_no': 'TEST_VIEWER',
        'direction': '出口',
        'consignee': 'Test for Viewer',
        'client': 'Client Test',
        'carrier': 'MSC',
        'port_loading': 'NINGBO',
        'port_discharge': 'SYDNEY',
        'etd': '2026-07-01',
        'eta': '2026-07-15'
    }
    resp = admin_session.post(f'{BASE_URL}/api/orders', json=test_order_for_viewer)
    viewer_test_order_id = resp.json()['id'] if resp.ok else None
    
    if admin_order_id:
        # Operator 删除 Admin 的订单 (应该失败)
        resp = operator_session.delete(f'{BASE_URL}/api/orders/{admin_order_id}')
        if resp.status_code == 403:
            print('  [OK] Operator 删除 Admin 的订单被拒绝 (403 Forbidden) - 符合预期')
        else:
            print(f'  [FAIL] Operator 删除 Admin 的订单: {resp.status_code} (应该返回403)')
        
        # Admin 删除自己的订单
        resp = admin_session.delete(f'{BASE_URL}/api/orders/{admin_order_id}')
        if resp.ok:
            print('  [OK] Admin 删除自己的订单成功')
        else:
            print(f'  [FAIL] Admin 删除自己的订单失败: {resp.json().get("error", "")}')
    
    if operator_order_id:
        # Operator 删除自己的订单
        resp = operator_session.delete(f'{BASE_URL}/api/orders/{operator_order_id}')
        if resp.ok:
            print('  ✓ Operator 删除自己的订单成功')
        else:
            print(f'  ✗ Operator 删除自己的订单失败: {resp.json().get("error")}')
    
    # Viewer 删除订单 (应该失败)
    resp = viewer_session.delete(f'{BASE_URL}/api/orders/{operator_order_id or admin_order_id or 1}')
    if resp.status_code == 403:
        print('  ✓ Viewer 删除订单被拒绝 (403 Forbidden) - 符合预期')
    else:
        print(f'  ✗ Viewer 删除订单: {resp.status_code} (应该返回403)')
    
    print('\n' + '=' * 60)
    print('  测试完成！')
    print('=' * 60)

if __name__ == '__main__':
    try:
        test_orders_permissions()
    except requests.exceptions.ConnectionError:
        print('\n✗ 错误: 无法连接到服务器')
        print(f'  请确保 Flask 应用已启动: python app.py')
        print(f'  或者修改 BASE_URL 为正确的地址')
        sys.exit(1)
    except Exception as e:
        print(f'\n✗ 测试过程中发生错误: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
