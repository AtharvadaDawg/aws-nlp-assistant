import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "mock-data")

def load(filename):
    with open(os.path.join(DATA_DIR, filename)) as f:
        return json.load(f)

def get_system_health():
    return load("ec2_instances.json")

def get_recent_errors():
    return load("cloudwatch_logs.json")

def get_cloud_cost():
    return load("cost_data.json")

def get_recent_changes():
    return load("cloudtrail_events.json")

def get_service_metrics(service_name=None):
    data = load("ec2_instances.json")
    if service_name:
        filtered = [i for i in data["instances"]
                    if service_name.lower() in i["name"].lower()]
        return {"instances": filtered if filtered else data["instances"]}
    return data

def get_s3_status():
    return {
        "buckets": [
            {"name": "company-assets-prod", "region": "ap-south-1", "is_public": False, "creation_date": "2024-03-12T10:00:00Z"},
            {"name": "user-profiles-prod", "region": "ap-south-1", "is_public": False, "creation_date": "2024-04-18T14:32:00Z"},
            {"name": "public-static-assets", "region": "ap-south-1", "is_public": True, "creation_date": "2025-01-05T08:22:00Z"},
        ]
    }

def get_rds_status():
    return {
        "db_instances": [
            {"id": "postgres-primary-prod", "engine": "postgres", "status": "available", "class": "db.t3.medium", "cpu_pct": 24.5},
            {"id": "mysql-analytics-read", "engine": "mysql", "status": "available", "class": "db.r6g.large", "cpu_pct": 12.0},
        ]
    }

def get_cost_optimization():
    return {
        "stopped_instances": [
            {"id": "i-0mno345pqr678", "name": "inventory-service-prod", "type": "t3.small", "cost_est_savings": 12.50}
        ],
        "unattached_volumes": [
            {"id": "vol-0abc123def456789a", "size_gb": 100, "type": "gp3", "cost_est_savings": 8.00},
            {"id": "vol-0def456abc789012b", "size_gb": 500, "type": "gp2", "cost_est_savings": 50.00},
        ]
    }

def get_lambda_status():
    return {
        "functions": [
            {"name": "postmortem-generator-prod", "runtime": "python3.11", "handler": "main.handler", "size_bytes": 1420500, "last_modified": "2026-07-20T12:00:00Z"},
            {"name": "user-signup-trigger", "runtime": "nodejs18.x", "handler": "index.handler", "size_bytes": 245000, "last_modified": "2026-06-15T08:34:00Z"},
            {"name": "stripe-webhook-handler", "runtime": "python3.10", "handler": "webhook.lambda_handler", "size_bytes": 1824000, "last_modified": "2026-07-22T04:12:00Z"}
        ]
    }

def get_dynamodb_status():
    return {
        "tables": [
            {"name": "users-table-prod", "status": "ACTIVE", "item_count": 14205, "size_bytes": 4820000},
            {"name": "orders-table-prod", "status": "ACTIVE", "item_count": 89431, "size_bytes": 62450000},
            {"name": "session-cache-temp", "status": "ACTIVE", "item_count": 340, "size_bytes": 84000}
        ]
    }

def get_sqs_status():
    return {
        "queues": [
            {"name": "payment-processing-queue", "visible_messages": 4, "invisible_messages": 2, "url": "https://sqs.ap-south-1.amazonaws.com/426818309914/payment-processing-queue"},
            {"name": "email-notification-dlq", "visible_messages": 12, "invisible_messages": 0, "url": "https://sqs.ap-south-1.amazonaws.com/426818309914/email-notification-dlq"},
            {"name": "order-fulfillment-pipeline", "visible_messages": 0, "invisible_messages": 0, "url": "https://sqs.ap-south-1.amazonaws.com/426818309914/order-fulfillment-pipeline"}
        ]
    }

def get_iam_status():
    return {
        "users": [
            {"name": "admin-principal", "mfa_active": True, "login_profile_exists": True, "created": "2024-01-10T12:00:00Z"},
            {"name": "nlp-user", "mfa_active": True, "login_profile_exists": False, "created": "2026-07-22T06:00:00Z"},
            {"name": "contractor-dev-temp", "mfa_active": False, "login_profile_exists": True, "created": "2026-05-14T08:00:00Z"}
        ]
    }

def get_ecs_status():
    return {
        "clusters": [
            {"name": "aws-nlp-assistant-cluster", "status": "ACTIVE", "services_count": 1, "running_tasks": 1, "pending_tasks": 0},
            {"name": "production-api-core", "status": "ACTIVE", "services_count": 4, "running_tasks": 8, "pending_tasks": 0},
            {"name": "staging-cluster-test", "status": "ACTIVE", "services_count": 2, "running_tasks": 2, "pending_tasks": 1}
        ]
    }