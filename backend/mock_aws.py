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