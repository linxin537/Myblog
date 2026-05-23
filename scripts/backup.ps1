# ============================================================
# 博客数据库备份脚本 (Windows PowerShell)
# 用法: .\scripts\backup.ps1
# 建议: 添加到任务计划程序每日执行
# ============================================================

param(
    [int]$RetentionDays = 7
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
$BackupDir = Join-Path $ProjectDir "backups"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# 创建备份目录
if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
}

Write-Host "[$(Get-Date)] 开始备份..."

# 1. 数据库备份
Write-Host "  → 备份数据库..."
docker exec blog_db mysqldump `
    -u blog_user `
    -p"$env:DB_PASSWORD" `
    --single-transaction `
    --routines `
    --triggers `
    blog_db `
    > (Join-Path $BackupDir "db_${Timestamp}.sql")

if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 数据库备份失败" -ForegroundColor Red
    exit 1
}

# 2. 上传文件备份
Write-Host "  → 备份上传文件..."
$uploadsBackup = Join-Path $BackupDir "uploads_${Timestamp}.tar.gz"
docker run --rm `
    -v blog_uploads:/data `
    -v "${BackupDir}:/backup" `
    alpine tar czf "/backup/uploads_${Timestamp}.tar.gz" -C /data .

Write-Host "  → 上传文件备份完成"

# 3. 清理过期备份
Write-Host "  → 清理 ${RetentionDays} 天前的旧备份..."
Get-ChildItem $BackupDir -Filter "db_*.sql" | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$RetentionDays) } | Remove-Item -Force
Get-ChildItem $BackupDir -Filter "uploads_*.tar.gz" | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$RetentionDays) } | Remove-Item -Force

$backupFile = Join-Path $BackupDir "db_${Timestamp}.sql"
$backupSize = (Get-Item $backupFile).Length / 1MB
Write-Host "[$(Get-Date)] 备份完成: $backupFile ($([math]::Round($backupSize, 2)) MB)" -ForegroundColor Green
