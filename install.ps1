# WorkFlowy MCP Server Installation Script for Windows

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "WorkFlowy MCP Server Installation" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check for Python 3.10+
Write-Host "Checking Python version..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
            Write-Host "❌ Python $major.$minor is installed but Python 3.10+ is required." -ForegroundColor Red
            exit 1
        }
        Write-Host "✅ Python $major.$minor is installed" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Python is not installed. Please install Python 3.10 or higher." -ForegroundColor Red
    Write-Host "   Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Check for pip
Write-Host "Checking pip..." -ForegroundColor Yellow
try {
    python -m pip --version | Out-Null
    Write-Host "✅ pip is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ pip is not installed. Installing pip..." -ForegroundColor Red
    python -m ensurepip --upgrade
    Write-Host "✅ pip installed" -ForegroundColor Green
}
Write-Host ""

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (!(Test-Path "venv")) {
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "ℹ️  Virtual environment already exists" -ForegroundColor Cyan
}
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✅ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel
Write-Host "✅ pip upgraded" -ForegroundColor Green
Write-Host ""

# Install package from PyPI
Write-Host "Installing WorkFlowy MCP Server..." -ForegroundColor Yellow
pip install workflowy-mcp
Write-Host "✅ WorkFlowy MCP Server installed" -ForegroundColor Green
Write-Host ""

# Set up environment file
Write-Host "Setting up configuration..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    @"
# WorkFlowy MCP Server Configuration
WORKFLOWY_API_KEY=your_api_key_here

# Optional configuration
WORKFLOWY_API_BASE_URL=https://beta.workflowy.com/api
WORKFLOWY_REQUEST_TIMEOUT=30
WORKFLOWY_MAX_RETRIES=3
WORKFLOWY_RATE_LIMIT_REQUESTS=60
WORKFLOWY_RATE_LIMIT_WINDOW=60
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✅ Created .env file" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Please edit .env and add your WorkFlowy API key" -ForegroundColor Yellow
} else {
    Write-Host "ℹ️  .env file already exists" -ForegroundColor Cyan
}
Write-Host ""

# Create MCP configuration for Claude Desktop
Write-Host "Setting up MCP configuration for Claude Desktop..." -ForegroundColor Yellow
$claudeConfigDir = "$env:APPDATA\Claude"
$claudeConfigFile = "$claudeConfigDir\claude_desktop_config.json"

$pythonPath = (Get-Command python).Path
$serverPath = (Get-Location).Path

if (Test-Path $claudeConfigFile) {
    Write-Host "ℹ️  Claude Desktop configuration already exists" -ForegroundColor Cyan
    Write-Host "   To add WorkFlowy MCP Server, edit: $claudeConfigFile" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   Add this to the 'mcpServers' section:" -ForegroundColor Yellow
    Write-Host @"
    "workflowy": {
      "command": "$pythonPath",
      "args": ["-m", "workflowy_mcp.server"],
      "env": {
        "WORKFLOWY_API_KEY": "your_api_key_here"
      }
    }
"@ -ForegroundColor White
} else {
    if (!(Test-Path $claudeConfigDir)) {
        New-Item -ItemType Directory -Path $claudeConfigDir -Force | Out-Null
    }
    
    $config = @{
        mcpServers = @{
            workflowy = @{
                command = "$pythonPath"
                args = @("-m", "workflowy_mcp.server")
                env = @{
                    WORKFLOWY_API_KEY = "your_api_key_here"
                }
            }
        }
    }
    
    $config | ConvertTo-Json -Depth 10 | Out-File -FilePath $claudeConfigFile -Encoding UTF8
    Write-Host "✅ Created Claude Desktop configuration" -ForegroundColor Green
    Write-Host "⚠️  IMPORTANT: Edit $claudeConfigFile and add your WorkFlowy API key" -ForegroundColor Yellow
}
Write-Host ""

# Test the installation
Write-Host "Testing installation..." -ForegroundColor Yellow
try {
    python -m workflowy_mcp.server --help 2>&1 | Out-Null
    Write-Host "✅ Server module is accessible" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Server module test failed, but installation may still work" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env file and add your WorkFlowy API key" -ForegroundColor White
Write-Host "2. Restart Claude Desktop to load the MCP server" -ForegroundColor White
Write-Host "3. The WorkFlowy tools will be available in Claude" -ForegroundColor White
Write-Host ""
Write-Host "To run the server manually:" -ForegroundColor Yellow
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  python -m workflowy_mcp.server" -ForegroundColor White
Write-Host ""
Write-Host "For more information, see README.md" -ForegroundColor Yellow
Write-Host ""