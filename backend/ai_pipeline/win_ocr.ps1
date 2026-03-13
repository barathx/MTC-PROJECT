param (
    [string]$ImagePath
)

try {
    if (-not (Test-Path $ImagePath)) {
        Write-Output "OCR_ERROR: File not found: $ImagePath"
        exit 1
    }

    # Use Add-Type with direct winmd references
    $winmdPath = "C:\Windows\System32\WinMetadata"
    $assemblies = @(
        "$winmdPath\Windows.Foundation.winmd",
        "$winmdPath\Windows.Storage.winmd",
        "$winmdPath\Windows.Media.winmd",
        "$winmdPath\Windows.Graphics.winmd"
    )
    
    foreach ($asm in $assemblies) {
        if (Test-Path $asm) {
            Add-Type -Path $asm -ErrorAction SilentlyContinue
        }
    }

    # Load System.Runtime.WindowsRuntime
    [void][System.Reflection.Assembly]::LoadWithPartialName("System.Runtime.WindowsRuntime")

    $fullPath = (Resolve-Path $ImagePath).Path
    
    # Use a slightly different way to call async methods without GetAwaiter()
    # We'll use [Task]::Run or just wait for status
    
    $fileTask = [Windows.Storage.StorageFile]::GetFileFromPathAsync($fullPath)
    while ($fileTask.Status -eq 'Started') { [System.Threading.Thread]::Sleep(10) }
    $file = $fileTask.GetResults()

    $streamTask = $file.OpenAsync([Windows.Storage.FileAccessMode]::Read)
    while ($streamTask.Status -eq 'Started') { [System.Threading.Thread]::Sleep(10) }
    $stream = $streamTask.GetResults()

    $decoderTask = [Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)
    while ($decoderTask.Status -eq 'Started') { [System.Threading.Thread]::Sleep(10) }
    $decoder = $decoderTask.GetResults()

    $bitmapTask = $decoder.GetSoftwareBitmapAsync()
    while ($bitmapTask.Status -eq 'Started') { [System.Threading.Thread]::Sleep(10) }
    $bitmap = $bitmapTask.GetResults()

    $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
    if (-not $engine) {
        Write-Output "OCR_ERROR: No OCR engine available"
        exit 1
    }

    $resultTask = $engine.RecognizeAsync($bitmap)
    while ($resultTask.Status -eq 'Started') { [System.Threading.Thread]::Sleep(10) }
    $ocrResult = $resultTask.GetResults()

    Write-Output $ocrResult.Text
} catch {
    Write-Output "OCR_ERROR: $($_.Exception.Message)"
    exit 1
}
