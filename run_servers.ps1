# Script utility to launch both FastAPI and React servers simultaneously in separate windows
$host.UI.RawUI.WindowTitle = "Launcher - React + FastAPI Híbrido"

Write-Host "==========================================================" -ForegroundColor Magenta
Write-Host "      PORTAL HÍBRIDO REACT + FASTAPI COM AGENTES DE IA    " -ForegroundColor Magenta
Write-Host "==========================================================" -ForegroundColor Magenta
Write-Host ""

# 1. Start FastAPI Backend on Port 8000
Write-Host "[FastAPI] Iniciando o Motor de IA e APIs na porta 8000..." -ForegroundColor DarkMagenta
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Title 'FastAPI Backend'; cd backend; uv run uvicorn main:app --port 8000 --reload"
Start-Sleep -Seconds 2

# 2. Start React Frontend on Port 5173 (Vite)
Write-Host "[React] Iniciando o Portal Web Frontend (Vite) na porta 5173..." -ForegroundColor DarkCyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Title 'React Frontend'; cd frontend; npm run dev"
Start-Sleep -Seconds 1

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  SUCESSO! Os servidores foram iniciados em novas janelas." -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  * Documentação das APIs (Swagger): http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "  * Portal Web Frontend (React):     http://localhost:5173" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "Pressione qualquer tecla para fechar este launcher..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

