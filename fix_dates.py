import json, re

DATA_FILE = 'data/slots.json'

with open(DATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

def normalize_date(val):
    if not val:
        return ''
    s = str(val).strip()
    m = re.match(r'(\d{4}-\d{2}-\d{2})', s)
    return m.group(1) if m else s

fixed = 0
for s in data:
    old_etd = s.get('etd', '')
    old_eta = s.get('eta', '')
    new_etd = normalize_date(old_etd)
    new_eta = normalize_date(old_eta)
    if old_etd != new_etd or old_eta != new_eta:
        print(f'  ID={s["id"]}: ETD {old_etd} -> {new_etd}, ETA {old_eta} -> {new_eta}')
        s['etd'] = new_etd
        s['eta'] = new_eta
        fixed += 1

with open(DATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'\n✅ 修复完成，共修复 {fixed} 条记录')
