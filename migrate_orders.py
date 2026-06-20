"""迁移 orders.json 数据：添加 container_no/seal_no 字段，清除无效旧字段"""
import json, os

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
ORDERS_FILE = os.path.join(DATA_DIR, 'orders.json')

with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

NEW_FIELDS = ['carrier', 'so_no', 'booking_no', 'port_loading', 'port_discharge',
              'container_type', 'quantity', 'container_no', 'seal_no', 'client', 'sale_price',
              'remark', 'cut_vgm', 'cut_si', 'etd', 'eta', 'truck', 'customs', 'payable',
              'receivable', 'released', 'owner', 'created_at', 'updated_at']

migrated = 0
for o in data:
    changed = False
    
    # 1. Handle old container_seal -> container_no/seal_no
    if 'container_seal' in o:
        cs = str(o.pop('container_seal', '')).strip()
        if '/' in cs:
            parts = cs.split('/', 1)
            o['container_no'] = parts[0].strip()
            o['seal_no'] = parts[1].strip() if len(parts) > 1 else ''
        else:
            o['container_no'] = cs
            o['seal_no'] = ''
        changed = True
        print(f"  ⚡ ID {o.get('id')}: container_seal → container_no={o['container_no']}, seal_no={o['seal_no']}")
    
    # 2. Add missing fields
    for f in NEW_FIELDS:
        if f not in o:
            o[f] = '' if f not in ['sale_price', 'payable', 'receivable'] else ''
            changed = True
    
    # 3. Ensure so_no has value (try job_no if missing)
    if not o.get('so_no') and o.get('job_no'):
        o['so_no'] = o['job_no']
        changed = True
        print(f"  ⚡ ID {o.get('id')}: job_no → so_no = {o['so_no']}")
    
    # 4. Remove old CargoPlus fields not in NEW_FIELDS
    old_fields = ['job_no', 'doc_type', 'direction', 'consignee', 'customer_ref',
                  'vessel', 'voyage', 'etd', 'eta', 'weight', 'volume', 'pieces',
                  'container_info', 'container_total', 'goods_en', 'goods_cn',
                  'shipper', 'operator', 'sales', 'status']
    for f in old_fields:
        if f in o:
            del o[f]
            changed = True
    
    if changed:
        migrated += 1

with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n✅ 迁移完成：{migrated}/{len(data)} 条记录已处理")
