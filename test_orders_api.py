import urllib.request, urllib.parse, json, http.cookiejar

BASE = 'http://127.0.0.1:5000'
jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

def req(method, path, body=None, headers=None):
    url = BASE + path
    kw = {}
    if body is not None:
        kw['data'] = json.dumps(body).encode('utf-8')
        hdrs = headers or {}
        hdrs['Content-Type'] = 'application/json'
        kw['headers'] = hdrs
    elif headers:
        kw['headers'] = headers
    req = urllib.request.Request(url, method=method, **kw)
    try:
        resp = opener.open(req, timeout=5)
        return resp.status, resp.read().decode('utf-8')
    except Exception as e:
        return getattr(e, 'code', 0), str(e)

# 1. Login as admin
status, body = req('POST', '/api/auth/login', {'username':'admin','password':'admin123'})
print('LOGIN admin:', status, body[:100])

# 2. Get orders scope=own (admin's own)
status, body = req('GET', '/api/orders?scope=own&page=1&per_page=5')
print('\nGET /api/orders?scope=own:', status)
d = json.loads(body)
print('  Total:', d.get('total'), '| Page:', d.get('page'), '| Data count:', len(d.get('data',[])))
if d.get('data'):
    print('  First order owner:', d['data'][0].get('owner'), '| _owner_name:', d['data'][0].get('_owner_name'))

# 3. Get orders scope=all (admin can see all)
status, body = req('GET', '/api/orders?scope=all&page=1&per_page=5')
print('\nGET /api/orders?scope=all:', status)
d = json.loads(body)
print('  Total:', d.get('total'), '| Data count:', len(d.get('data',[])))

# 4. Get single order
status, body = req('GET', '/api/orders/1')
print('\nGET /api/orders/1:', status, body[:150])

# 5. Create new order
new_order = {
    'job_no': 'TEST-001',
    'consignee': 'Test Customer',
    'port_loading': 'SHA',
    'port_discharge': 'NZAKL',
    'carrier': 'TEST',
    'etd': '2026-07-01',
    'eta': '2026-07-20',
    'container_info': '20GP x 1',
    'pieces': 10,
    'weight': 5000,
    'volume': 10.5,
    'goods_en': 'Test Goods'
}
status, body = req('POST', '/api/orders', new_order)
print('\nPOST /api/orders (create):', status, body[:100])

# 6. Update order (if created successfully)
if status == 201:
    new_id = json.loads(body).get('id')
    status, body = req('PUT', f'/api/orders/{new_id}', {'job_no': 'TEST-001-UPDATED', 'status': '已确认'})
    print('PUT /api/orders/{new_id}:', status, body[:100])

# 7. Login as lhclx (operator)
jar2 = http.cookiejar.CookieJar()
opener2 = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar2))
def req2(method, path, body=None):
    url = BASE + path
    kw = {}
    if body is not None:
        kw['data'] = json.dumps(body).encode('utf-8')
        kw['headers'] = {'Content-Type': 'application/json'}
    req = urllib.request.Request(url, method=method, **kw)
    try:
        resp = opener2.open(req, timeout=5)
        return resp.status, resp.read().decode('utf-8')
    except Exception as e:
        return getattr(e, 'code', 0), str(e)

status, body = req2('POST', '/api/auth/login', {'username':'lhclx','password':'lhclx1981'})
print('\nLOGIN lhclx:', status, body[:100])

# lhclx (admin role) gets all orders
status, body = req2('GET', '/api/orders?scope=all&page=1&per_page=5')
print('\nlhclx GET /api/orders?scope=all:', status, '| Total:', json.loads(body).get('total'))

print('\n=== ALL TESTS COMPLETE ===')
