$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting Cross-Platform Build for Raspberry Pi (ARM64)..." -ForegroundColor Cyan

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is not installed or not in PATH."
}

# Use explicit objects
$projects = @(
    [PSCustomObject]@{ Name = "caro-website"; Path = "./caro-website"; Image = "caro-website:latest"; BuildArg = "" },
    [PSCustomObject]@{ Name = "keto-monitor"; Path = "./keto-monitor"; Image = "keto-monitor:latest"; BuildArg = "" },
    [PSCustomObject]@{ Name = "handball-backend"; Path = "./Handball_DB"; Image = "handball-backend:latest"; BuildArg = "" },
    # Ensure nested path uses forward slashes or backslashes correctly. Docker likes forward on Windows too usually.
    [PSCustomObject]@{ Name = "handball-frontend"; Path = "./Handball_DB/frontend"; Image = "handball-frontend:latest"; BuildArg = "REACT_APP_API_URL=https://api.thy-projects.com" },
    [PSCustomObject]@{ Name = "landing-page"; Path = "./landing-page"; Image = "landing-page:latest"; BuildArg = "" }
)

$outDir = ".\pi-images"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

foreach ($p in $projects) {
    Write-Host "`n🔨 Building $($p.Name)..." -ForegroundColor Yellow

    # Simple string construction to avoid PS array expansion issues
    $cmd = "docker buildx build --platform linux/arm64 -t $($p.Image) $($p.Path) --load"
    
    if ($p.BuildArg -ne "") {
        $cmd = "$cmd --build-arg `"$($p.BuildArg)`""
    }

    Write-Host "Exec: $cmd" -ForegroundColor Gray
    
    # Execute
    Invoke-Expression $cmd
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Build FAILED for $($p.Name)!"
    }

    Write-Host "📦 Saving $($p.Name) to archive..." -ForegroundColor Gray
    $tarPath = "$outDir\$($p.Name).tar"
    
    docker save -o $tarPath $p.Image
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Save FAILED for $($p.Name)!"
    }
    
    Write-Host "✅ Saved to $tarPath" -ForegroundColor Green
}

Write-Host "`n🎉 All Builds Complete!" -ForegroundColor Cyan
