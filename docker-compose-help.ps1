# Docker Compose Wrapper
# This file maintains backward compatibility
# The actual docker-compose.yml is now at: config/environments/development/docker-compose.yml

Write-Host "⚠️  docker-compose.yml has moved!" -ForegroundColor Yellow
Write-Host "New location: config/environments/development/docker-compose.yml" -ForegroundColor Cyan
Write-Host ""
Write-Host "Use this command instead:" -ForegroundColor Green
Write-Host "docker-compose -f config/environments/development/docker-compose.yml up" -ForegroundColor White
Write-Host ""
Write-Host "Or create an alias:" -ForegroundColor Green
Write-Host '$dc = "docker-compose -f config/environments/development/docker-compose.yml"' -ForegroundColor White
