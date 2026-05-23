provider "aws" {
  region = var.aws_region
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_security_group" "app_sg" {
  name        = "devops-app-sg"
  description = "Allow SSH and app traffic"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "App port"
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_key_pair" "devops_key" {
  key_name   = "devops-key"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCNYKJeoRvWlJXzhXGOZOiwVdA0Lz06YUqJXXcx3iyaO7NK2Dof027n7tKy/bcAz49ZUM3YXr/BjDZapPsFDjIBaTE+FNEVELV0CSXbF8oBYqXRPjZucCoZa2xX+ULS9XuQSGSWruRtOlx0sbj743CsK1xjaZtkHGMwaOGt8So4+SwclEUkNgsgT6caoWVaknz4lgRKVn5rRiypkSCwjrwKlMV09v9Ft6KYMe9bC8N09xl6NZB6iVdn/fBzoO5FEsM9fnjCGUke1sDlAOW1BbA0i+C3/iQpr4UOhxBQBOA4HC3Jf+ZDwzW0shpnu6Kp5J/zI0euh+3rbfTWngHFjp9H Muhammad Ismail@Muhammad21"
}

resource "aws_instance" "app_server" {
  ami                    = "ami-0c02fb55956c7d316"
  instance_type          = "t3.micro"
  key_name               = aws_key_pair.devops_key.key_name
  vpc_security_group_ids = [aws_security_group.app_sg.id]

  user_data = <<-SCRIPT
    #!/bin/bash
    yum update -y
    yum install -y docker
    service docker start
    usermod -aG docker ec2-user
    yum install -y aws-cli
  SCRIPT

  tags = {
    Name = "devops-app-server"
  }
}
