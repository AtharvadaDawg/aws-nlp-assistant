import os
import json
import boto3
from datetime import datetime
from dotenv import load_dotenv
from aws_client_factory import get_aws_client

load_dotenv()

MOCK_MODE = os.getenv("AWS_MOCK", "true").lower() == "true"
REGION = os.getenv("AWS_REGION", "ap-south-1")

def get_active_region() -> str:
    from aws_client_factory import aws_credentials_context
    ctx = aws_credentials_context.get()
    if ctx and ctx.get("region"):
        return ctx["region"]
    return REGION

# Instance name → ID mapping from mock data
MOCK_INSTANCE_MAP = {
    "payment-service-prod":   "i-0abc123def456",
    "payment":                "i-0abc123def456",
    "auth-service-prod":      "i-0def456abc789",
    "auth":                   "i-0def456abc789",
    "order-service-prod":     "i-0ghi789jkl012",
    "order":                  "i-0ghi789jkl012",
    "database-primary":       "i-0jkl012mno345",
    "database":               "i-0jkl012mno345",
    "inventory-service-prod": "i-0mno345pqr678",
    "inventory":              "i-0mno345pqr678",
}

def resolve_instance(service_name: str, run_real: bool = False) -> dict:
    if not service_name:
        return {"error": "No service name provided"}
    
    name = service_name.lower().replace(" ", "-")
    
    if run_real:
        try:
            ec2 = get_aws_client("ec2")
            # 1. Direct instance ID resolution
            if service_name.startswith("i-") and len(service_name) in (10, 19):
                resp = ec2.describe_instances(InstanceIds=[service_name])
                for reservation in resp.get("Reservations", []):
                    for inst in reservation.get("Instances", []):
                        inst_name = service_name
                        for tag in inst.get("Tags", []):
                            if tag.get("Key") == "Name":
                                inst_name = tag.get("Value")
                        return {"instance_id": service_name, "name": inst_name}
            
            # 2. Lookup by Name Tag substring match
            resp = ec2.describe_instances()
            for reservation in resp.get("Reservations", []):
                for inst in reservation.get("Instances", []):
                    inst_id = inst["InstanceId"]
                    inst_name = ""
                    for tag in inst.get("Tags", []):
                        if tag.get("Key") == "Name":
                            inst_name = tag.get("Value")
                    
                    if inst_name and (name in inst_name.lower() or inst_name.lower() in name):
                        return {"instance_id": inst_id, "name": inst_name}
                    
                    if name in inst_id.lower() or inst_id.lower() in name:
                        return {"instance_id": inst_id, "name": inst_name or inst_id}
        except Exception as e:
            print(f"[DEBUG] AWS instance resolution failed: {str(e)}")
            
    # Mock fallback
    for key, iid in MOCK_INSTANCE_MAP.items():
        if key in name or name in key:
            return {"instance_id": iid, "name": key}
            
    return {"error": f"Could not find instance for '{service_name}'"}

# ── Mock actions ──────────────────────────────────────────────────────────────

def mock_restart(service_name: str) -> dict:
    resolved = resolve_instance(service_name)
    if "error" in resolved:
        return {"success": False, "message": resolved["error"]}
    return {
        "success": True,
        "action": "restart",
        "instance_id": resolved["instance_id"],
        "service_name": resolved["name"],
        "message": f"[MOCK] {resolved['name']} ({resolved['instance_id']}) stopped and restarted successfully. Service is back online.",
        "duration_seconds": 28
    }

def mock_stop(service_name: str) -> dict:
    resolved = resolve_instance(service_name)
    if "error" in resolved:
        return {"success": False, "message": resolved["error"]}
    return {
        "success": True,
        "action": "stop",
        "instance_id": resolved["instance_id"],
        "service_name": resolved["name"],
        "message": f"[MOCK] {resolved['name']} ({resolved['instance_id']}) stopped successfully.",
    }

def mock_scale(service_name: str, scale_by: int = 1) -> dict:
    return {
        "success": True,
        "action": "scale",
        "service_name": service_name or "order-service",
        "previous_capacity": 2,
        "new_capacity": 2 + scale_by,
        "message": f"[MOCK] Scaled {service_name or 'order-service'} from 2 to {2 + scale_by} instances.",
    }

def mock_alarm(service_name: str, metric: str = "CPUUtilization", threshold: float = 80.0) -> dict:
    return {
        "success": True,
        "action": "create_alarm",
        "alarm_name": f"{service_name or 'service'}-{metric}-alarm",
        "metric": metric,
        "threshold": threshold,
        "message": f"[MOCK] CloudWatch alarm created: alert when {metric} > {threshold}% for {service_name or 'the service'}.",
    }

