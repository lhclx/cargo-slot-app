import requests, time

minimal_pdf = b'%PDF-1.0\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>endobj\n4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n5 0 obj<</Length 100>>stream\nBT /F1 12 Tf 100 700 Td (MSC SO MEDUN7388390 NINGBO MELBOURNE 40HQ) Tj ET\nendstream\nendobj\nxref\n0 6\ntrailer<</Size 6/Root 1 0 R>>\nstartxref\n220\n%%EOF'

print('=== 连续请求测试 ===')
for i in range(3):
    files = {'file': ('test_so.pdf', minimal_pdf, 'application/pdf')}
    print(f'\n--- 第{i+1}次请求 ({time.strftime("%H:%M:%S")}) ---')
    start = time.time()
    try:
        resp = requests.post('http://localhost:5000/api/recognize-so', files=files, timeout=120)
        elapsed = time.time() - start
        print(f'耗时 {elapsed:.1f}s | Status: {resp.status_code}')
        if resp.status_code == 200:
            print('成功:', resp.json())
        else:
            print('失败:', resp.text[:200])
    except Exception as e:
        print(f'异常: {e}')
    
    if i < 2:
        print('等待2秒...')
        time.sleep(2)
