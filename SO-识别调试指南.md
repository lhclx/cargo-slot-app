# SO识别功能调试指南

## 🔍 问题现象
上传 PDF 文件后没有反应，无法识别。

---

## 🦊 第一步：打开浏览器控制台

1. **按 F12** 打开开发者工具
2. 切换到 **Console** 标签页
3. 尝试上传一个 PDF 文件
4. **查看 Console 中是否有红色错误信息**

---

## 📋 第二步：检查常见错误

### 错误 1：`recognizeSO is not defined`
**原因**：JS 代码有语法错误，整个 `<script>` 块失效。

**解决方法**：
```powershell
cd C:\Users\Administrator\.qclaw\workspace\cargo-slot-app
python -X utf8 -c "
import re
with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()
scripts = re.findall(r'<script>(.*?)</script>', c, re.DOTALL)
with open('__check.js', 'w', encoding='utf-8') as f:
    f.write(scripts[0])
print('JS extracted')
"
node --check __check.js 2>&1
Remove-Item '__check.js' -ErrorAction SilentlyContinue
```

如果输出错误，请根据错误信息修复 JS 语法。

---

### 错误 2：`Failed to load resource: 404 (NOT FOUND)`
**原因**：后端 `/api/recognize-so` 端点不存在或 Flask 服务器未启动。

**解决方法**：
```powershell
# 检查 Flask 是否在运行
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like '*app.py*'}

# 如果没运行，启动它
Start-Process -FilePath 'python' -ArgumentList 'app.py' -WorkingDirectory 'C:\Users\Administrator\.qclaw\workspace\cargo-slot-app'
```

---

### 错误 3：`network error` 或 `CORS error`
**原因**：跨域问题或网络问题。

**解决方法**：确保前端通过 `http://localhost:5000` 访问（不要直接用 `file://` 打开 HTML 文件）。

---

## 🐍 第三步：检查后端日志

1. **找到 Flask 服务器窗口**（应该有一个黑色命令行窗口）
2. **查看是否有新的日志输出**（当出现 `[SO识别]` 开头的日志时，说明请求已到达后端）
3. **如果没有日志输出**，说明请求未到达后端，检查前端 JS 是否出错。

---

## 📄 第四步：测试 PDF 处理

### 测试 1：用简单图片测试
1. 准备一张简单的 PNG/JPG 图片（不是 PDF）
2. 尝试上传图片
3. 如果图片能识别但 PDF 不能，说明 PDF 处理有问题

### 测试 2：检查 pdfplumber 是否正常工作
```powershell
python -c "
import pdfplumber
print('pdfplumber version:', pdfplumber.__version__)
"
```

如果报错，重新安装：
```powershell
pip install pdfplumber Pillow -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 🔧 第五步：手动测试 API 端点

### 测试 1：无文件请求（应该返回 400 错误）
```powershell
Invoke-RestMethod -Uri 'http://localhost:5000/api/recognize-so' -Method POST -ErrorAction SilentlyContinue
```

**预期结果**：返回 `{"error":"No file uploaded"}`

### 测试 2：用真实文件测试
```powershell
# 准备一个测试图片（改为你的文件路径）
$filePath = "C:\temp\test.png"

# 发送请求
$form = @{
    'file' = Get-Item $filePath
}
Invoke-RestMethod -Uri 'http://localhost:5000/api/recognize-so' -Method POST -Form $form
```

**预期结果**：返回识别后的 JSON 数据

---

## 📞 如果还有问题

请截图 **F12 → Console** 中的红色错误信息，并发给我。

同时，请告诉我：
1. 按 F12 后，Console 标签页显示什么？
2. Flask 服务器窗口有没有新的日志输出？
3. 用图片测试能否识别？还是图片和 PDF 都不能识别？

---

## ✅ 正常流程应有的表现

1. 点击「📷 识别SO」按钮 → 文件选择框弹出
2. 选择 PDF 文件 → 页面显示「⏳ 正在识别中，请稍候...」
3. 等待 5-10 秒 → 自动弹出「新增舱位」弹窗，表单已填充
4. 如果失败 → 显示红色错误提示

如果流程在任何一步卡住，请告诉我具体卡在哪一步。
