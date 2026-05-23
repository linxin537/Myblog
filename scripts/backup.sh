#!/usr/bin/env bash
# ============================================================
# 博客数据库备份脚本 (Linux/macOS)
# 用法: bash scripts/backup.sh
# 建议: 添加到 crontab 每日执行
#   0 3 * * * cd /path/to/project && bash scripts/backup.sh >> backup.log 2>&1
# ============================================================

set -e

# 配置 (从 .env 读取或手动设置)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${PROJECT_DIR}/backups"
RETENTION_DAYS=7

# 从 .env 读取密码
if [ -f "${PROJECT_DIR}/.env" ]; then
    set -a
    source "${PROJECT_DIR}/.env"
    set +a
fi

DB_PASSWORD="${DB_PASSWORD:-}"
if [ -z "$DB_PASSWORD" ]; then
    echo "错误: 无法读取 DB_PASSWORD，请确保 .env 文件存在"
    exit 1
fi

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p "${BACKUP_DIR}"

echo "[$(date)] 开始备份..."

# 1. 数据库备份
echo "  → 备份数据库..."
docker exec blog_db mysqldump \
    -u blog_user \
    -p"${DB_PASSWORD}" \
    --single-transaction \
    --routines \
    --triggers \
    blog_db \
    > "${BACKUP_DIR}/db_${TIMESTAMP}.sql"

# 2. 上传文件备份
echo "  → 备份上传文件..."
if [ -d "${PROJECT_DIR}/backups/uploads" ]; then
    # 从 volume 备份
    docker run --rm \
        -v blog_uploads:/data \
        -v "${BACKUP_DIR}:/backup" \
        alpine tar czf "/backup/uploads_${TIMESTAMP}.tar.gz" -C /data .
    echo "  → 上传文件备份完成"
else
    echo "  → 上传目录不存在，跳过"
fi

# 3. 删除过期备份
echo "  → 清理 ${RETENTION_DAYS} 天前的旧备份..."
find "${BACKUP_DIR}" -name "db_*.sql" -mtime +${RETENTION_DAYS} -delete 2>/dev/null || true
find "${BACKUP_DIR}" -name "uploads_*.tar.gz" -mtime +${RETENTION_DAYS} -delete 2>/dev/null || true

echo "[$(date)] 备份完成:"
ls -lh "${BACKUP_DIR}/db_${TIMESTAMP}.sql"

# 保留备份列表
echo ""
echo "最近 ${RETENTION_DAYS} 天备份:"
find "${BACKUP_DIR}" -type f | sort -r | head -20
