import os
import json
from typing import Optional, List, Dict
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

SKILLS = {
    # Read skills
    "system_health":   "Check if AWS services and EC2 instances are running normally",
    "recent_errors":   "Find recent errors, incidents, or outages in CloudWatch logs",
    "cloud_cost":      "Check cloud spending, costs, or billing information",
    "recent_changes":  "See what changed recently in infrastructure via CloudTrail",
    "service_metrics": "Get CPU, memory, or performance metrics for a specific service",
    "s3_status":       "List S3 buckets, check their region, and audit public access settings",
    "rds_status":      "Check RDS database health, engine type, and running status",
    "cost_optimization": "Audit idle resources, stopped instances, or unattached storage volumes to save costs",
    "lambda_status":     "Check AWS Lambda functions, runtimes, and status",
    "dynamodb_status":   "Check DynamoDB tables, item counts, and statuses",
    "sqs_status":        "Audit SQS queues, active backlogs, and message counts",
    "iam_status":        "Audit IAM user logins, security compliance, and MFA status",
    "ecs_status":        "Check ECS clusters, active container services, and task counts",
    # Action skills
    "action_restart":    "Restart a specific service or EC2 instance",
    "action_stop":       "Stop a specific service or EC2 instance",
    "action_scale":      "Scale up or increase capacity of a service or Auto Scaling Group",
    "action_alarm":      "Create a CloudWatch alert or alarm for a metric",
    "action_postmortem": "Generate a postmortem report for the current or recent incident",
    "action_create_instance": "Create or launch a new EC2 instance with specified name and type",
    "action_create_s3_bucket": "Create a new S3 bucket with secure defaults",
    "action_rds_snapshot": "Create a backup snapshot of an RDS database",
    "unknown": "Question cannot be answered with available AWS data"
}

ACTION_SKILLS = {
    "action_restart",
    "action_stop",
    "action_scale",
    "action_alarm",
    "action_postmortem",
    "action_create_instance",
    "action_create_s3_bucket",
    "action_rds_snapshot",
}


def _format_history(history: Optional[List[Dict[str, str]]]) -> str:
    if not history:
        return ""
    lines = []
    for msg in history[-6:]:
        role = msg.get("role", "")
        content = (msg.get("content") or "")[:300]
        if role not in ("user", "assistant") or not content:
            continue
        label = "User" if role == "user" else "Assistant"
        lines.append(f"{label}: {content}")
    if not lines:
        return ""
    return "Recent conversation:\n" + "\n".join(lines) + "\n\n"


def classify_intent(user_message: str, history: Optional[List[Dict[str, str]]] = None) -> dict:
    skills_list = "\n".join([f"- {k}: {v}" for k, v in SKILLS.items()])
    history_block = _format_history(history)

    prompt = f"""You are an AWS infrastructure assistant classifier.

{history_block}A user has asked: "{user_message}"

Available skills:
{skills_list}

Return ONLY valid JSON in this exact format:
{{
  "skill": "skill_name_here",
  "confidence": 0.95,
  "is_action": true,
  "extracted": {{
    "service_name": "name of specific service or ASG mentioned or null",
    "instance_id": "EC2 instance ID if mentioned or null",
    "time_range": "time period mentioned or null",
    "metric_name": "metric name if relevant or null",
    "threshold": "numeric threshold if mentioned or null",
    "scale_by": "number to scale by or null",
    "instance_type": "type of instance to create (e.g. t3.micro, t2.micro) or null",
    "instance_name": "Name tag for the new instance or null",
    "bucket_name": "Name of S3 bucket to create or audit or null",
    "db_instance_id": "RDS DB instance identifier to backup or check or null",
    "asg_name": "Auto Scaling Group name to scale or null",
    "desired_capacity": "Desired scaling target count or null"
  }},
  "thinking": "one sentence explaining why you chose this skill"
}}

Set is_action to true only for action_ skills.
Use conversation context for follow-up questions (e.g. "what about the payment service?" after a health check).
Return only JSON, no markdown."""

    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.1
        )
        text = response.choices[0].message.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()
        result = json.loads(text)
        result["is_action"] = result.get("skill", "") in ACTION_SKILLS
        return result
    except Exception as e:
        return {
            "skill": "unknown",
            "confidence": 0.0,
            "is_action": False,
            "extracted": {},
            "thinking": f"Classification failed: {str(e)}"
        }
