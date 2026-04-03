variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "financial-agent"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

variable "openai_api_key" {
  description = "OpenAI API Key"
  type        = string
  sensitive   = true
}

variable "langfuse_secret_key" {
  description = "Langfuse Secret Key"
  type        = string
  sensitive   = true
}

variable "langfuse_public_key" {
  description = "Langfuse Public Key"
  type        = string
  sensitive   = true
}

variable "langfuse_host" {
  description = "Langfuse Host URL"
  type        = string
  default     = "https://cloud.langfuse.com"
}
