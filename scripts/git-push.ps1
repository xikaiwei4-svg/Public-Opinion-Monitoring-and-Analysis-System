# git-push.ps1 — 一键推送代码到 GitHub
# 在项目根目录执行：.\scripts\git-push.ps1

$token = $env:GITHUB_TOKEN
if (-not $token) {
    Write-Host "请设置 GITHUB_TOKEN 环境变量" -ForegroundColor Red
    exit 1
}
$repo = "https://xikaiwei4-svg:${token}@github.com/xikaiwei4-svg/Public-Opinion-Monitoring-and-Analysis-System.git"

Write-Host "🚀 初始化 Git..." -ForegroundColor Cyan
if (-not (Test-Path .git)) { git init }
git remote remove origin 2>$null
git remote add origin $repo
git config user.name "Xikai wei"
git config user.email "xikaiwei4@gmail.com"

Write-Host "📦 添加文件..." -ForegroundColor Cyan
git add -A

Write-Host "📝 提交..." -ForegroundColor Cyan
git commit -m "feat: campus opinion monitoring system with Docker CI/CD" --allow-empty

Write-Host "📤 推送..." -ForegroundColor Cyan
git branch -m main 2>$null
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n🎉 推送成功！" -ForegroundColor Green
    Write-Host "https://github.com/xikaiwei4-svg/Public-Opinion-Monitoring-and-Analysis-System"
} else {
    Write-Host "`n❌ 推送失败，检查网络或 Token 权限" -ForegroundColor Red
}
