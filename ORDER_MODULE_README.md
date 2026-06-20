# 订单管理模块 - 实现说明

## 概述

本文档说明在 cargo-slot-app 项目中实现的订单管理模块，包括后端 API、前端页面和权限控制。

---

## 1. 后端实现 (app.py)

### 1.1 数据模型

订单数据存储在 `data/orders.json`，字段定义参考 CargoPlus 海运订单系统。

**核心字段：**
- `id`: 订单唯一标识
- `owner`: 创建订单的用户 ID（自动设置）
- `job_no`: 订单号
- `consignee`: 收货人
- `client`: 委托方/客户
- `port_loading`: 起运港
- `port_discharge`: 目的港
- `carrier`: 船公司
- `container_info`: 柜型信息
- `container_total`: 柜数
- `etd`: 预计离港时间
- `eta`: 预计到港时间
- `goods_en` / `goods_cn`: 货物描述
- `created_at`: 创建时间
- `updated_at`: 更新时间
- `status`: 订单状态

**字段列表：** 完整字段定义在 `ORDER_FIELDS` 列表中（约 80+ 字段）。

### 1.2 API 端点

#### GET /api/orders - 获取订单列表
- **权限：** 所有登录用户
- **参数：**
  - `scope=own|all`：查看范围（默认 `own`）
  - `page`：页码（默认 1）
  - `per_page`：每页数量（默认 20）
  - `date_field`：日期筛选字段（如 `created_at`, `etd`, `eta`）
  - `date_from` / `date_to`：日期范围
  - 其他字段参数：按字段内容模糊匹配
- **权限逻辑：**
  - `scope=own`：只能查看自己的订单（`owner == current_user.id`）
  - `scope=all`：
    - `admin` 角色：可查看所有订单
    - `operator` 角色：可查看所有订单（需前端传递 `scope=all`）
    - `viewer` 角色：强制 `scope=own`，即使请求 `scope=all`
- **返回：**
  ```json
  {
    "data": [...],
    "total": 100,
    "page": 1,
    "per_page": 20
  }
  ```

#### POST /api/orders - 创建订单
- **权限：** `admin` 或 `operator`（使用 `@require_writer` 装饰器）
- **逻辑：**
  - 自动设置 `owner = current_user['id']`
  - 自动生成 `created_at` 和 `updated_at` 时间戳
- **返回：** 创建成功的订单对象（HTTP 201）

#### GET /api/orders/<id> - 获取单个订单
- **权限：** 所有登录用户（可查看所有订单详情，因为列表已做权限过滤）
- **返回：** 订单对象

#### PUT /api/orders/<id> - 更新订单
- **权限：**
  - `admin`：可编辑所有订单
  - `operator`：**仅可编辑自己的订单**（`owner == current_user.id`）
  - `viewer`：禁止编辑（403）
- **逻辑：**
  - 不允许修改 `owner` 字段
  - 保留原始 `created_at` 和 `owner`
  - 更新 `updated_at` 时间戳
- **返回：** 更新成功的订单对象

#### DELETE /api/orders/<id> - 删除订单
- **权限：**
  - `admin`：可删除所有订单
  - `operator`：**仅可删除自己的订单**
  - `viewer`：禁止删除（403）
- **返回：** `{ "ok": true }`

### 1.3 权限装饰器

- `@require_auth`：要求登录（所有端点使用）
- `@require_writer`：要求 `admin` 或 `operator` 角色（创建、更新端点使用）
- `@require_admin`：要求 `admin` 角色（用户管理端点使用）

### 1.4 测试数据初始化

`init_test_orders()` 函数在应用启动时自动执行：
- 检查 `data/orders.json` 是否存在或为空
- 如果是，则创建 3 条测试订单：
  - 订单 1：owner = admin (id=1)
  - 订单 2：owner = operator (id=2)
  - 订单 3：owner = admin (id=1)

---

## 2. 前端实现 (orders.html)

### 2.1 认证集成

- **登录覆盖层：** 页面加载时显示登录界面，直到用户成功登录
- **checkAuth() 函数：** 检查用户登录状态
  - 调用 `/api/auth/me` 验证 session
  - 成功：隐藏登录界面，显示主界面，调用 `initApp()`
  - 失败：显示登录界面
- **doLogin() 函数：** 处理登录表单提交
- **doLogout() 函数：** 清除 session，返回登录界面

### 2.2 API 请求封装

- **apiFetch() 函数：** 封装 `fetch()`，自动添加 `credentials: 'include'`
  - 处理 401 未授权错误（自动跳转到登录界面）
  - 统一设置 `Content-Type: application/json`

### 2.3 权限控制 UI

- **initApp() 函数：** 根据用户角色初始化界面
  - `admin` / `operator`：显示"新增"按钮、显示"我的订单/全部订单"切换按钮
  - `viewer`：隐藏"新增"按钮、不显示"全部订单"选项

- **范围切换：**
  - "我的订单"按钮：`scope=own`（默认）
  - "全部订单"按钮：`scope=all`（仅 `admin` 和 `operator` 可见）

### 2.4 表格和操作列

- **表格列：** 根据 `ALL_COLUMNS` 定义动态渲染
- **操作列：**
  - "编辑"按钮：根据权限显示（`admin` 始终可见，`operator` 仅自己的订单可见）
  - "删除"按钮：根据权限显示（`admin` 或 `owner` 可见）

---

## 3. 侧边栏菜单 (index.html)

在 `index.html` 的头部工具栏添加了"📋 订单管理"链接：
```html
<a href="/orders" class="btn btn-p" style="text-decoration:none;display:inline-block;">📋 订单管理</a>
```

