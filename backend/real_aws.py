import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

REGION = os.getenv("AWS_REGION", "ap-south-1")


def _ec2():
    return boto3.client("ec2", region_name=REGION)


def _cloudwatch():
    return boto3.client("cloudwatch", region_name=REGION)


def _logs():
    return boto3.client("logs", region_name=REGION)


def _cost_explorer():
    return boto3.client("ce", region_name="us-east-1")


def _cloudtrail():
    return boto3.client("cloudtrail", region_name=REGION)


def _instance_name(tags: list) -> str:
    for tag in tags or []:
        if tag.get("Key") == "Name":
            return tag["Value"]
    return ""


def _map_instance(inst: dict, cpu_avg: Optional[float] = None) -> dict:
    return {
        "id": inst["InstanceId"],
        "name": _instance_name(inst.get("Tags")) or inst["InstanceId"],
        "type": inst["InstanceType"],
        "state": inst["State"]["Name"].lower(),
        "cpu_avg": cpu_avg,
        "region": REGION,
    }


def _cpu_avg(instance_id: str, hours: int = 1) -> Optional[float]:
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=hours)
    try:
        resp = _cloudwatch().get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName="CPUUtilization",
            Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
            StartTime=start,
            EndTime=end,
            Period=3600,
            Statistics=["Average"],
        )
        datapoints = resp.get("Datapoints", [])
        if not datapoints:
            return None
        latest = max(datapoints, key=lambda d: d["Timestamp"])
        return round(latest["Average"], 1)
    except ClientError:
        return None


def _log_groups() -> list:
    configured = os.getenv("CLOUDWATCH_LOG_GROUPS", "").strip()
    if configured:
        return [g.strip() for g in configured.split(",") if g.strip()]
    try:
        resp = _logs().describe_log_groups(limit=5)
        return [g["logGroupName"] for g in resp.get("logGroups", [])]
    except ClientError:
        return []


def _parse_cost(result: dict) -> Tuple[float, str]:
    groups = result.get("ResultsByTime", [])
    if not groups:
        return 0.0, "USD"
    total = groups[0].get("Total", {}).get("UnblendedCost", {})
    amount = float(total.get("Amount", 0))
    currency = total.get("Unit", "USD")
    return amount, currency


def get_system_health() -> dict:
    try:
        resp = _ec2().describe_instances()
        instances = []
        for reservation in resp.get("Reservations", []):
            for inst in reservation.get("Instances", []):
                state = inst["State"]["Name"]
                if state in ("terminated", "shutting-down"):
                    continue
                cpu = _cpu_avg(inst["InstanceId"])
                instances.append(_map_instance(inst, cpu))
        return {"instances": instances}
    except ClientError as e:
        return {"instances": [], "error": str(e)}


def get_recent_errors() -> dict:
    groups = _log_groups()
    if not groups:
        return {"recent_errors": [], "log_groups": [], "error": "No CloudWatch log groups found"}

    start_ms = int((datetime.now(timezone.utc) - timedelta(hours=24)).timestamp() * 1000)
    errors = []

    for group in groups[:5]:
        try:
            resp = _logs().filter_log_events(
                logGroupName=group,
                startTime=start_ms,
                filterPattern="?ERROR ?Error ?FATAL ?Fatal ?Exception",
                limit=20,
            )
            service = group.rstrip("/").split("/")[-1]
            for event in resp.get("events", []):
                ts = datetime.fromtimestamp(event["timestamp"] / 1000, tz=timezone.utc)
                errors.append({
                    "time": ts.isoformat().replace("+00:00", "Z"),
                    "service": service,
                    "level": "ERROR",
                    "message": event["message"][:200],
                })
        except ClientError:
            continue

    errors.sort(key=lambda e: e["time"], reverse=True)
    return {"log_groups": groups, "recent_errors": errors[:20]}


