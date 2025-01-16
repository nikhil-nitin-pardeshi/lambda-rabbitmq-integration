# Lambda Function to Push Messages to RabbitMQ

This project contains two AWS Lambda functions written in Python that connect to RabbitMQ and push messages to a RabbitMQ queue. One function uses environment variables for configuration, and the other retrieves sensitive information from AWS Secrets Manager.

## Description

This project includes:
- A Lambda function that connects to RabbitMQ using environment variables.
- A Lambda function that connects to RabbitMQ using credentials stored in AWS Secrets Manager.

## Prerequisites

- AWS account with permissions to create and manage Lambda functions and Secrets Manager.
- RabbitMQ server.
- Python 3.8 or later.
