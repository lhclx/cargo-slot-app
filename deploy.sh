#!/bin/bash
# ============================================
# 货代舱位管理系统 - 百度云一键部署脚本
# 适用系统：Ubuntu 22.04 LTS
# 使用方法：
#   1. 上传整个 cargo-slot-app 目录到服务器
#   2. chmod +x deploy.sh
#   3. sudo ./deploy.sh
# ============================================

set -e

# ---- 配置区（按需修改） ----
APP_DIR="/opt/cargo-slot-app"           # 应用安装目录
APP_USER="cargo"                         # 运行应用的系统用户
APP_PORT=5000                            # Flask 内部端口
NGINX_DOMAIN=""                          # 域名（留空则用 IP 访问）
DATA_DISK="/mnt/data"                    # 数据盘挂载点（留空则用系统盘）
DATA_DIR="${DATA_DISK:-/opt}/cargo-data" # 数据存储目录
FLASK_WORKERS=2                          # Gunicorn worker 数（建议 CPU核数×2+1）
TIMEZONE="Asia/Shanghai"

echo "=========================================="
echo "  货代舱位管理系统 - 一键部署"
echo "=========================================="
echo "应用目录: $APP_DIR"
echo "数据目录: $DATA_DIR"
echo "运行用户: $APP_USER"
echo ""

# ---- 1. 系统基础配置 ----
echo "[1/8] 配置系统时区..."
timedatectl set-timezone $TIMEZONE 2>/dev/null || true

echo "[2/8] 更新系统 & 安装依赖..."
apt update
apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx \
    git curl wget unzip

# ---- 2. 创建应用用户 ----
echo "[3/8] 创建应用用户: $APP_USER..."
if ! id -u $APP_USER &>/dev/null; then
    useradd -r -m -s /bin/bash $APP_USER
    echo "  ✅ 用户 $APP_USER 已创建"
else
    echo "  ℹ️ 用户 $APP_USER 已存在"
fi

# ---- 3. 部署应用代码 ----
echo "[4/8] 部署应用代码..."

