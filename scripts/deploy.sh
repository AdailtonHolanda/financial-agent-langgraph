#!/bin/bash

set -e

echo "Starting deployment process..."

echo "Step 1: Building Lambda package..."
./scripts/build_lambda.sh

echo "Step 2: Initializing Terraform..."
cd terraform
terraform init

echo "Step 3: Planning Terraform deployment..."
terraform plan -out=tfplan

echo "Step 4: Applying Terraform configuration..."
terraform apply tfplan

echo "Step 5: Getting outputs..."
terraform output

echo "Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Create a Cognito user: aws cognito-idp admin-create-user --user-pool-id <pool-id> --username <email>"
echo "2. Set initial password: aws cognito-idp admin-set-user-password --user-pool-id <pool-id> --username <email> --password <password> --permanent"
echo "3. Use the notebook to test the API"
