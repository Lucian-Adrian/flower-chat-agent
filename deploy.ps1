# XOFlowers AI Agent Deployment Script (PowerShell)
# This script helps deploy the application in different environments on Windows

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("development", "staging", "production")]
    [string]$Environment = "production",
    
    [Parameter(Mandatory=$false)]
    [switch]$Build,
    
    [Parameter(Mandatory=$false)]
    [switch]$NoPull,
    
    [Parameter(Mandatory=$false)]
    [switch]$Backup,
    
    [Parameter(Mandatory=$false)]
    [switch]$Help
)

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Function to show usage
function Show-Usage {
    Write-Host "Usage: .\deploy.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Environment ENV     Set environment (development|staging|production) [default: production]"
    Write-Host "  -Build              Build images locally instead of pulling"
    Write-Host "  -NoPull             Don't pull images before starting"
    Write-Host "  -Backup             Create backup before deployment"
    Write-Host "  -Help               Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\deploy.ps1                           Deploy production environment"
    Write-Host "  .\deploy.ps1 -Environment development  Deploy development environment"
    Write-Host "  .\deploy.ps1 -Build -Backup           Build images and create backup"
}

# Show help if requested
if ($Help) {
    Show-Usage
    exit 0
}

$ComposeFile = "docker-compose.yml"
$OverrideFile = ""
$BuildImages = $Build.IsPresent
$PullImages = -not $NoPull.IsPresent
$BackupData = $Backup.IsPresent

Write-Status "Starting deployment for environment: $Environment"

# Set compose files based on environment
switch ($Environment) {
    "production" { $OverrideFile = "docker-compose.prod.yml" }
    "staging" { $OverrideFile = "docker-compose.staging.yml" }
}

# Check if required files exist
if (-not (Test-Path $ComposeFile)) {
    Write-Error "Docker compose file not found: $ComposeFile"
    exit 1
}

if ($OverrideFile -and -not (Test-Path $OverrideFile)) {
    Write-Error "Override compose file not found: $OverrideFile"
    exit 1
}

# Check if environment file exists
$EnvFile = ".env"
switch ($Environment) {
    "production" { $EnvFile = ".env.production" }
    "staging" { $EnvFile = ".env.staging" }
}

if (-not (Test-Path $EnvFile)) {
    Write-Warning "Environment file not found: $EnvFile"
    Write-Warning "Using default environment variables"
}

# Create backup if requested
if ($BackupData) {
    Write-Status "Creating backup..."
    $BackupDir = "backups\$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    
    # Backup ChromaDB data
    if (Test-Path "chroma_db_flowers") {
        Write-Status "Backing up ChromaDB data..."
        Compress-Archive -Path "chroma_db_flowers" -DestinationPath "$BackupDir\chroma_db_flowers.zip"
    }
    
    # Backup logs
    if (Test-Path "logs") {
        Write-Status "Backing up logs..."
        Compress-Archive -Path "logs" -DestinationPath "$BackupDir\logs.zip"
    }
    
    Write-Success "Backup created in: $BackupDir"
}

# Build Docker compose command
$ComposeCmd = "docker-compose -f $ComposeFile"
if ($OverrideFile) {
    $ComposeCmd += " -f $OverrideFile"
}

# Stop existing containers
Write-Status "Stopping existing containers..."
Invoke-Expression "$ComposeCmd down"

# Pull or build images
if ($BuildImages) {
    Write-Status "Building images..."
    Invoke-Expression "$ComposeCmd build --no-cache"
} elseif ($PullImages) {
    Write-Status "Pulling latest images..."
    Invoke-Expression "$ComposeCmd pull"
}

# Create necessary directories
Write-Status "Creating necessary directories..."
@("logs", "chroma_db_flowers", "data") | ForEach-Object {
    if (-not (Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
    }
}

# Start services
Write-Status "Starting services..."
Invoke-Expression "$ComposeCmd up -d"

# Wait for services to be healthy
Write-Status "Waiting for services to be healthy..."
Start-Sleep -Seconds 10

# Check service health
Write-Status "Checking service health..."
$HealthCheckRetries = 30
$HealthCheckInterval = 5

for ($i = 1; $i -le $HealthCheckRetries; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Success "Application is healthy!"
            break
        }
    } catch {
        if ($i -eq $HealthCheckRetries) {
            Write-Error "Application failed to become healthy after $($HealthCheckRetries * $HealthCheckInterval) seconds"
            Write-Error "Check logs with: $ComposeCmd logs"
            exit 1
        } else {
            Write-Status "Waiting for application to become healthy... (attempt $i/$HealthCheckRetries)"
            Start-Sleep -Seconds $HealthCheckInterval
        }
    }
}

# Show running services
Write-Status "Running services:"
Invoke-Expression "$ComposeCmd ps"

# Show useful commands
Write-Success "Deployment completed successfully!"
Write-Host ""
Write-Status "Useful commands:"
Write-Host "  View logs:           $ComposeCmd logs -f"
Write-Host "  Check status:        $ComposeCmd ps"
Write-Host "  Stop services:       $ComposeCmd down"
Write-Host "  Restart service:     $ComposeCmd restart xoflowers-ai"
Write-Host "  Health check:        Invoke-WebRequest http://localhost:8000/health"
Write-Host "  API documentation:   http://localhost:8000/docs"

if ($Environment -eq "production") {
    Write-Host ""
    Write-Warning "Production deployment notes:"
    Write-Host "  - Configure SSL certificates in nginx.conf"
    Write-Host "  - Set up proper domain name and DNS"
    Write-Host "  - Configure monitoring and alerting"
    Write-Host "  - Set up log rotation and backup strategies"
    Write-Host "  - Review security settings and firewall rules"
}