# tasks.ps1 — Équivalent Windows du Makefile
# Usage : .\tasks.ps1 <commande>

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "Commandes disponibles :" -ForegroundColor Cyan
    Write-Host "  .\tasks.ps1 install   - Installe les dépendances"
    Write-Host "  .\tasks.ps1 lint      - Lance ruff check"
    Write-Host "  .\tasks.ps1 format    - Formate le code avec ruff"
    Write-Host "  .\tasks.ps1 test      - Lance pytest avec couverture"
    Write-Host "  .\tasks.ps1 clean     - Nettoie les caches Python"
    Write-Host "  .\tasks.ps1 help      - Affiche cette aide"
}

function Invoke-Install {
    Write-Host "Installation des dépendances..." -ForegroundColor Green
    python -m pip install --upgrade pip
    pip install -r requirements.txt
}

function Invoke-Lint {
    Write-Host "Linting avec ruff..." -ForegroundColor Green
    ruff check src tests
}

function Invoke-Format {
    Write-Host "Formatage avec ruff..." -ForegroundColor Green
    ruff format src tests
    ruff check --fix src tests
}

function Invoke-Test {
    Write-Host "Tests avec pytest..." -ForegroundColor Green
    pytest tests/ -v
}

function Invoke-Clean {
    Write-Host "Nettoyage des caches..." -ForegroundColor Yellow
    $paths = @(".pytest_cache", ".ruff_cache", "htmlcov", ".coverage")
    foreach ($p in $paths) {
        if (Test-Path $p) {
            Remove-Item -Recurse -Force $p
            Write-Host "  Supprimé : $p"
        }
    }
    Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | ForEach-Object {
        Remove-Item -Recurse -Force $_.FullName
        Write-Host "  Supprimé : $($_.FullName)"
    }
    Write-Host "Nettoyage terminé." -ForegroundColor Green
}

switch ($Command.ToLower()) {
    "install" { Invoke-Install }
    "lint"    { Invoke-Lint }
    "format"  { Invoke-Format }
    "test"    { Invoke-Test }
    "clean"   { Invoke-Clean }
    "help"    { Show-Help }
    default   { Write-Host "Commande inconnue : $Command" -ForegroundColor Red; Show-Help }
}