def mock_create_instance(instance_name: str, instance_type: str = "t3.micro") -> dict:
    iid = f"i-0mock{hash(instance_name) & 0xffffffff:08x}"
    return {
        "success": True,
        "action": "create_instance",
        "instance_id": iid,
        "instance_name": instance_name,
        "instance_type": instance_type,
        "message": f"[MOCK] Launched new {instance_type} instance '{instance_name}' ({iid}) successfully. Instance state: pending.",
    }

def mock_create_s3_bucket(bucket_name: str) -> dict:
    return {
        "success": True,
        "action": "create_s3_bucket",
        "bucket_name": bucket_name,
        "message": f"[MOCK] Created secure S3 bucket '{bucket_name}' in {REGION} with default encryption and public access block active.",
    }

def mock_rds_snapshot(db_instance_id: str) -> dict:
    snapshot_id = f"{db_instance_id}-snap-mock"
    return {
        "success": True,
        "action": "rds_snapshot",
        "db_instance_id": db_instance_id,
        "snapshot_id": snapshot_id,
        "message": f"[MOCK] Initiated database snapshot '{snapshot_id}' for database '{db_instance_id}'.",
    }

def mock_scale_asg(asg_name: str, desired_capacity: int = 0, scale_by: int = 1) -> dict:
    current = 2
    target = desired_capacity if desired_capacity > 0 else (current + scale_by)
    return {
        "success": True,
        "action": "scale_asg",
        "asg_name": asg_name,
        "previous_capacity": current,
        "new_capacity": target,
        "message": f"[MOCK] Scaled Auto Scaling Group '{asg_name}' from {current} to {target} instances.",
    }

# ── Real AWS actions ──────────────────────────────────────────────────────────

def real_restart(instance_id: str, service_name: str) -> dict:
    try:
        ec2 = get_aws_client("ec2")
        ec2.stop_instances(InstanceIds=[instance_id])
        waiter = ec2.get_waiter("instance_stopped")
        waiter.wait(InstanceIds=[instance_id])
        ec2.start_instances(InstanceIds=[instance_id])
        return {
            "success": True,
            "action": "restart",
            "instance_id": instance_id,
            "service_name": service_name,
            "message": f"✅ {service_name} ({instance_id}) restarted successfully on AWS.",
        }
    except Exception as e:
        return {"success": False, "message": f"AWS error: {str(e)}"}

def real_stop(instance_id: str, service_name: str) -> dict:
    try:
        ec2 = get_aws_client("ec2")
        ec2.stop_instances(InstanceIds=[instance_id])
        return {
            "success": True,
            "action": "stop",
            "instance_id": instance_id,
            "service_name": service_name,
            "message": f"✅ {service_name} ({instance_id}) stopped on AWS.",
        }
    except Exception as e:
        return {"success": False, "message": f"AWS error: {str(e)}"}

def real_alarm(service_name: str, metric: str = "CPUUtilization", threshold: float = 80.0) -> dict:
    try:
        cw = get_aws_client("cloudwatch")
        alarm_name = f"{service_name}-{metric}-alarm"
        cw.put_metric_alarm(
            AlarmName=alarm_name,
            MetricName=metric,
            Namespace="AWS/EC2",
            Statistic="Average",
            Period=300,
            EvaluationPeriods=2,
            Threshold=threshold,
            ComparisonOperator="GreaterThanThreshold",
        )
        return {
            "success": True,
            "action": "create_alarm",
            "alarm_name": alarm_name,
            "message": f"✅ CloudWatch alarm '{alarm_name}' created on AWS.",
        }
    except Exception as e:
        return {"success": False, "message": f"AWS error: {str(e)}"}

def real_create_instance(instance_name: str, instance_type: str = "t3.micro") -> dict:
    try:
        ssm = get_aws_client("ssm")
        param = ssm.get_parameter(Name="/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2")
        ami_id = param["Parameter"]["Value"]
    except Exception:
        ami_id = "ami-0522ab6e1ddcc7055"

    try:
        ec2 = get_aws_client("ec2")
        resp = ec2.run_instances(
            ImageId=ami_id,
            InstanceType=instance_type,
            MinCount=1,
            MaxCount=1,
            TagSpecifications=[
                {
                    "ResourceType": "instance",
                    "Tags": [
                        {"Key": "Name", "Value": instance_name}
                    ]
                }
            ]
        )
        inst = resp["Instances"][0]
        iid = inst["InstanceId"]
        return {
            "success": True,
            "action": "create_instance",
            "instance_id": iid,
            "instance_name": instance_name,
            "instance_type": instance_type,
            "message": f"✅ Launched new {instance_type} instance '{instance_name}' ({iid}) successfully on AWS.",
        }
    except Exception as e:
        return {"success": False, "message": f"AWS error: {str(e)}"}

