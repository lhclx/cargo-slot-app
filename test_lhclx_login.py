import requests as req

BASE = 'http://127.0.0.1:5000'

r = req.post(f'{BASE}/api/auth/login', json={'username': 'lhclx', 'password': 'lhclx1981'})
print('login status', r.status_code, r.text[:200])

r2 = req.get(f'{BASE}/api/auth/me', cookies=r.cookies)
print('me status', r2.status_code, r2.text[:200])

r3 = req.get(f'{BASE}/api/slots', cookies=r.cookies)
print('slots status', r3.status_code, r3.text[:200])
