# Download KaTeX assets into static/vendor/katex
$dest = Join-Path -Path $PSScriptRoot -ChildPath "..\static\vendor\katex"
$dest = Resolve-Path -Path $dest -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Path -ErrorAction SilentlyContinue
if (-not $dest) { $dest = (Join-Path -Path $PSScriptRoot -ChildPath "..\static\vendor\katex"); New-Item -ItemType Directory -Force -Path $dest | Out-Null }

$files = @(
    @{ url = 'https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js'; name = 'katex.min.js' },
    @{ url = 'https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js'; name = 'contrib/auto-render.min.js' },
    @{ url = 'https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css'; name = 'katex.min.css' }
)

Write-Host "Downloading KaTeX files to $dest"
foreach ($f in $files) {
    $outPath = Join-Path $dest $f.name
    $outDir = Split-Path $outPath -Parent
    if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Force -Path $outDir | Out-Null }
    try {
        Write-Host "Fetching $($f.url) -> $outPath"
        Invoke-WebRequest -Uri $f.url -OutFile $outPath -UseBasicParsing -ErrorAction Stop
    } catch {
        Write-Warning "Failed to download $($f.url): $_"
    }
}

Write-Host "Done. You can now serve static/vendor/katex from the app."