import re

with open(r'C:\Users\Administrator\.qclaw\workspace\cargo-slot-app\orders.html', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'<a class="menu-item" href="#" onclick="toast\([^)]+\)"><span>📍 舱位管理</span></a>'
new = '<a class="menu-item" href="/" onclick="localStorage.setItem(\'activeMenu\', \'舱位管理\'); toast(\'已恢复舱位管理\')"><span>📍 舱位管理</span></a>'

found = re.search(pattern, content)
if found:
    print("Found!")
    content = re.sub(pattern, new, content)
    print("Replaced!")
else:
    print("Not found via regex")

with open(r'C:\Users\Administrator\.qclaw\workspace\cargo-slot-app\orders.html', 'w', encoding='utf-8') as f:
    f.write(content)