点击后跳转到 `/orders` 页面（即 `orders.html`）。

---

## 4. 测试脚本 (test_orders.py)

创建 `test_orders.py` 用于验证权限控制是否正常工作。

### 4.1 测试覆盖

1. **登录测试：**
   - Admin 登录
   - Operator 登录
   - Viewer 登录

2. **GET /api/orders 权限测试：**
   - Admin + `scope=all` → 看到所有订单
   - Operator + `scope=all` → 看到所有订单
   - Viewer + `scope=all` → 强制改为 `scope=own`，只能看到自己的

3. **POST /api/orders 权限测试：**
   - Admin 可创建订单
   - Operator 可创建订单
   - Viewer 创建订单返回 403

4. **PUT /api/orders/<id> 权限测试：**
   - Admin 可编辑自己的订单
   - Admin 可编辑 Operator 的订单
   - Operator 可编辑自己的订单
   - Operator 编辑 Admin 的订单返回 403
   - Viewer 编辑订单返回 403

5. **DELETE /api/orders/<id> 权限测试：**
   - Admin 可删除自己的订单
   - Admin 可删除 Operator 的订单
   - Operator 可删除自己的订单
   - Operator 删除 Admin 的订单返回 403
   - Viewer 删除订单返回 403

### 4.2 运行测试

```bash
# 启动 Flask 应用
python app.py

# 在另一个终端运行测试
python test_orders.py
```

---

## 5. 使用说明

### 5.1 启动应用

```bash
cd C:\Users\Administrator\.qclaw\workspace\cargo-slot-app
python app.py
```

应用默认运行在 `http://0.0.0.0:5000`

### 5.2 登录

- **默认管理员账号：**
  - 用户名：`admin`
  - 密码：`admin123`

- **测试账号（需先注册）：**
  - `operator` / `operator123` （角色：operator）
  - `viewer` / `viewer123` （角色：viewer）

### 5.3 访问订单管理

1. 打开浏览器访问 `http://127.0.0.1:5000`
2. 登录后，点击头部工具栏的"📋 订单管理"按钮
3. 跳转到订单管理页面 `/orders`

### 5.4 操作订单

- **查看订单：**
  - 默认显示"我的订单"
  - 点击"全部订单"查看所有订单（需 admin/operator 权限）

- **创建订单：**
  - 点击"新增"按钮
  - 填写订单信息
  - 点击"保存"

- **编辑订单：**
  - 点击订单行的"编辑"按钮
  - 修改信息
  - 点击"保存"

- **删除订单：**
  - 勾选订单（支持多选）
  - 点击"删除"按钮
  - 确认删除

---

## 6. 文件清单

| 文件 | 说明 |
|------|------|
| `app.py` | 后端主文件，包含订单 API 端点 |
| `orders.html` | 前端订单管理页面 |
| `index.html` | 前端主页面，添加"订单管理"入口 |
| `data/orders.json` | 订单数据存储文件（自动创建）|
| `test_orders.py` | 权限测试脚本 |
| `ORDER_MODULE_README.md` | 本文档 |

---

## 7. 技术要点

### 7.1 权限判断流程

```
请求到达 → @require_auth 装饰器 → 获取 current_user
      ↓
检查权限：
- GET /api/orders:
  - scope=all + admin/operator → 不过滤
  - scope=own 或 viewer → 过滤 owner == user.id
  
- POST /api/orders:
  - @require_writer → admin/operator 通过，viewer 403
  
- PUT /api/orders/<id>:
  - @require_writer → admin/operator 通过
  - 进一步检查：admin 可编辑所有，operator 仅自己的
  
- DELETE /api/orders/<id>:
  - @require_auth → 所有登录用户
  - 进一步检查：admin 或 owner 可删除
```

### 7.2 Session 管理

- 使用 Flask `session` 对象
- 登录成功后设置 `session['user_id'] = user['id']`
- 所有请求自动携带 session cookie（前端设置 `credentials: 'include'`）
- 登出时清除 `session['user_id']`

### 7.3 前端状态管理

```javascript
let currentUser = null;  // 当前登录用户信息
let currentScope = 'own';  // 当前查看范围
let allData = [];  // 所有订单数据（已根据权限过滤）
let filteredData = [];  // 根据筛选条件过滤后的数据
```

---

## 8. 后续扩展建议

1. **订单详情页：** 点击订单号跳转到详情页
2. **批量操作：** 批量分配、批量修改状态
3. **订单附件：** 上传提单、箱单等文件
4. **操作日志：** 记录订单的创建、修改、删除操作
5. **邮件通知：** 订单状态变更时自动发送邮件
6. **报表导出：** 按客户、按船公司、按日期范围导出 Excel
7. **高级筛选：** 多条件组合筛选、保存筛选方案
8. **订单模板：** 常用订单保存为模板，快速创建

---

## 9. 常见问题

### Q: 为什么 Viewer 无法看到所有订单？
A: 这是预期行为。Viewer 角色只有查看自己订单的权限。`scope=all` 参数对 Viewer 强制改为 `scope=own`。

### Q: Operator 可以编辑其他人的订单吗？
A: 不可以。Operator 只能编辑自己创建的订单。只有 Admin 可以编辑所有订单。

### Q: 如何备份订单数据？
A: 直接复制 `data/orders.json` 文件。或使用"导出"功能导出为 CSV/Excel。

### Q: 忘记密码怎么办？
A: 需要 Admin 用户在"用户管理"中重置密码，或直接在数据库中修改 `users.json`。

---

## 10. 联系方式

如有问题或建议，请联系项目负责人。

---

**文档版本：** 1.0  
**更新日期：** 2026-06-20  
**作者：** QClaw Subagent
