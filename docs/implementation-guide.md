# Serverless Inventory Processing System - Implementation Guide

## Architecture Overview
This system processes inventory CSV files uploaded to S3, updates DynamoDB, and sends low-stock alerts via SNS.

## Components
- **S3 Bucket**: Receives inventory CSV files
- **Lambda Function**: Processes CSV and updates DynamoDB
- **DynamoDB Table**: Stores inventory data
- **SNS Topic**: Sends low-stock email alerts

## Deployment Steps

### Prerequisites
- AWS CLI installed and configured
- Python 3.9+
- AWS SAM CLI (optional)

### Step 1: Create S3 Bucket
```bash
aws s3 mb s3://your-inventory-bucket-name
