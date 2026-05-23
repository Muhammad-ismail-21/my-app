# Next-Generation DevOps & Deployment Engine

A production-grade CI/CD pipeline that automatically builds, tests, and deploys a containerized Flask application to AWS EC2 using GitHub Actions and Terraform.

## Architecture
GitHub → GitHub Actions → AWS ECR → AWS EC2
↓
CloudWatch + SNS Email Alerts
## Tech Stack

| Tool | Purpose |
|---|---|
| GitHub Actions | CI/CD pipeline automation |
| Docker | Application containerization |
| AWS ECR | Docker image registry |
| Terraform | Infrastructure as Code |
| AWS EC2 t3.micro | Application hosting (free tier) |
| AWS CloudWatch | Monitoring and alarms |
| AWS SNS | Email alerting |

## Environments

| Branch | Environment | URL |
|---|---|---|
| `dev` | Development | http://EC2_IP:5001 |
| `main` | Production | http://EC2_IP:5000 |

## Pipeline Flow

1. Push code to GitHub
2. GitHub Actions triggers automatically
3. Python lint check runs
4. Docker image built and pushed to ECR
5. Image deployed to EC2 via SSH
6. Email alert sent on any failure

## Infrastructure Setup

```bash
cd terraform
terraform init
terraform apply
```

## Local Development

```bash
pip install -r app/requirements.txt
python app/app.py
```

## Endpoints

- `GET /` — Home page
- `GET /health` — Health check

## Alerts

CloudWatch monitors:
- CPU utilization above 80%
- EC2 instance status check failure

Email notifications sent on pipeline failure via AWS SNS.
