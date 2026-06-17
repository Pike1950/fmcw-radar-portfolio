# =============================================================================
# build-all.ps1 -- render every figure under docs/figures/ to .svg
# =============================================================================
# Usage (from the docs/figures/ directory):
#     .\build-all.ps1
#
# Requires:
#   - MiKTeX (pdflatex on PATH)        for .tex (TikZ) figures
#   - Poppler (pdftocairo on PATH)     for PDF -> SVG conversion
#   - Python + matplotlib + numpy      for .py (data-plot) figures
#
# Recursively finds every .tex outside style/ (pdflatex x2 -> pdftocairo -svg)
# and runs every .py plot script in place. Mirrors the PMVB figure pipeline.
# =============================================================================

$ErrorActionPreference = "Stop"
$here = $PSScriptRoot

function Build-OneFigure {
    param([string]$texPath)

    $dir  = Split-Path $texPath -Parent
    $base = [System.IO.Path]::GetFileNameWithoutExtension($texPath)

    Push-Location $dir
    try {
        Write-Host "TikZ  $base..." -ForegroundColor Cyan

        # Run pdflatex twice so TikZ resolves remembered positions (overlays,
        # fit nodes referencing later content) on the second pass.
        & pdflatex -interaction=nonstopmode -halt-on-error "$base.tex" | Out-Null
        & pdflatex -interaction=nonstopmode -halt-on-error "$base.tex" | Out-Null

        if (-not (Test-Path "$base.pdf")) {
            Write-Host "  pdflatex failed for $base" -ForegroundColor Red
            return
        }

        & pdftocairo -svg "$base.pdf" "$base.svg"

        if (Test-Path "$base.svg") {
            Write-Host "  -> $base.svg" -ForegroundColor Green
        }

        # Clean up LaTeX intermediate artifacts (keep .tex and .svg)
        foreach ($ext in "aux", "log", "out", "pdf") {
            Get-ChildItem -Filter "$base.$ext" -ErrorAction SilentlyContinue |
                Remove-Item -ErrorAction SilentlyContinue
        }
    }
    finally {
        Pop-Location
    }
}

# --- TikZ figures (skip the style/ helper directory) ------------------------
Get-ChildItem -Path $here -Filter "*.tex" -Recurse |
    Where-Object { $_.DirectoryName -notmatch "[\\/]style$" } |
    ForEach-Object { Build-OneFigure $_.FullName }

# --- matplotlib data plots --------------------------------------------------
Get-ChildItem -Path $here -Filter "*.py" -Recurse |
    Where-Object { $_.DirectoryName -notmatch "[\\/]style$" } |
    ForEach-Object {
        Write-Host "plot  $($_.Name)..." -ForegroundColor Cyan
        Push-Location $_.DirectoryName
        try { & python $_.Name } finally { Pop-Location }
    }

Write-Host "`nDone." -ForegroundColor Cyan
