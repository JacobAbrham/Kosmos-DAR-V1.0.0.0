# Quick Demo - Test .env Configuration in Both GUIs

Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  KOSMOS GUI .env Configuration Demo" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "You now have TWO ways to configure .env interactively!" -ForegroundColor Green
Write-Host ""

Write-Host "Option 1: Windows Desktop App" -ForegroundColor Yellow
Write-Host "  • Native Windows GUI" -ForegroundColor Gray
Write-Host "  • Scrollable form dialog" -ForegroundColor Gray
Write-Host "  • Perfect for desktop users" -ForegroundColor Gray
Write-Host ""
Write-Host "  To test:" -ForegroundColor White
Write-Host "  python gui/setup_gui.py" -ForegroundColor Cyan
Write-Host ""

Write-Host "Option 2: Web Dashboard" -ForegroundColor Yellow
Write-Host "  • Modern web interface" -ForegroundColor Gray
Write-Host "  • Beautiful modal overlay" -ForegroundColor Gray
Write-Host "  • Works on any device" -ForegroundColor Gray
Write-Host ""
Write-Host "  To test:" -ForegroundColor White
Write-Host "  python gui/web_setup.py" -ForegroundColor Cyan
Write-Host "  Then open: http://localhost:5000" -ForegroundColor Cyan
Write-Host ""

Write-Host "───────────────────────────────────────" -ForegroundColor Gray
Write-Host ""

$choice = Read-Host "Which would you like to test? (1=Desktop, 2=Web, 0=Exit)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Launching Desktop App..." -ForegroundColor Green
        Write-Host "Steps to test:" -ForegroundColor White
        Write-Host "  1. Select an environment" -ForegroundColor Gray
        Write-Host "  2. Click 'Start Setup'" -ForegroundColor Gray
        Write-Host "  3. .env dialog will appear" -ForegroundColor Gray
        Write-Host "  4. Modify any values" -ForegroundColor Gray
        Write-Host "  5. Click 'Save & Continue'" -ForegroundColor Gray
        Write-Host "  6. Check .env file was created!" -ForegroundColor Gray
        Write-Host ""
        
        if (Test-Path "gui/setup_gui.py") {
            python gui/setup_gui.py
        } else {
            Write-Host "Error: gui/setup_gui.py not found" -ForegroundColor Red
        }
    }
    
    "2" {
        Write-Host ""
        Write-Host "Launching Web Dashboard..." -ForegroundColor Green
        Write-Host "Steps to test:" -ForegroundColor White
        Write-Host "  1. Browser will open to http://localhost:5000" -ForegroundColor Gray
        Write-Host "  2. Click an environment card" -ForegroundColor Gray
        Write-Host "  3. Click 'Start Setup'" -ForegroundColor Gray
        Write-Host "  4. Modal with .env form appears" -ForegroundColor Gray
        Write-Host "  5. Fill in/modify values" -ForegroundColor Gray
        Write-Host "  6. Click 'Save & Continue'" -ForegroundColor Gray
        Write-Host "  7. Check .env file was created!" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Starting server..." -ForegroundColor Yellow
        Write-Host ""
        
        if (Test-Path "gui/web_setup.py") {
            # Check if dependencies are installed
            $flaskInstalled = python -c "import flask" 2>$null
            if ($LASTEXITCODE -ne 0) {
                Write-Host "Installing required packages..." -ForegroundColor Yellow
                pip install flask flask-socketio python-socketio
            }
            
            # Start server and open browser
            Start-Process "http://localhost:5000"
            python gui/web_setup.py
        } else {
            Write-Host "Error: gui/web_setup.py not found" -ForegroundColor Red
        }
    }
    
    "0" {
        Write-Host "Exiting..." -ForegroundColor Gray
        exit 0
    }
    
    default {
        Write-Host "Invalid choice. Exiting..." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Demo complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Check your .env file:" -ForegroundColor White
Write-Host "  Get-Content .env" -ForegroundColor Cyan
Write-Host ""
Write-Host "Full documentation:" -ForegroundColor White
Write-Host "  • gui/ENV_CONFIG_COMPLETE.md" -ForegroundColor Cyan
Write-Host "  • gui/UPDATE_INSTRUCTIONS.md" -ForegroundColor Cyan
Write-Host "  • GUI_QUICK_START.md" -ForegroundColor Cyan
Write-Host ""
