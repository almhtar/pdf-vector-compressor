param([string]$TargetPdf)

Set-Location $PSScriptRoot

if ([string]::IsNullOrWhiteSpace($TargetPdf)) {
    $TargetPdf = Join-Path $PSScriptRoot "input.PDF"
} else {
    $TargetPdf = (Resolve-Path $TargetPdf -ErrorAction SilentlyContinue).Path
}

if (-not $TargetPdf -or -not (Test-Path $TargetPdf)) {
    Write-Host "ERROR: File not found. Drag & drop a PDF onto compress_pdf.bat or place input.PDF in this folder." -ForegroundColor Red
    exit 1
}

$inFile = Get-Item $TargetPdf
$outDir = $inFile.DirectoryName
$outName = "$($inFile.BaseName)_MaxCompressed.pdf"
$outPath = Join-Path $outDir $outName

$pyExe = "$env:USERPROFILE\scoop\apps\python\current\python.exe"
if (-not (Test-Path $pyExe)) { $pyExe = "python" }
$mutool = "C:\Program Files\MuPDF\mutool.exe"
$qpdf = (Get-Item "C:\Program Files\qpdf*\bin\qpdf.exe" | Select-Object -First 1).FullName

Remove-Item "temp_dec.pdf", "uncomp_vec.pdf", "dedup_raw.pdf", "dedup_clean.pdf", $outPath -Force -ErrorAction SilentlyContinue

Write-Host "Processing: $($inFile.Name)" -ForegroundColor Yellow
Write-Host "[1/2] Decrypting & Cleaning PDF structure..." -ForegroundColor Cyan
& $qpdf --decrypt $inFile.FullName temp_dec.pdf 2>$null
$src = if (Test-Path "temp_dec.pdf") { "temp_dec.pdf" } else { $inFile.FullName }

Write-Host "[2/2] Applying Maximum Lossless Vector Compression..." -ForegroundColor Cyan
& $mutool clean -d -gggg $src uncomp_vec.pdf
& $pyExe "$PSScriptRoot\vec_dedup.py"
& $mutool clean -gggg -z -f dedup_raw.pdf dedup_clean.pdf 2>$null
& $qpdf --object-streams=generate --recompress-flate --compression-level=9 dedup_clean.pdf $outPath

Remove-Item "temp_dec.pdf", "uncomp_vec.pdf", "dedup_raw.pdf", "dedup_clean.pdf" -Force -ErrorAction SilentlyContinue

Write-Host "`nDone! Maximum Compression Result:" -ForegroundColor Green
Get-Item $inFile.FullName, $outPath -ErrorAction SilentlyContinue |
    Select-Object Name, @{N="Size_KB";E={[math]::Round($_.Length/1KB)}}, @{N="Size_MB";E={[math]::Round($_.Length/1MB, 2)}} |
    Format-Table -AutoSize
