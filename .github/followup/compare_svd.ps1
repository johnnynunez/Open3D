$ErrorActionPreference='Stop'
$vswhere=Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
$vs=(& $vswhere -latest -products * -property installationPath).Trim()
$helpers=(Resolve-Path ../harness/.github/followup).Path
python "$helpers/extract_svd.py" . evidence/svd-original
if ($LASTEXITCODE -ne 0) { throw 'Original extraction failed' }
python "$helpers/make_candidate.py" . evidence/candidate
if ($LASTEXITCODE -ne 0) { throw 'Candidate extraction failed' }
python "$helpers/extract_svd.py" evidence/candidate evidence/svd-candidate
if ($LASTEXITCODE -ne 0) { throw 'Candidate numerical extraction failed' }
$results=@()
foreach($version in @('14.44.35207','14.51.36231')) {
  foreach($variant in @('original','candidate')) {
    $inc=(Resolve-Path "evidence/svd-$variant").Path
    $dir=Join-Path (Resolve-Path evidence).Path "$version-$variant"
    New-Item -ItemType Directory -Force $dir | Out-Null
    @"
@echo off
call "$vs\VC\Auxiliary\Build\vcvarsall.bat" arm64 -vcvars_ver=$version || exit /b 1
where cl
cl /nologo /std:c++17 /EHsc /O2 /W3 /WX /I"$inc" "$helpers\svd_probe.cpp" /Fe:"$dir\probe.exe" /Fo:"$dir\probe.obj"
exit /b %errorlevel%
"@ | Set-Content "$dir/compile.cmd" -Encoding ascii
    & cmd /d /c "$dir/compile.cmd" 2>&1 | Tee-Object "$dir/compile.log"
    $compiled=$LASTEXITCODE
    $runs=@()
    if($compiled -eq 0) {
      foreach($rep in 1..3) {
        & "$dir/probe.exe" 2>&1 | Tee-Object "$dir/runtime-$rep.log"
        $runs+=$LASTEXITCODE
      }
    }
    $results+=@{toolset=$version;variant=$variant;compile_exit=$compiled;runtime_exits=$runs}
  }
}
$results | ConvertTo-Json -Depth 5 | Set-Content evidence/svd-comparison.json
foreach($r in $results) {
  if($r.compile_exit -ne 0 -or $r.runtime_exits.Count -ne 3) { throw 'Incomplete compiler comparison' }
  if($r.variant -eq 'candidate' -and @($r.runtime_exits|Where-Object {$_ -ne 0}).Count -ne 0) { throw 'Candidate numerical regression failed' }
  if($r.variant -eq 'original' -and @($r.runtime_exits|Where-Object {$_ -ne 0}).Count -eq 0) { throw 'Original defect not reproduced' }
}
exit 0
