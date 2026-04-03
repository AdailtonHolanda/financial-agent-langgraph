$ErrorActionPreference = "Stop"

Write-Host "Starting deployment process..." -ForegroundColor Green

Write-Host "`nStep 1: Building Lambda package..." -ForegroundColor Yellow
& .\scripts\build_lambda.ps1

Write-Host "`nStep 2: Initializing Terraform..." -ForegroundColor Yellow
Set-Location terraform
terraform init

Write-Host "`nStep 3: Planning Terraform deployment..." -ForegroundColor Yellow
terraform plan -out=tfplan

Write-Host "`nStep 4: Applying Terraform configuration..." -ForegroundColor Yellow
terraform apply tfplan

Write-Host "`nStep 5: Getting outputs..." -ForegroundColor Yellow
terraform output

Set-Location ..

Write-Host "`nDeployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Create a Cognito user: aws cognito-idp admin-create-user --user-pool-id <pool-id> --username <email>"
Write-Host "2. Set initial password: aws cognito-idp admin-set-user-password --user-pool-id <pool-id> --username <email> --password <password> --permanent"
Write-Host "3. Use the notebook to test the API"
