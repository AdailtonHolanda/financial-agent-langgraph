output "api_endpoint" {
  description = "API Gateway endpoint URL"
  value       = "${aws_api_gateway_deployment.main.invoke_url}/query"
}

output "cognito_user_pool_id" {
  description = "Cognito User Pool ID"
  value       = aws_cognito_user_pool.main.id
}

output "cognito_client_id" {
  description = "Cognito User Pool Client ID"
  value       = aws_cognito_user_pool_client.main.id
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.financial_agent.function_name
}

output "s3_bucket_name" {
  description = "S3 bucket for Lambda deployment"
  value       = aws_s3_bucket.lambda_bucket.id
}
