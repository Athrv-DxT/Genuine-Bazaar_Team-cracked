# PowerShell script to create .env file
# Run this in PowerShell: .\create_env.ps1

$envContent = @"
DATABASE_URL=sqlite:///./retail_cortex.db
SECRET_KEY=dev-secret-key-change-in-production

OPENWEATHER_API_KEY=REPLACE_WITH_YOUR_OPENWEATHER_KEY
CALENDARIFIC_API_KEY=REPLACE_WITH_YOUR_CALENDARIFIC_KEY
TWITTER_BEARER_TOKEN=REPLACE_WITH_YOUR_TWITTER_TOKEN

DEBUG=True
LOG_LEVEL=INFO
"@

$envPath = Join-Path $PSScriptRoot ".env"
$envContent | Out-File -FilePath $envPath -Encoding utf8 -NoNewline

Write-Host "========================================" -ForegroundColor Green
Write-Host ".env file created!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "File location: $envPath" -ForegroundColor Yellow
Write-Host ""
Write-Host "IMPORTANT: Now edit the .env file and replace:" -ForegroundColor Yellow
Write-Host "  - REPLACE_WITH_YOUR_OPENWEATHER_KEY" -ForegroundColor Yellow
Write-Host "  - REPLACE_WITH_YOUR_CALENDARIFIC_KEY" -ForegroundColor Yellow
Write-Host "  - REPLACE_WITH_YOUR_TWITTER_TOKEN" -ForegroundColor Yellow
Write-Host ""
Write-Host "With your actual API keys!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Then run: python debug_env.py" -ForegroundColor Cyan


