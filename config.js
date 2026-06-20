// ============================================
// 货代舱位管理系统 - API 配置
// ============================================
// 
// 使用说明：
// 1. 启动本地 Flask: python app.py
// 2. 启动 Cloudflare Tunnel: cloudflared tunnel --url http://localhost:5000
// 3. 复制下面的 URL 为您的隧道地址
// 4. 保存后重新部署到 Vercel
//
// 注意：
// - 本地开发时用 localhost
// - 生产环境用 Cloudflare Tunnel URL
// - 每次重启 Tunnel URL 会变化，需要更新这里
// ============================================

const CONFIG = {
    // ⬇️ 把这里的 URL 改为您的 Cloudflare Tunnel 地址
    API_BASE_URL: 'https://YOUR-CLOUDFLARE-TUNNEL-URL.trycloudflare.com',
    
    // 或者本地开发时使用：
    // API_BASE_URL: 'http://localhost:5000'
};

// 导出配置（兼容 ES Module 和全局变量）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}
