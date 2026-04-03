Write-Host "Building Lambda deployment package..." -ForegroundColor Green

if (Test-Path lambda_package) {
    Remove-Item -Recurse -Force lambda_package
}

if (Test-Path lambda_deployment.zip) {
    Remove-Item -Force lambda_deployment.zip
}

New-Item -ItemType Directory -Path lambda_package | Out-Null

Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt -t lambda_package/

Write-Host "Copying source code..." -ForegroundColor Yellow
Copy-Item -Recurse src lambda_package/

Write-Host "Creating zip file..." -ForegroundColor Yellow
Set-Location lambda_package
Compress-Archive -Path * -DestinationPath ../lambda_deployment.zip -Force
Set-Location ..

$size = (Get-Item lambda_deployment.zip).Length / 1MB
Write-Host "Lambda package created: lambda_deployment.zip" -ForegroundColor Green
Write-Host "Size: $([math]::Round($size, 2)) MB" -ForegroundColor Green
