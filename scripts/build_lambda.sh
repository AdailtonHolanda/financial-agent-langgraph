#!/bin/bash

echo "Building Lambda deployment package..."

rm -rf lambda_package
rm -f lambda_deployment.zip

mkdir -p lambda_package

pip install -r requirements.txt -t lambda_package/

cp -r src lambda_package/

cd lambda_package

zip -r ../lambda_deployment.zip . -x "*.pyc" -x "*__pycache__*"

cd ..

echo "Lambda package created: lambda_deployment.zip"
echo "Size: $(du -h lambda_deployment.zip | cut -f1)"
