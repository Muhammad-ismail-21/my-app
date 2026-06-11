# Next-Generation DevOps & Deployment Engine

> Automated CI/CD Pipeline with Cloud-Native Deployment, Monitoring & Audit Logging

[![CI/CD Pipeline](https://github.com/Muhammad-ismail-21/my-app/actions/workflows/pipeline.yml/badge.svg)](https://github.com/Muhammad-ismail-21/my-app/actions/workflows/pipeline.yml)

## Live Dashboard

| Environment | URL | Branch |
|---|---|---|
| Production | http://YOUR_EC2_IP:5000 | main |
| Development | http://YOUR_EC2_IP:5001 | dev |

---

## What is this project?

This project is a fully automated cloud deployment system built using
industry-standard DevOps tools. It eliminates manual deployment entirely.
Every time a developer pushes code to GitHub, the system automatically
tests, packages, and deploys the application to AWS cloud — with zero
human intervention after the push.

The project includes a live DevOps Dashboard showing real-time system
status, server uptime, current deployed Git SHA, animated CI/CD pipeline
steps, tech stack, and deployment history pulled live from AWS S3.

---

## Problem Statement

Manual software deployment suffers from three core problems:

- **Slow** — Takes 20–30 minutes per deployment with 8–12 manual steps
- **Error-prone** — Human mistakes cause production outages and lost data
- **No visibility** — No record of what was deployed, when, or by whom

This project solves all three. Deployment time reduced to under 3 minutes.
Zero manual steps. Every deployment logged permanently to AWS S3.

---

## Architecture
Developer runs git push
↓
GitHub detects commit → triggers GitHub Actions
↓
Install dependencies → Configure AWS credentials
↓
flake8 code quality gate (bad code stops here)
↓
Build Docker image (tagged with Git SHA)
↓
Push image to AWS ECR
↓
SSH into EC2 → deploy new container
↓
Write deployment log to AWS S3
↓
Email alert via SNS if any step fails
↓
Live dashboard updated with new deployment entry

**Side services running 24/7:**
- CloudWatch monitors CPU and EC2 health
- SNS sends email alerts on alarms and failures
- S3 stores permanent deployment audit logs

---

## Tech Stack

| Tool | Purpose | Free Tier |
|---|---|---|
| GitHub | Source control and collaboration | Free |
| GitHub Actions | CI/CD pipeline automation | 2000 min/month free |
| Docker | Application containerization | Free |
| AWS ECR | Docker image registry | 500MB/month free |
| AWS EC2 t3.micro | Cloud hosting | 750 hrs/month free |
| Terraform | Infrastructure as Code | Free |
| AWS S3 | Deployment audit logs | 5GB/month free |
| AWS CloudWatch | Server monitoring | 10 alarms free |
| AWS SNS | Email alerting | 1000 emails/month free |
| Python Flask | Web app and dashboard | Free |
| flake8 | Code quality linter | Free |

**Estimated AWS cost: $0** (within free tier limits)

---

## Pipeline Stages

Every git push triggers these 11 automated steps:

| Step | Action | Purpose |
|---|---|---|
| 1 | Code pushed to GitHub | Triggers pipeline automatically |
| 2 | GitHub Actions starts | Fresh Ubuntu runner spins up |
| 3 | Install dependencies | Flask, boto3, flake8 installed |
| 4 | Configure AWS credentials | Loaded from GitHub Secrets securely |
| 5 | flake8 quality gate | Bad code blocked here — never deployed |
| 6 | Login to AWS ECR | Authenticates for image push |
| 7 | Build Docker image | Tagged with exact Git SHA |
| 8 | Push to AWS ECR | Stored permanently, any version redeployable |
| 9 | SSH deploy to EC2 | Old container stopped, new one started |
| 10 | Write log to AWS S3 | JSON audit record created |
| 11 | Email alert on failure | SNS notifies team with direct link |

---

## Environments

| Branch | Environment | Port | Trigger |
|---|---|---|---|
| `dev` | Development | 5001 | Push to dev branch |
| `main` | Production | 5000 | Push to main branch |

---

## 📁 Project Structure

```text
my-app/
├── app/
│   ├── app.py                 # Flask app with live DevOps dashboard
│   └── requirements.txt       # Python dependencies (Flask, boto3)
│
├── .github/
│   └── workflows/
│       └── pipeline.yml       # Complete 11-step CI/CD pipeline
│
├── terraform/
│   ├── main.tf                # EC2, security group, SSH key pair
│   ├── variables.tf           # AWS region variable
│   └── outputs.tf             # EC2 IP and app URL output
│
├── Dockerfile                 # Container build - python:3.11-slim base
├── .gitignore                 # Excludes terraform state and pycache
└── README.md                  # Project documentation
```

---

## Dashboard Features

The Flask application serves a live dashboard with real AWS data:

- **System Status** — Live pulse indicator (green = operational)
- **Server Uptime** — Time since last deployment
- **Git Commit SHA** — Exact version currently running in production
- **Live UTC Clock** — Updates every second
- **Animated Pipeline** — 11 steps light up sequentially on page load
- **Tech Stack Badges** — All tools displayed
- **Deployment History** — Last 5 deployments fetched live from S3
- **Auto-refresh** — Reloads every 30 seconds automatically

---

## AWS Infrastructure

Provisioned entirely via Terraform — no manual console clicks:

**EC2 t3.micro**
- Amazon Linux 2 AMI
- Docker installed via user_data startup script
- Docker auto-starts on every reboot
- IAM role attached for ECR and S3 access

**Security Group**
- Port 22 — SSH access for pipeline deployment
- Port 5000 — Production app
- Port 5001 — Development app

**IAM**
- Pipeline user with minimum required permissions
- EC2 role with ECR read and S3 read — no access keys on server
- All credentials stored in GitHub Secrets

---

## Monitoring & Alerting

| Alarm | Trigger | Action |
|---|---|---|
| EC2-High-CPU | CPU > 80% for 10 minutes | SNS email alert |
| EC2-Instance-Down | Status check fails 2 minutes | SNS email alert |
| Pipeline-Failure | Any GitHub Actions step fails | SNS email with link |
| Total-Bill-Alert | AWS charges exceed $1 | SNS email alert |

---

## Setup Guide

### Prerequisites

- Git installed
- AWS CLI v2 installed
- Terraform installed
- Docker Desktop installed
- AWS account (free tier)

### Step 1 — Clone the repository

```bash
git clone https://github.com/Muhammad-ismail-21/my-app.git
cd my-app
```

### Step 2 — Configure AWS CLI

```bash
aws configure
```

Enter:
- AWS Access Key ID — from IAM user credentials
- AWS Secret Access Key — from IAM user credentials
- Default region — us-east-1
- Default output format — json

### Step 3 — Provision infrastructure

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

Type `yes` when prompted. Note the EC2 IP from the output.

### Step 4 — Add GitHub Secrets

Go to repo → Settings → Secrets → Actions → add:

| Secret | Value |
|---|---|
| AWS_ACCESS_KEY_ID | Your IAM access key |
| AWS_SECRET_ACCESS_KEY | Your IAM secret key |
| AWS_ACCOUNT_ID | Your 12-digit AWS account ID |
| EC2_HOST | EC2 public IP from terraform output |
| EC2_SSH_KEY | Contents of ~/.ssh/devops-key |
| SNS_TOPIC_ARN | ARN of your SNS topic |
| S3_BUCKET | Your S3 bucket name |

### Step 5 — Deploy

Push any commit to trigger the pipeline:

```bash
git commit --allow-empty -m "ci: initial deployment"
git push origin main
```

Watch GitHub Actions — pipeline runs automatically.

---

## Team Workflow

### Daily workflow for team members

```bash
# Always start fresh
git checkout dev
git pull origin dev

# Create your feature branch
git checkout -b feature/your-name-change

# Make changes, then push
git add .
git commit -m "feat: describe your change"
git push origin feature/your-name-change

# Raise Pull Request on GitHub — feature branch → dev
```

### Admin merge process

```bash
# Merge to dev (triggers dev pipeline)
git checkout dev
git pull origin dev
git merge origin/feature/branch-name
git push origin dev

# After dev pipeline is green — merge to production
git checkout main
git merge dev
git push origin main
```

---

## EC2 Management

### Start EC2 before demo

```bash
aws ec2 start-instances --instance-ids YOUR_INSTANCE_ID --region us-east-1
```

### Get current IP after restart

```bash
aws ec2 describe-instances \
  --instance-ids YOUR_INSTANCE_ID \
  --query "Reservations[0].Instances[0].PublicIpAddress" \
  --output text \
  --region us-east-1
```

### Update EC2_HOST secret

After getting new IP — go to GitHub → Settings → Secrets → update EC2_HOST.
Then retrigger pipeline:

```bash
git commit --allow-empty -m "ci: retrigger after EC2 restart"
git push origin main
```

### Stop EC2 after demo (protect free tier)

```bash
aws ec2 stop-instances --instance-ids YOUR_INSTANCE_ID --region us-east-1
```

---

## Rollback

Any previous version can be redeployed using its Git SHA stored in AWS ECR.
Check deployment history on the dashboard for the SHA to roll back to.
Rollback takes under 30 seconds.

---

## Free Tier Safety

| Service | Free Limit | Our Usage | Safe |
|---|---|---|---|
| EC2 t3.micro | 750 hrs/month | Only when running | Yes |
| ECR storage | 500 MB/month | ~100MB images | Yes |
| S3 storage | 5 GB/month | Few KB JSON logs | Yes |
| CloudWatch alarms | 10 alarms free | 4 alarms | Yes |
| SNS emails | 1000/month free | Few emails | Yes |
| GitHub Actions | 2000 min/month | ~3 min per push | Yes |

Six billing alarms configured — email sent if charges exceed threshold on any service.

---

## Team

| Member | Role |
|---|---|
| Muhammad Ismail | Team Lead — Pipeline, AWS, Terraform, Dashboard |
| SK | Collaborator — Feature branch contributor |
| AB | Collaborator — Feature branch contributor |
| Basu | Collaborator — Feature branch contributor |

---

## Portfolio

[View full project portfolio](https://sites.google.com/kletech.ac.in/my-devops-portfolio/home)
