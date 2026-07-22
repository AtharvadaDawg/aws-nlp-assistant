import os
import json
from typing import Optional, List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv
import mock_aws
import real_aws

load_dotenv()

client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

READ_FETCHERS = {
    "system_health": lambda _: real_aws.get_system_health(),
    "recent_errors": lambda _: real_aws.get_recent_errors(),
    "cloud_cost": lambda _: real_aws.get_cloud_cost(),
    "recent_changes": lambda _: real_aws.get_recent_changes(),
    "service_metrics": lambda extracted: real_aws.get_service_metrics(extracted.get("service_name")),
    "s3_status": lambda _: real_aws.get_s3_status(),
    "rds_status": lambda _: real_aws.get_rds_status(),
    "cost_optimization": lambda _: real_aws.get_cost_optimization(),
}

MOCK_FETCHERS = {
    "system_health": lambda _: mock_aws.get_system_health(),
    "recent_errors": lambda _: mock_aws.get_recent_errors(),
    "cloud_cost": lambda _: mock_aws.get_cloud_cost(),
    "recent_changes": lambda _: mock_aws.get_recent_changes(),
    "service_metrics": lambda extracted: mock_aws.get_service_metrics(extracted.get("service_name")),
    "s3_status": lambda _: mock_aws.get_s3_status(),
    "rds_status": lambda _: mock_aws.get_rds_status(),
    "cost_optimization": lambda _: mock_aws.get_cost_optimization(),
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


def translate_to_plain_english(
    question: str,
    skill: str,
    raw_data: dict,
    history: Optional[List[Dict[str, str]]] = None,
) -> str:
    history_block = _format_history(history)
    prompt = f"""You are an AWS infrastructure assistant helping a NON-TECHNICAL business user.

{history_block}The user asked: "{question}"

You queried AWS and got this data:
{json.dumps(raw_data, indent=2)}

Write a clear, friendly, plain-English response. Rules:
- Never use AWS jargon (no EC2, CloudWatch, IAM, etc.) unless unavoidable
- If you must use a technical term, explain it in brackets
- Be concise — 2-4 sentences max unless listing items
- If there are problems, be clear about their severity
- Use conversation context when the question is a follow-up (e.g. "what about that service?")
- End with one actionable suggestion if relevant
- Do NOT say "Based on the data" or "According to the API"
- Just answer naturally like a knowledgeable colleague would

Response:"""

    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"I was able to retrieve the data but had trouble summarising it. Error: {str(e)}"


def normalize_cost(raw: dict) -> dict:
    current = raw.get("current_month", {})
    last = raw.get("last_month", {})
    by_service = raw.get("by_service", [])
    chart_data = [
        {"name": (s.get("service") or "Unknown")[:14], "value": s.get("cost", 0.0)}
        for s in by_service
    ]
    return {
        "total_cost": current.get("total", 0),
        "period": "Current month",
        "currency": current.get("currency", "USD"),
        "last_month_total": last.get("total"),
        "by_service": by_service,
        "trend": raw.get("trend"),
        "change_pct": raw.get("change_pct"),
        "chart_data": chart_data,
    }


def normalize_errors(raw: dict) -> dict:
    errors = raw.get("recent_errors", [])
    return {
        "errors": errors,
        "total_errors": len(errors),
    }


def normalize_metrics(raw: dict, service_name: Optional[str] = None) -> dict:
    instances = raw.get("instances", [])
    chart_data = [
        {"name": (inst.get("name") or inst.get("id", "?"))[:14], "value": inst["cpu_avg"]}
        for inst in instances
        if inst.get("cpu_avg") is not None
    ]
    return {
        "instances": instances,
        "service_name": service_name,
        "chart_data": chart_data,
        "chart_type": "bar" if len(chart_data) > 1 else "line",
    }


def _fetch_raw(skill: str, extracted: dict, use_mock: bool) -> dict:
    fetchers = MOCK_FETCHERS if use_mock else READ_FETCHERS
    fetch = fetchers.get(skill)
    if not fetch:
        return {}
    return fetch(extracted)


def run_skill(
    skill: str,
    question: str,
    extracted: dict,
    history: Optional[List[Dict[str, str]]] = None,
) -> dict:
    from aws_client_factory import aws_credentials_context
    ctx = aws_credentials_context.get()
    has_dynamic_creds = ctx and ctx.get("access_key_id") and ctx.get("secret_access_key")
    use_mock = False if has_dynamic_creds else (os.getenv("AWS_MOCK", "true").lower() == "true")

    if skill == "system_health":
        raw = _fetch_raw(skill, extracted, use_mock)
        instances = raw.get("instances", [])
        running = [i for i in instances if i.get("state") == "running"]
        stopped = [i for i in instances if i.get("state") == "stopped"]
        answer = translate_to_plain_english(question, skill, raw, history)
        return {
            "skill_used": skill,
            "answer": answer,
            "data_type": "instances",
            "data": {
                "running_count": len(running),
                "stopped_count": len(stopped),
                "instances": instances,
            }
        }

    elif skill == "recent_errors":
        raw = _fetch_raw(skill, extracted, use_mock)
        data = normalize_errors(raw)
        answer = translate_to_plain_english(question, skill, raw, history)
        return {
            "skill_used": skill,
            "answer": answer,
            "data_type": "errors",
            "data": data,
        }

    elif skill == "cloud_cost":
        raw = _fetch_raw(skill, extracted, use_mock)
        data = normalize_cost(raw)
        answer = translate_to_plain_english(question, skill, raw, history)
        return {
            "skill_used": skill,
            "answer": answer,
            "data_type": "cost",
            "data": data,
        }

    elif skill == "recent_changes":
        raw = _fetch_raw(skill, extracted, use_mock)
        answer = translate_to_plain_english(question, skill, raw, history)
        return {
            "skill_used": skill,
            "answer": answer,
            "data_type": "changes",
            "data": {"events": raw.get("events", [])},
        }

    elif skill == "service_metrics":
        service = extracted.get("service_name")
        raw = _fetch_raw(skill, extracted, use_mock)
        data = normalize_metrics(raw, service)
        answer = translate_to_plain_english(question, skill, raw, history)
        return {
            "skill_used": skill,
            "answer": answer,
            "data_type": "metrics",
            "data": data,
        }

    elif skill == "s3_status":
        raw = _fetch_raw(skill, extracted, use_mock)
        answer = translate_to_plain_english(question, skill, raw, history)
        return {
            "skill_used": skill,
            "answer": answer,
            "data_type": "s3",
            "data": raw,
        }

    elif skill == "rds_status":
        raw = _fetch_raw(skill, extracted, use_mock)
        answer = translate_to_plain_english(question, skill, raw, history)
        return {
            "skill_used": skill,
            "answer": answer,
            "data_type": "rds",
            "data": raw,
        }

    elif skill == "cost_optimization":
        raw = _fetch_raw(skill, extracted, use_mock)
        answer = translate_to_plain_english(question, skill, raw, history)
        stopped_savings = sum(i.get("cost_est_savings", 0) for i in raw.get("stopped_instances", []))
        vol_savings = sum(v.get("cost_est_savings", 0) for v in raw.get("unattached_volumes", []))
        total_savings = round(stopped_savings + vol_savings, 2)
        return {
            "skill_used": skill,
            "answer": answer,
            "data_type": "savings",
            "data": {
                **raw,
                "total_est_savings": total_savings
            },
        }

    else:
        return {
            "skill_used": "unknown",
            "answer": "I'm not sure how to answer that with the AWS data I have access to. Try asking about system health, recent errors, cloud costs, recent changes, service performance, S3, RDS, or cost optimization.",
            "data_type": None,
            "data": {}
        }
