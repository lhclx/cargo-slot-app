import re

with open(r'C:\Users\Administrator\.qclaw\workspace\cargo-slot-app\orders.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove 舱位管理 from 空运业务 group (the one with activeMenu link we added)
old_in_air = r"<a class=\"menu-item\" href=\"/\" onclick=\"localStorage\.setItem\('activeMenu', '舱位管理'\); toast\('已恢复舱位管理'\)\"><span>📍 舱位管理</span></a>\s*</div>\s*</div>\s*<!-- 空运业务 -->"
content = re.sub(old_in_air, "</div>\n      </div>\n      <!-- 空运业务 -->", content)

# 2. Add 舱位管理 to 海运业务 group (after 单证管理)
old_ship = '<a class="menu-item" href="#" onclick="toast\(\'开发中\'\)"><span>📄 单证管理</span></a>'
new_ship = '''<a class="menu-item" href="#" onclick="toast('开发中')"><span>📄 单证管理</span></a>
          <a class="menu-item" href="/" onclick="localStorage.setItem('activeMenu', '舱位管理'); toast('已跳到舱位管理')"><span>📍 舱位管理</span></a>'''

content = content.replace(
    '<a class="menu-item" href="#" onclick="toast(\'开发中\')"><span>📄 单证管理</span></a>',
    new_ship
)

with open(r'C:\Users\Administrator\.qclaw\workspace\cargo-slot-app\orders.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done")