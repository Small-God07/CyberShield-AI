# ============================================
# 🚀 Installation Service Windows pour CyberShield-AI
# ============================================
# Exécuter comme ADMINISTRATEUR sur Windows Server 2019/2022
# Run as ADMINISTRATOR on Windows Server 2019/2022

# Configuration
$ServiceName = "CyberShield-AI"
$DisplayName = "CyberShield-AI - Cyber Attack Detection"
$ProjectPath = "C:\CyberShield-AI"
$VenvPath = "$ProjectPath\venv"
$PythonExe = "$VenvPath\Scripts\python.exe"
$GunicornExe = "$VenvPath\Scripts\gunicorn.exe"
$Port = 8000
$Workers = 4

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 Installation Service Windows" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

# Vérifier si l'utilisateur est administrateur
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "❌ Erreur: Veuillez exécuter ce script en tant qu'ADMINISTRATEUR !" -ForegroundColor Red
    exit 1
}

# Vérifier si le projet existe
if (-not (Test-Path $ProjectPath)) {
    Write-Host "❌ Erreur: Le chemin du projet n'existe pas: $ProjectPath" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Chemins vérifiés" -ForegroundColor Green

# Arrêter le service s'il existe déjà
$existingService = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($existingService) {
    Write-Host "⏹️ Arrêt du service existant..." -ForegroundColor Yellow
    Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    
    Write-Host "🗑️ Suppression du service existant..." -ForegroundColor Yellow
    & sc.exe delete $ServiceName
    Start-Sleep -Seconds 2
}

# Créer le script de lancement
$StartScriptPath = "$ProjectPath\start-service.ps1"
$StartScriptContent = @"
# Script de démarrage du service CyberShield-AI
cd '$ProjectPath'

# Activer l'environnement virtuel
& '$VenvPath\Scripts\Activate.ps1'

# Charger les variables d'environnement depuis .env
if (Test-Path '.env') {
    Get-Content .env | ForEach-Object {
        if (\`$_ -match '^([^=]+)=(.*)$') {
            `$key = \`$matches[1]
            `$value = \`$matches[2]
            [Environment]::SetEnvironmentVariable(\`$key, \`$value, 'Process')
        }
    }
}

# Lancer Gunicorn
& '$GunicornExe' `
    --config gunicorn_config.py `
    --workers $Workers `
    --bind 0.0.0.0:$Port `
    --timeout 120 `
    app:app
"@

Set-Content -Path $StartScriptPath -Value $StartScriptContent -Encoding UTF8
Write-Host "✅ Script de démarrage créé: $StartScriptPath" -ForegroundColor Green

# Créer le service Windows
Write-Host "📝 Création du service Windows..." -ForegroundColor Yellow

$serviceDescription = @"
Service de détection et résolution de cyberattaques basé sur l'IA.
Tourne en permanence pour analyser les menaces en temps réel.

Accès: http://localhost:$Port
Documentation: https://github.com/Small-God07/CyberShield-AI
"@

$nssm = "$ProjectPath\nssm.exe"

# Télécharger NSSM si nécessaire
if (-not (Test-Path $nssm)) {
    Write-Host "📥 Téléchargement de NSSM (Non-Sucking Service Manager)..." -ForegroundColor Yellow
    $nssmUrl = "https://nssm.cc/download/nssm-2.24-101-g897c7ad.zip"
    $nssmZip = "$ProjectPath\nssm.zip"
    
    try {
        Invoke-WebRequest -Uri $nssmUrl -OutFile $nssmZip -ErrorAction Stop
        Expand-Archive -Path $nssmZip -DestinationPath "$ProjectPath\nssm-temp" -ErrorAction Stop
        Copy-Item "$ProjectPath\nssm-temp\nssm-2.24-101-g897c7ad\win64\nssm.exe" -Destination $nssm -Force
        Remove-Item "$ProjectPath\nssm-temp" -Recurse -Force
        Remove-Item $nssmZip -Force
        Write-Host "✅ NSSM téléchargé avec succès" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ Impossible de télécharger NSSM automatiquement" -ForegroundColor Yellow
        Write-Host "Téléchargez manuellement depuis: https://nssm.cc/download" -ForegroundColor Yellow
        Write-Host "Extrayez nssm.exe vers: $nssm" -ForegroundColor Yellow
    }
}

# Créer le service avec NSSM
if (Test-Path $nssm) {
    Write-Host "🔧 Configuration du service avec NSSM..." -ForegroundColor Yellow
    
    & $nssm install $ServiceName "powershell.exe" "-ExecutionPolicy Bypass -NoProfile -File `"$StartScriptPath`""
    & $nssm set $ServiceName AppDirectory $ProjectPath
    & $nssm set $ServiceName Description $serviceDescription
    & $nssm set $ServiceName Start SERVICE_AUTO_START
    & $nssm set $ServiceName Type SERVICE_WIN32_OWN_PROCESS
    & $nssm set $ServiceName AppStdout "$ProjectPath\logs\service-output.log"
    & $nssm set $ServiceName AppStderr "$ProjectPath\logs\service-error.log"
    & $nssm set $ServiceName AppRotateFiles 1
    & $nssm set $ServiceName AppRotateOnline 1
    & $nssm set $ServiceName AppRotateSeconds 86400
    & $nssm set $ServiceName AppRotateBytes 10485760
    
    Write-Host "✅ Service configuré avec NSSM" -ForegroundColor Green
} else {
    # Alternative: Utiliser sc.exe directement (moins flexible)
    Write-Host "⚠️ Utilisation de sc.exe (configuration manuelle recommandée)" -ForegroundColor Yellow
    & sc.exe create $ServiceName `
        binPath= "powershell.exe -ExecutionPolicy Bypass -NoProfile -File `"$StartScriptPath`"" `
        start= auto `
        DisplayName= $DisplayName
}

# Créer le dossier logs
if (-not (Test-Path "$ProjectPath\logs")) {
    New-Item -ItemType Directory -Path "$ProjectPath\logs" -Force | Out-Null
    Write-Host "✅ Dossier logs créé" -ForegroundColor Green
}

# Démarrer le service
Write-Host "🚀 Démarrage du service..." -ForegroundColor Yellow
Start-Service -Name $ServiceName -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3

# Vérifier le statut
$service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
if ($service.Status -eq "Running") {
    Write-Host "✅ Service en cours d'exécution!" -ForegroundColor Green
    Write-Host "" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "✨ CyberShield-AI installé avec succès!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📊 Accès à l'application:" -ForegroundColor Green
    Write-Host "   URL: http://localhost:$Port" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🔧 Gestion du service:" -ForegroundColor Green
    Write-Host "   Démarrer : Restart-Service $ServiceName" -ForegroundColor Yellow
    Write-Host "   Arrêter  : Stop-Service $ServiceName" -ForegroundColor Yellow
    Write-Host "   Statut   : Get-Service $ServiceName" -ForegroundColor Yellow
    Write-Host "   Logs     : Get-Content $ProjectPath\logs\service-output.log -Tail 50" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "❌ Erreur: Le service n'a pas démarré" -ForegroundColor Red
    Write-Host "Consultez les logs:" -ForegroundColor Yellow
    Write-Host "   $ProjectPath\logs\service-error.log" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Pour les mises à jour: git pull && pip install -r requirements-prod.txt" -ForegroundColor Cyan
