import requests, json, traceback

session = requests.Session()
base = 'http://127.0.0.1:5000'

# login
r = session.post(base + '/api/auth/login', json={'username': 'admin', 'password': 'admin123'})
print('login status', r.status_code, r.text)

# me
r = session.get(base + '/api/auth/me')
print('me status', r.status_code, r.text)

# slots
try:
    r = session.get(base + '/api/slots')
    print('slots status', r.status_code, r.text[:200])
except Exception as e:
    print('slots exception', e)
    traceback.print_exc()
