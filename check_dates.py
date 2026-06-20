import json
with open('data/slots.json','r',encoding='utf-8') as f:
    data = json.load(f)
for s in data[:5]:
    print(f'ID={s["id"]} ETD={repr(s.get("etd"))} ETA={repr(s.get("eta"))}')
