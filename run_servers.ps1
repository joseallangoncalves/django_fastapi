# Script utility to launch both FastAPI and Django servers simultaneously in separate windows
$host.UI.RawUI.WindowTitle = "Launcher - Django + FastAPI Híbrido"

Write-Host "==========================================================" -ForegroundColor Magenta
Write-Host "      PORTAL HÍBRIDO DJANGO + FASTAPI COM AGENTES DE IA   " -ForegroundColor Magenta
Write-Host "==========================================================" -ForegroundColor Magenta
Write-Host ""

# 1. Start FastAPI Backend on Port 8000
Write-Host "[FastAPI] Iniciando o Motor de IA e APIs na porta 8000..." -ForegroundColor DarkMagenta
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Title 'FastAPI Backend'; cd backend; uv run uvicorn main:app --port 8000"
Start-Sleep -Seconds 2

# 2. Start Django Frontend on Port 8080
Write-Host "[Django] Iniciando o Portal Web Frontend na porta 8080..." -ForegroundColor DarkCyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Title 'Django Frontend'; cd frontend; uv run python manage.py runserver 8080"
Start-Sleep -Seconds 1

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  SUCESSO! Os servidores foram iniciados em novas janelas." -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  * Documentação das APIs (Swagger): http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "  * Portal Web Frontend (Django):   http://127.0.0.1:8080" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "Pressione qualquer tecla para fechar este launcher..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
