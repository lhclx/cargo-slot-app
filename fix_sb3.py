with open(r'C:\Users\Administrator\.qclaw\workspace\cargo-slot-app\orders.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the duplicate 舱位管理 from 空运业务 (the one pointing to "/")
old = "<a class=\"menu-item\" href=\"/\" onclick=\"localStorage.setItem('activeMenu', '舱位管理'); toast('已恢复舱位管理')\"><span>📍 舱位管理</span></a>"
content = content.replace(old, '')
print("Removed duplicate" if old in content else "Already removed")

with open(r'C:\Users\Administrator\.qclaw\workspace\cargo-slot-app\orders.html', 'w', encoding='utf-8') as f:
    f.write(content)