def get_cloud_cost() -> dict:
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_end = month_start - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)

    fmt = "%Y-%m-%d"
    start_str = month_start.strftime(fmt)
    end_str = now.strftime(fmt)
    if start_str == end_str:
        end_str = (now + timedelta(days=1)).strftime(fmt)

    try:
        ce = _cost_explorer()
        current_resp = ce.get_cost_and_usage(
            TimePeriod={"Start": start_str, "End": end_str},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
        )
        last_resp = ce.get_cost_and_usage(
            TimePeriod={"Start": last_month_start.strftime(fmt), "End": month_start.strftime(fmt)},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
        )
        by_service_resp = ce.get_cost_and_usage(
            TimePeriod={"Start": start_str, "End": end_str},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
            GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
        )

        current_total, currency = _parse_cost(current_resp)
        last_total, _ = _parse_cost(last_resp)

        by_service = []
        for group in by_service_resp.get("ResultsByTime", []):
            for item in group.get("Groups", []):
                cost = float(item["Metrics"]["UnblendedCost"]["Amount"])
                if cost > 0:
                    by_service.append({
                        "service": item["Keys"][0],
                        "cost": round(cost, 2),
                    })
        by_service.sort(key=lambda x: x["cost"], reverse=True)

        change_pct = None
        trend = "flat"
        if last_total > 0:
            change_pct = round(((current_total - last_total) / last_total) * 100, 2)
            trend = "up" if change_pct > 0 else "down" if change_pct < 0 else "flat"

        return {
            "current_month": {"total": round(current_total, 2), "currency": currency},
            "last_month": {"total": round(last_total, 2), "currency": currency},
            "by_service": by_service[:10],
            "trend": trend,
            "change_pct": change_pct,
        }
    except ClientError as e:
        return {
            "current_month": {"total": 0, "currency": "USD"},
            "last_month": {"total": 0, "currency": "USD"},
            "by_service": [],
            "error": str(e),
        }


def get_recent_changes() -> dict:
    start = datetime.now(timezone.utc) - timedelta(days=7)
    try:
        resp = _cloudtrail().lookup_events(StartTime=start, MaxResults=20)
        events = []
        for evt in resp.get("Events", []):
            resources = evt.get("Resources") or []
            resource_name = resources[0].get("ResourceName", "") if resources else ""
            events.append({
                "time": evt["EventTime"].astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
                "user": evt.get("Username") or "unknown",
                "action": evt.get("EventName", ""),
                "resource": resource_name,
                "region": REGION,
            })
        return {"events": events}
    except ClientError as e:
        return {"events": [], "error": str(e)}


def get_service_metrics(service_name: Optional[str] = None) -> dict:
    raw = get_system_health()
    instances = raw.get("instances", [])
    if service_name:
        needle = service_name.lower()
        filtered = [i for i in instances if needle in i["name"].lower()]
        instances = filtered if filtered else instances
    return {"instances": instances}


def get_s3_status() -> dict:
    try:
        s3 = boto3.client("s3")
        resp = s3.list_buckets()
        buckets = []
        for b in resp.get("Buckets", []):
            name = b["Name"]
            try:
                loc = s3.get_bucket_location(Bucket=name)
                region = loc.get("LocationConstraint") or "us-east-1"
                if region == "EU":
                    region = "eu-west-1"
            except ClientError:
                region = REGION

            is_public = False
            try:
                pub_status = s3.get_bucket_policy_status(Bucket=name)
                is_public = pub_status.get("PolicyStatus", {}).get("IsPublic", False)
            except ClientError:
                pass

            buckets.append({
                "name": name,
                "region": region,
                "is_public": is_public,
                "creation_date": b["CreationDate"].isoformat().replace("+00:00", "Z") if b.get("CreationDate") else "",
            })
        return {"buckets": buckets}
    except ClientError as e:
        return {"buckets": [], "error": str(e)}


def get_rds_status() -> dict:
    try:
        rds = boto3.client("rds", region_name=REGION)
        resp = rds.describe_db_instances()
        db_instances = []
        for db in resp.get("DBInstances", []):
            db_instances.append({
                "id": db["DBInstanceIdentifier"],
                "engine": db["Engine"],
                "status": db["DBInstanceStatus"],
                "class": db["DBInstanceClass"],
                "cpu_pct": None,
            })
        return {"db_instances": db_instances}
    except ClientError as e:
        return {"db_instances": [], "error": str(e)}


def get_cost_optimization() -> dict:
    try:
        ec2 = boto3.client("ec2", region_name=REGION)
        instances_resp = ec2.describe_instances(
            Filters=[{"Name": "instance-state-name", "Values": ["stopped"]}]
        )
        stopped = []
        for reservation in instances_resp.get("Reservations", []):
            for inst in reservation.get("Instances", []):
                name = _instance_name(inst.get("Tags")) or inst["InstanceId"]
                stopped.append({
                    "id": inst["InstanceId"],
                    "name": name,
                    "type": inst["InstanceType"],
                    "cost_est_savings": 15.00,
                })

        volumes_resp = ec2.describe_volumes(
            Filters=[{"Name": "status", "Values": ["available"]}]
        )
        unattached = []
        for vol in volumes_resp.get("Volumes", []):
            size = vol["Size"]
            cost = round(size * 0.08, 2)
            unattached.append({
                "id": vol["VolumeId"],
                "size_gb": size,
                "type": vol["VolumeType"],
                "cost_est_savings": cost,
            })

        return {
            "stopped_instances": stopped,
            "unattached_volumes": unattached
        }
    except ClientError as e:
        return {
            "stopped_instances": [],
            "unattached_volumes": [],
            "error": str(e)
        }
