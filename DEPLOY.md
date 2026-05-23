# 部署文档 — 个人博客平台

> 适用于 Linux 云服务器（Ubuntu 22.04 / Debian 12 / CentOS 9+）

## 前置要求

| 软件 | 最低版本 | 安装说明 |
|------|----------|----------|
| Docker | 24.0+ | `curl -fsSL https://get.docker.com \| bash` |
| Docker Compose | 2.20+ | Docker Desktop 已内置，Linux 按需安装插件 |
| Git | 2.0+ | `apt install git` / `yum install git` |

验证安装：
```bash
docker --version
docker compose version
```

---

## 一、快速部署（5 分钟）

### 1. 克隆项目

```bash
git clone <your-repo-url> /opt/blog
cd /opt/blog
```

### 2. 配置环境变量

```bash
cp .env.production .env
nano .env   # 修改所有 "change-this" 开头的值
```

必须修改的值：
- `DB_ROOT_PASSWORD` — MySQL root 密码
- `DB_PASSWORD` — 博客数据库用户密码（需与 `DATABASE_URL` 中的密码一致）
- `JWT_SECRET_KEY` — 随机字符串，建议 `openssl rand -hex 32` 生成
- `CORS_ORIGINS` — 改为你的域名，如 `https://your-domain.com`

### 3. 启动服务

```bash
docker compose up -d
```

### 4. 验证

```bash
# 检查所有服务运行正常
docker compose ps

# API 健康检查
curl http://localhost/api/v1/health
# 应返回: {"status":"ok","database":"connected"}

# 浏览器访问
# http://<服务器IP>
```

---

## 二、配置 HTTPS（推荐）

使用 Let's Encrypt 免费证书：

```bash
# 1. 安装 Certbot
apt install certbot python3-certbot-nginx -y

# 2. 先确保域名 DNS 已解析到服务器
# 3. 生成证书（standalone 模式需要先停掉 Nginx）
docker compose stop frontend
certbot certonly --standalone -d your-domain.com
docker compose start frontend

# 4. 修改 nginx.conf 添加 SSL 配置，然后重建前端容器
# （见下方 SSL 配置模板）
```

### Nginx SSL 配置（追加到 nginx.conf 的 server 块）

```nginx
listen 443 ssl http2;
ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers HIGH:!aNULL:!MD5;

# HTTP → HTTPS 重定向（另起一个 server 块）
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$host$request_uri;
}
```

---

## 三、目录结构

```
/opt/blog/
├── docker-compose.yml      # 服务编排
├── Dockerfile              # 后端镜像
├── Dockerfile.frontend     # 前端镜像
├── nginx.conf              # Nginx 配置
├── .env                    # 环境变量（从 .env.production 复制）
├── backend/                # FastAPI 源码
├── frontend/               # Vue 3 源码
├── scripts/
│   ├── backup.sh           # Linux 备份脚本
│   └── backup.ps1          # Windows 备份脚本
├── backups/                # 备份文件（脚本自动创建）
└── DEPLOY.md               # 本文档
```

---

## 四、日常运维

### 查看日志

```bash
# 全部服务
docker compose logs -f

# 单个服务
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db
```

### 重启服务

```bash
docker compose restart          # 重启所有
docker compose restart backend  # 只重启后端
```

### 更新部署

```bash
git pull
docker compose up -d --build   # 重新构建并启动
docker compose exec backend pip install -r requirements.txt  # 如有新依赖
```

### 数据库备份

```bash
# 手动备份
bash scripts/backup.sh

# 自动备份（每日凌晨 3 点）
crontab -e
# 添加:
0 3 * * * cd /opt/blog && bash scripts/backup.sh >> /opt/blog/backups/backup.log 2>&1
```

### 恢复数据库

```bash
# 1. 找到要恢复的备份文件
ls backups/

# 2. 恢复
docker exec -i blog_db mysql -u blog_user -p blog_db < backups/db_20260101_030000.sql
# 输入密码
```

### 查看磁盘占用

```bash
docker system df          # Docker 占用
du -sh backups/ uploads/  # 备份和上传文件
```

---

## 五、容器说明

| 容器 | 镜像 | 端口 | 说明 |
|------|------|------|------|
| `blog_db` | mysql:8.0 | 3306（内网） | MySQL 数据库 |
| `blog_backend` | Dockerfile 构建 | 8000（内网） | FastAPI 后端 |
| `blog_frontend` | Dockerfile.frontend 构建 | 80 → 宿主机 | Nginx + 前端静态文件 |

---

## 六、常见问题

### MySQL 启动失败

```bash
# 检查日志
docker compose logs db

# 常见原因: 端口冲突、权限问题
# 清理数据卷重新初始化（会丢失数据！）
docker compose down -v
docker compose up -d
```

### 后端连接数据库失败

```bash
# 检查 .env 中 DATABASE_URL 密码是否与 DB_PASSWORD 一致
# 等待 MySQL 健康检查通过后再试
docker compose logs backend
```

### 前端页面 404

```bash
# 检查 SPA 路由回退
# nginx.conf 中确保有: try_files $uri $uri/ /index.html;
docker compose restart frontend
```

### 文件上传失败

```bash
# 检查 uploads volume 是否正常
docker compose exec backend ls -la /app/static/uploads
# 检查文件大小限制 (默认 10MB)
```

---

## 七、安全建议

1. **修改默认端口**：如不使用 80 端口，修改 `docker-compose.yml` 中的端口映射
2. **防火墙**：仅开放 80/443 端口，3306 不对外暴露
   ```bash
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw enable
   ```
3. **定期更新**：`docker compose pull` 拉取最新基础镜像
4. **备份策略**：3-2-1 原则（3 份备份，2 种介质，1 份异地）