# 如果脚本在 cargo-slot-app 目录内运行，自动复制
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$SCRIPT_DIR/app.py" ]; then
    echo "  从当前目录复制代码..."
    mkdir -p $APP_DIR
    cp -r $SCRIPT_DIR/* $APP_DIR/
    # 排除不必要的文件
    rm -rf $APP_DIR/__pycache__ $APP_DIR/node_modules $APP_DIR/.git
else
    echo "  ⚠️ 未在当前目录找到 app.py，请手动将代码上传到 $APP_DIR"
    mkdir -p $APP_DIR
fi

# ---- 4. 数据目录 ----
echo "[5/8] 配置数据目录: $DATA_DIR..."
mkdir -p $DATA_DIR
# 迁移数据文件（如果存在）
if [ -d "$APP_DIR/data" ]; then
    cp -n $APP_DIR/data/*.json $DATA_DIR/ 2>/dev/null || true
fi
# 创建符号链接，让 app.py 读写 data/ 指向数据盘
rm -rf $APP_DIR/data
ln -sf $DATA_DIR $APP_DIR/data
chown -R $APP_USER:$APP_USER $DATA_DIR
chown -R $APP_USER:$APP_USER $APP_DIR

# 确保数据文件存在
touch $DATA_DIR/slots.json $DATA_DIR/orders.json $DATA_DIR/users.json $DATA_DIR/logs.json
chmod 660 $DATA_DIR/*.json
chown $APP_USER:$APP_USER $DATA_DIR/*.json

# 写入默认管理员（如果 users.json 为空）
if [ ! -s $DATA_DIR/users.json ] || [ "$(cat $DATA_DIR/users.json)" = "[]" ]; then
    cat > $DATA_DIR/users.json << 'EOF'
[
  {
    "id": 1,
    "username": "admin",
    "password": "e10adc3949ba59abbe56e057f20f883e",
    "role": "admin",
    "display_name": "管理员"
  }
]
EOF
    echo "  ✅ 默认管理员已创建 (admin / 123456)"
fi

# ---- 5. Python 虚拟环境 & 依赖 ----
echo "[6/8] 安装 Python 依赖..."
python3 -m venv $APP_DIR/venv
source $APP_DIR/venv/bin/activate
pip install --upgrade pip -q
pip install flask gunicorn openpyxl pdfplumber Pillow -q
deactivate

# ---- 6. Systemd 服务 ----
echo "[7/8] 配置 Systemd 服务..."
cat > /etc/systemd/system/cargo-slot.service << EOF
[Unit]
Description=Cargo Slot Management System
After=network.target

[Service]
Type=notify
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin:/usr/bin
Environment=FLASK_ENV=production
Environment=SESSION_SECRET=$(openssl rand -hex 32)
ExecStart=$APP_DIR/venv/bin/gunicorn \
    --workers $FLASK_WORKERS \
    --bind 127.0.0.1:$APP_PORT \
    --timeout 120 \
    --access-logfile /var/log/cargo-slot-access.log \
    --error-logfile /var/log/cargo-slot-error.log \
    app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable cargo-slot
systemctl restart cargo-slot
echo "  ✅ cargo-slot 服务已启动并设为开机自启"

# ---- 7. Nginx 反向代理 ----
echo "[8/8] 配置 Nginx 反向代理..."

# 检测服务器公网 IP
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ip.sb 2>/dev/null || echo "YOUR_SERVER_IP")
SERVER_NAME="${NGINX_DOMAIN:-$SERVER_IP}"

cat > /etc/nginx/sites-available/cargo-slot << EOF
server {
    listen 80;
    server_name $SERVER_NAME;

    client_max_body_size 20M;

    # 安全头
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options SAMEORIGIN;
    add_header X-XSS-Protection "1; mode=block";

    location / {
        proxy_pass http://127.0.0.1:$APP_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 120s;
    }

    location /static/ {
        alias $APP_DIR/static/;
        expires 7d;
    }
}
EOF

ln -sf /etc/nginx/sites-available/cargo-slot /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# ---- 8. 防火墙 ----
echo "配置防火墙..."
if command -v ufw &>/dev/null; then
    ufw allow 22/tcp    # SSH
    ufw allow 80/tcp    # HTTP
    ufw allow 443/tcp   # HTTPS
    ufw --force enable
    echo "  ✅ UFW 防火墙已配置"
elif command -v firewall-cmd &>/dev/null; then
    firewall-cmd --permanent --add-service=ssh
    firewall-cmd --permanent --add-service=http
    firewall-cmd --permanent --add-service=https
    firewall-cmd --reload
    echo "  ✅ Firewalld 防火墙已配置"
fi

# ---- 9. SSL 证书（仅域名模式） ----
if [ -n "$NGINX_DOMAIN" ]; then
    echo "申请 SSL 证书..."
    certbot --nginx -d $NGINX_DOMAIN --non-interactive --agree-tos --register-unsafely-without-email || {
        echo "  ⚠️ SSL 证书申请失败，可稍后手动运行: certbot --nginx -d $NGINX_DOMAIN"
    }
fi

# ---- 完成 ----
echo ""
echo "=========================================="
echo "  ✅ 部署完成！"
echo "=========================================="
echo ""
echo "  📡 访问地址: http://${SERVER_NAME}"
echo "  👤 默认账号: admin / 123456"
echo "  ⚠️  请立即登录后修改密码！"
echo ""
echo "  📁 应用目录: $APP_DIR"
echo "  📁 数据目录: $DATA_DIR"
echo "  📋 应用日志: /var/log/cargo-slot-error.log"
echo "  📋 访问日志: /var/log/cargo-slot-access.log"
echo ""
echo "  常用命令:"
echo "    查看状态:  systemctl status cargo-slot"
echo "    重启服务:  systemctl restart cargo-slot"
echo "    查看日志:  tail -f /var/log/cargo-slot-error.log"
echo "    更新代码:  cp -r 新代码/* $APP_DIR/ && systemctl restart cargo-slot"
echo ""