def real_create_s3_bucket(bucket_name: str) -> dict:
    try:
        active_region = get_active_region()
        s3 = get_aws_client("s3")
        if active_region == "us-east-1":
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": active_region}
            )

        s3.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                "BlockPublicAcls": True,
                "IgnorePublicAcls": True,
                "BlockPublicPolicy": True,
                "RestrictPublicBuckets": True
            }
        )

        s3.put_bucket_encryption(
            Bucket=bucket_name,
            ServerSideEncryptionConfiguration={
                "Rules": [
                    {
                        "ApplyServerSideEncryptionByDefault": {
                            "SSEAlgorithm": "AES256"
                        }
                    }
                ]
            }
        )

        return {
            "success": True,
            "action": "create_s3_bucket",
            "bucket_name": bucket_name,
            "message": f"✅ Created secure S3 bucket '{bucket_name}' in {active_region} with default encryption and public access blocks active.",
        }
    except Exception as e:
        return {"success": False, "message": f"AWS error: {str(e)}"}

def real_rds_snapshot(db_instance_id: str) -> dict:
    try:
        rds = get_aws_client("rds")
        snapshot_id = f"{db_instance_id}-snap-{int(datetime.now().timestamp())}"
        rds.create_db_snapshot(
            DBSnapshotIdentifier=snapshot_id,
            DBInstanceIdentifier=db_instance_id
        )
        return {
            "success": True,
            "action": "rds_snapshot",
            "db_instance_id": db_instance_id,
            "snapshot_id": snapshot_id,
            "message": f"✅ Initiated database snapshot '{snapshot_id}' for database '{db_instance_id}'. State: creating.",
        }
    except Exception as e:
        return {"success": False, "message": f"AWS error: {str(e)}"}

def real_scale_asg(asg_name: str, desired_capacity: int = 0, scale_by: int = 1) -> dict:
    try:
        asg = get_aws_client("autoscaling")
        resp = asg.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])
        groups = resp.get("AutoScalingGroups", [])
        if not groups:
            return {"success": False, "message": f"Auto Scaling Group '{asg_name}' not found."}
        
        current_capacity = groups[0]["DesiredCapacity"]
        target_capacity = desired_capacity if desired_capacity > 0 else (current_capacity + scale_by)
        
        asg.update_auto_scaling_group(
            AutoScalingGroupName=asg_name,
            DesiredCapacity=target_capacity
        )
        return {
            "success": True,
            "action": "scale_asg",
            "asg_name": asg_name,
            "previous_capacity": current_capacity,
            "new_capacity": target_capacity,
            "message": f"✅ Successfully scaled Auto Scaling Group '{asg_name}' from {current_capacity} to {target_capacity} desired instances.",
        }
    except Exception as e:
        return {"success": False, "message": f"AWS error: {str(e)}"}

# ── Dispatcher ────────────────────────────────────────────────────────────────

