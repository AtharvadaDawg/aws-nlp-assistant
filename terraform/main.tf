terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# ── PROVIDER ──────────────────────────────────────────────────────────────────

provider "aws" {
  region = var.aws_region
}

# ── VARIABLES ─────────────────────────────────────────────────────────────────

variable "aws_region" {
  type        = string
  default     = "ap-south-1"
  description = "AWS Region to deploy resources into"
}

variable "app_name" {
  type        = string
  default     = "aws-nlp-assistant"
  description = "Application name prefix for resource naming"
}

variable "openrouter_api_key" {
  type        = string
  sensitive   = true
  description = "API key for OpenRouter (Llama 3.1 intent classification and summary)"
}

variable "aws_mock" {
  type        = string
  default     = "false"
  description = "Toggle to query mock data instead of real AWS APIs ('true' or 'false')"
}

# ── NETWORKING (VPC) ─────────────────────────────────────────────────────────

# A custom VPC to host our assistant.
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.app_name}-vpc"
  }
}

# We need at least 2 public subnets in different AZs for the ALB.
# We hardcode suffixes 'a' and 'b' to avoid requiring the ec2:DescribeAvailabilityZones IAM permission.
resource "aws_subnet" "public_1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "${var.aws_region}a"

  tags = {
    Name = "${var.app_name}-public-subnet-1"
  }
}

resource "aws_subnet" "public_2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "${var.aws_region}b"

  tags = {
    Name = "${var.app_name}-public-subnet-2"
  }
}

# Internet Gateway for public internet access
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.app_name}-igw"
  }
}

# Route table to direct internet traffic through the IGW
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }

  tags = {
    Name = "${var.app_name}-public-rt"
  }
}

# Associate public subnets to route table
resource "aws_route_table_association" "public_1" {
  subnet_id      = aws_subnet.public_1.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_2" {
  subnet_id      = aws_subnet.public_2.id
  route_table_id = aws_route_table.public.id
}

# ── SECURITY GROUPS ──────────────────────────────────────────────────────────

# Security group for the Application Load Balancer (allows port 80 public traffic)
resource "aws_security_group" "alb" {
  name        = "${var.app_name}-alb-sg"
  description = "Allow inbound public HTTP access"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.app_name}-alb-sg"
  }
}

# Security group for the Fargate tasks (allows inbound port 8002 strictly from ALB)
resource "aws_security_group" "ecs_task" {
  name        = "${var.app_name}-task-sg"
  description = "Allow inbound port 8002 from ALB only"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 8002
    to_port         = 8002
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.app_name}-task-sg"
  }
}

# ── CONTAINER REGISTRY (ECR) ─────────────────────────────────────────────────

resource "aws_ecr_repository" "app" {
  name                 = var.app_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# ── IAM ROLES ────────────────────────────────────────────────────────────────

# ECS Execution Role (Required for ECS service agent to pull ECR images and send logs to CloudWatch)
resource "aws_iam_role" "ecs_execution_role" {
  name = "${var.app_name}-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = { Service = "ecs-tasks.amazonaws.com" }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ECS Task Role (Used by the application inside the container to make AWS API calls)
resource "aws_iam_role" "ecs_task_role" {
  name = "${var.app_name}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = { Service = "ecs-tasks.amazonaws.com" }
      }
    ]
  })
}

# Create a policy containing the permissions needed by AWS NLP Assistant and attach it to the Task Role
resource "aws_iam_policy" "nlp_assistant_policy" {
  name        = "${var.app_name}-nlp-policy"
  description = "Permissions for AWS NLP Assistant backend skills"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "AWSNLPAssistantPermissions"
        Effect   = "Allow"
        Action = [
          "ec2:DescribeInstances",
          "ec2:DescribeVolumes",
          "ec2:StartInstances",
          "ec2:StopInstances",
          "ec2:RunInstances",
          "ssm:GetParameter",
          "ce:GetCostAndUsage",
          "s3:ListAllMyBuckets",
          "s3:GetBucketLocation",
          "s3:GetBucketPolicyStatus",
          "s3:GetBucketAcl",
          "s3:CreateBucket",
          "s3:PutBucketPublicAccessBlock",
          "s3:PutEncryptionConfiguration",
          "rds:DescribeDBInstances",
          "rds:CreateDBSnapshot",
          "autoscaling:DescribeAutoScalingGroups",
          "autoscaling:UpdateAutoScalingGroup",
          "logs:DescribeLogGroups",
          "logs:FilterLogEvents",
          "lambda:ListFunctions",
          "dynamodb:ListTables",
          "dynamodb:DescribeTable",
          "sqs:ListQueues",
          "sqs:GetQueueAttributes",
          "iam:ListUsers",
          "iam:ListMFADevices",
          "iam:GetLoginProfile",
          "ecs:ListClusters",
          "ecs:DescribeClusters",
          "ecs:ListServices",
          "ecs:DescribeServices"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_nlp" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.nlp_assistant_policy.arn
}

# ── LOGGING ──────────────────────────────────────────────────────────────────

resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/${var.app_name}"
  retention_in_days = 7

  tags = {
    Name = "${var.app_name}-logs"
  }
}

# ── LOAD BALANCER (ALB) ──────────────────────────────────────────────────────

resource "aws_lb" "main" {
  name               = "${var.app_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = [aws_subnet.public_1.id, aws_subnet.public_2.id]

  tags = {
    Name = "${var.app_name}-alb"
  }
}

resource "aws_lb_target_group" "app" {
  name        = "${var.app_name}-tg"
  port        = 8002
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    path                = "/api/health"
    protocol            = "HTTP"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 3
    unhealthy_threshold = 3
  }

  tags = {
    Name = "${var.app_name}-target-group"
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

# ── ECS CLUSTER & SERVICE ────────────────────────────────────────────────────

resource "aws_ecs_cluster" "main" {
  name = "${var.app_name}-cluster"

  tags = {
    Name = "${var.app_name}-cluster"
  }
}

resource "aws_ecs_task_definition" "app" {
  family                   = var.app_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = var.app_name
      image     = "${aws_ecr_repository.app.repository_url}:latest"
      cpu       = 256
      memory    = 512
      essential = true
      portMappings = [
        {
          containerPort = 8002
          hostPort      = 8002
          protocol      = "tcp"
        }
      ]
      environment = [
        { name = "LLM_API_KEY", value = var.openrouter_api_key },
        { name = "AWS_MOCK", value = var.aws_mock },
        { name = "AWS_REGION", value = var.aws_region }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "main" {
  name            = "${var.app_name}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.public_1.id, aws_subnet.public_2.id]
    security_groups  = [aws_security_group.ecs_task.id]
    assign_public_ip = true # Required since tasks are in public subnet to pull ECR images and call API without NAT Gateway
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = var.app_name
    container_port   = 8002
  }

  # Prevent service creation failure before image exists in ECR.
  # Note: A placeholder image is not needed if the image is pushed first, which is standard.
  # We instruct the user to build and push the image before initiating tf apply.
  depends_on = [
    aws_lb_listener.http
  ]

  tags = {
    Name = "${var.app_name}-service"
  }
}

# ── OUTPUTS ──────────────────────────────────────────────────────────────────

output "ecr_repository_url" {
  value       = aws_ecr_repository.app.repository_url
  description = "The URL of the ECR repository to push the Docker image to."
}

output "application_url" {
  value       = "http://${aws_lb.main.dns_name}"
  description = "Public URL of the AWS NLP Assistant."
}
