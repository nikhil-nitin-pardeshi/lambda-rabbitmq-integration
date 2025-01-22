# 🚀 Lambda Function to Push Messages to RabbitMQ

This project includes two AWS Lambda functions written in 🐍 Python that connect to 🐇 RabbitMQ and push messages to a queue. One function leverages environment variables for configuration, while the other securely retrieves credentials from AWS Secrets Manager.

## 📄 Description

This project provides:
- A Lambda function that connects to RabbitMQ using environment variables.
- A Lambda function that connects to RabbitMQ using credentials stored in AWS Secrets Manager.

## ✅ Prerequisites

- An AWS account with permissions to create and manage Lambda functions and AWS Secrets Manager.
- A RabbitMQ server.
- Python 3.8 or later.

## 🛠 Technologies Used
- **AWS Lambda**: Serverless computing service for running code.
- **RabbitMQ**: Message broker for handling communication between services.
- **Python**: Programming language used for writing the Lambda functions.
- **AWS Secrets Manager**: Securely stores and retrieves sensitive information.

## 🚀 Getting Started

Follow these steps to deploy and run the Lambda functions.

### 1️⃣ 📥 Clone the Repository
```sh
git clone <repository_url>
cd lambda-rabbitmq-integration
```

### 2️⃣ 🏗 Install Dependencies
```sh
pip install -r requirements.txt
```

### 3️⃣ 📦 Deploy the Lambda Functions
```sh
serverless deploy
```

### 4️⃣ ▶ Trigger the Functions
Invoke the deployed functions to send messages to RabbitMQ.