def build_proposal(skill: str, extracted: dict) -> dict:
    service = extracted.get("service_name") or "the service"
    
    from aws_client_factory import aws_credentials_context
    ctx = aws_credentials_context.get()
    has_dynamic_creds = ctx and ctx.get("access_key_id") and ctx.get("secret_access_key")
    is_mock = False if has_dynamic_creds else MOCK_MODE
    active_region = get_active_region()
    mode = "MOCK" if is_mock else "LIVE AWS"
    
    resolved = resolve_instance(service, run_real=not is_mock)
    iid = extracted.get("instance_id") or resolved.get("instance_id", "unknown")

    proposals = {
        "action_restart": {
            "title": f"Restart {service}",
            "description": f"Stop and restart {service} ({iid}) in {active_region}. Expect ~30 seconds of downtime.",
            "risk": "medium",
            "mode": mode
        },
        "action_stop": {
            "title": f"Stop {service}",
            "description": f"Stop {service} ({iid}) in {active_region}. The service will be unavailable until manually restarted.",
            "risk": "high",
            "mode": mode
        },
        "action_scale": {
            "title": f"Scale Auto Scaling Group",
            "description": f"Scale Auto Scaling Group '{extracted.get('asg_name') or service}' to {extracted.get('desired_capacity') or 'desired capacity + ' + str(extracted.get('scale_by', 1))} instances in {active_region}.",
            "risk": "low",
            "mode": mode
        },
        "action_alarm": {
            "title": f"Create CloudWatch alarm",
            "description": f"Alert when {extracted.get('metric_name', 'CPU')} exceeds {extracted.get('threshold', 80)}% for {service}.",
            "risk": "low",
            "mode": mode
        },
        "action_create_instance": {
            "title": "Create EC2 Instance",
            "description": f"Launch a new {extracted.get('instance_type') or 't3.micro'} instance named '{extracted.get('instance_name') or extracted.get('service_name') or 'new-instance'}' in {active_region}.",
            "risk": "medium",
            "mode": mode
        },
        "action_create_s3_bucket": {
            "title": "Create S3 Bucket",
            "description": f"Create a new private S3 bucket named '{extracted.get('bucket_name') or 'new-bucket'}' in {active_region} with default encryption and public access blocks active.",
            "risk": "low",
            "mode": mode
        },
        "action_rds_snapshot": {
            "title": "Create RDS DB Snapshot",
            "description": f"Create a manual backup snapshot for RDS database instance '{extracted.get('db_instance_id') or 'database-primary'}' in {active_region}.",
            "risk": "low",
            "mode": mode
        },
        "action_postmortem": {
            "title": "Generate postmortem",
            "description": "Call the Postmortem Generator with recent error logs to produce a full incident report.",
            "risk": "none",
            "mode": mode
        },
    }
    return proposals.get(skill, {"title": "Unknown action", "description": "", "risk": "unknown", "mode": mode})

def execute_action(skill: str, extracted: dict, use_real_aws: bool = False) -> dict:
    service = extracted.get("service_name") or "the service"
    
    from aws_client_factory import aws_credentials_context
    ctx = aws_credentials_context.get()
    has_dynamic_creds = ctx and ctx.get("access_key_id") and ctx.get("secret_access_key")
    is_mock = False if has_dynamic_creds else MOCK_MODE
    run_real = True if has_dynamic_creds else use_real_aws

    resolved = resolve_instance(service, run_real=run_real and not is_mock)
    
    if "error" in resolved and skill in ("action_restart", "action_stop"):
        return {"success": False, "message": resolved["error"]}

    iid = resolved.get("instance_id", "unknown")

    if skill == "action_restart":
        if run_real and not is_mock:
            return real_restart(iid, service)
        return mock_restart(service)

    elif skill == "action_stop":
        if run_real and not is_mock:
            return real_stop(iid, service)
        return mock_stop(service)

    elif skill == "action_scale":
        asg_name = extracted.get("asg_name") or service or "order-service"
        desired_capacity = int(extracted.get("desired_capacity") or 0)
        scale_by = int(extracted.get("scale_by") or 1)
        if run_real and not is_mock:
            return real_scale_asg(asg_name, desired_capacity, scale_by)
        return mock_scale_asg(asg_name, desired_capacity, scale_by)

    elif skill == "action_alarm":
        metric = extracted.get("metric_name") or "CPUUtilization"
        threshold = float(extracted.get("threshold") or 80.0)
        if run_real and not is_mock:
            return real_alarm(service, metric, threshold)
        return mock_alarm(service, metric, threshold)

    elif skill == "action_create_instance":
        instance_name = extracted.get("instance_name") or service or "new-instance"
        instance_type = extracted.get("instance_type") or "t3.micro"
        if run_real and not is_mock:
            return real_create_instance(instance_name, instance_type)
        return mock_create_instance(instance_name, instance_type)

    elif skill == "action_create_s3_bucket":
        bucket_name = extracted.get("bucket_name") or "new-bucket"
        if run_real and not is_mock:
            return real_create_s3_bucket(bucket_name)
        return mock_create_s3_bucket(bucket_name)

    elif skill == "action_rds_snapshot":
        db_instance_id = extracted.get("db_instance_id") or "database-primary"
        if run_real and not is_mock:
            return real_rds_snapshot(db_instance_id)
        return mock_rds_snapshot(db_instance_id)

    elif skill == "action_postmortem":
        return {
            "success": True,
            "action": "postmortem",
            "message": "Postmortem generation triggered. Open the Postmortem Generator with recent CloudWatch logs to proceed.",
        }

    return {"success": False, "message": "Unknown action"}