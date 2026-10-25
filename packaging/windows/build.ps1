# Builds CleanYourTV-Setup.exe: the console menu (PyInstaller), the repo's tools and lists, an embedded
# Python with tools/requirements.txt, then the Inno Setup wizard. Needs Python 3.11 and Inno Setup 6.
# Usage: powershell -ExecutionPolicy Bypass -File packaging\windows\build.ps1
$ErrorActionPreference = 'Stop'
$here = $PSScriptRoot
$repo = Split-Path -Parent (Split-Path -Parent $here)
$build = Join-Path $here 'build'
$stage = Join-Path $build 'stage'
$pyVer = '3.11.9'
$embedZip = Join-Path $build "python-$pyVer-embed-amd64.zip"
# The embedded Python and the wheels below are 3.11, so the build Python must be 3.11 too.
$ver = (& python -c "import sys,sysconfig;print('%d.%d-%s' % (sys.version_info[:2] + (sysconfig.get_platform(),)))")
if ($ver -ne '3.11-win-amd64') { throw "python on PATH is $ver, need 3.11-win-amd64" }
$iscc = @("$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe", "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe") |
    Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $iscc) { throw 'Inno Setup 6 not found: winget install -e --id JRSoftware.InnoSetup' }

if (Test-Path $stage) { Remove-Item -Recurse -Force $stage }
New-Item -ItemType Directory -Force $stage | Out-Null

# 1. The menu as one exe.
$bvenv = Join-Path $build 'venv-build'
if (-not (Test-Path "$bvenv\Scripts\python.exe")) {
    python -m venv $bvenv
    & "$bvenv\Scripts\python.exe" -m pip install --quiet pyinstaller==6.11.1
}
& "$bvenv\Scripts\pyinstaller.exe" --noconfirm --onefile --console --name CleanYourTV `
    --distpath $stage --workpath (Join-Path $build 'pyi') --specpath $build (Join-Path $here 'cleanyourtv_menu.py')
if ($LASTEXITCODE -ne 0) { throw 'PyInstaller failed' }

# 2. The repo's own tools and lists, unchanged.
New-Item -ItemType Directory -Force "$stage\tools" | Out-Null
Get-ChildItem (Join-Path $repo 'tools') -File | Copy-Item -Destination "$stage\tools"
Copy-Item -Recurse (Join-Path $repo 'examples') "$stage\examples"
Copy-Item (Join-Path $repo 'LICENSE') "$stage\LICENSE.txt"
Copy-Item (Join-Path $here 'THIRD_PARTY_NOTICES.txt') $stage

# 3. Embedded Python where disable.ps1 and restore.ps1 look for it (tools\venv\Scripts\python.exe).
if (-not (Test-Path $embedZip)) {
    Invoke-WebRequest "https://www.python.org/ftp/python/$pyVer/python-$pyVer-embed-amd64.zip" -OutFile $embedZip
}
$pyDir = "$stage\tools\venv\Scripts"
Expand-Archive $embedZip $pyDir
Add-Content "$pyDir\python311._pth" 'Lib\site-packages' -Encoding ascii
# Same version and platform as the build Python (checked above); adb-shell 0.4.4 ships no wheel.
python -m pip install --quiet `
    --target "$pyDir\Lib\site-packages" -r (Join-Path $repo 'tools\requirements.txt')
if ($LASTEXITCODE -ne 0) { throw 'pip install of tools\requirements.txt failed' }

# 4. The wizard.
& $iscc (Join-Path $here 'CleanYourTV.iss')
if ($LASTEXITCODE -ne 0) { throw 'ISCC failed' }
Get-ChildItem (Join-Path $here 'Output\*.exe')
