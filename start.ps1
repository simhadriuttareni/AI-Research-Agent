# Start PostgreSQL
docker start research_db 2>$null
if ($LASTEXITCODE -ne 0) {
    docker run --name research_db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=1234 -e POSTGRES_DB=research -p 5432:5432 -d postgres:15
}

# Start Backend
Start-Process -NoNewWindow -FilePath "powershell" -ArgumentList "-Command cd 'D:\AI Research Agent\ai-research-agent'; venv\Scripts\activate; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

# Wait for backend
Start-Sleep -Seconds 5

# Start Streamlit UI
Start-Process -NoNewWindow -FilePath "powershell" -ArgumentList "-Command cd 'D:\AI Research Agent\ai-research-agent'; venv\Scripts\activate; streamlit run ui/streamlit_app.py --server.headless true --server.port 8501"

# Start React UI
Start-Process -NoNewWindow -FilePath "powershell" -ArgumentList "-Command cd 'D:\AI Research Agent\frontend'; npm start"

Write-Host "✅ Application started!"
Write-Host "📊 API: http://localhost:8000"
Write-Host "📊 API Docs: http://localhost:8000/docs"
Write-Host "🎨 Streamlit UI: http://localhost:8501"
Write-Host "⚛️ React UI: http://localhost:3000"
