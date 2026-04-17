$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\\..")).Path
$toolRoot = $env:A13_WINDOWS_TOOL_ROOT
if ([string]::IsNullOrWhiteSpace($toolRoot)) {
  $toolRoot = Join-Path $repoRoot ".desktop_tools"
}
$venvPython = Join-Path $toolRoot "venv\\Scripts\\python.exe"
$pyinstaller = Join-Path $toolRoot "venv\\Scripts\\pyinstaller.exe"
$buildRoot = Join-Path $toolRoot "build"
$distRoot = Join-Path $buildRoot "dist"
$workRoot = Join-Path $buildRoot "work"
$specRoot = Join-Path $buildRoot "spec"
$entryScript = Join-Path $repoRoot "a13_starter\\desktop\\launcher.py"

if (-not (Test-Path $venvPython)) {
  throw "未找到 Windows 打包环境：$venvPython"
}

New-Item -ItemType Directory -Force -Path $buildRoot, $distRoot, $workRoot, $specRoot | Out-Null

& $venvPython -m pip install -r (Join-Path $repoRoot "a13_starter\\requirements.txt") pywebview pyinstaller

& $pyinstaller `
  --noconfirm `
  --clean `
  --windowed `
  --name "CareerLoopA13App" `
  --distpath $distRoot `
  --workpath $workRoot `
  --specpath $specRoot `
  --paths $repoRoot `
  --collect-submodules webview `
  --collect-submodules clr_loader `
  --add-data "$repoRoot\\a13_starter\\web;a13_starter\\web" `
  --add-data "$repoRoot\\a13_starter\\generated;a13_starter\\generated" `
  --add-data "$repoRoot\\a13_starter\\samples;a13_starter\\samples" `
  $entryScript

Write-Host ""
Write-Host "桌面 App 已构建完成：" -ForegroundColor Green
Write-Host (Join-Path $distRoot "CareerLoopA13App\\CareerLoopA13App.exe")
