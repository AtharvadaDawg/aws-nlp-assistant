# AWS NLP Assistant

A conversational interface that lets non-technical users interact with AWS infrastructure in plain English. No console, no CLI, no dashboards — just ask questions and get human answers.

## Example questions
- "Is our system running fine right now?"
- "What broke last Tuesday night?"
- "How much did we spend on cloud this month?"
- "Which service had the most errors this week?"
- "What changed in our infrastructure recently?"
- "Restart the payment service" *(requires confirmation)*

## Stack
- Frontend: React + Tailwind CSS (chat UI)
- Backend: FastAPI (Python) — intent classification + AWS skill execution
- AI: LLM via OpenRouter — intent parsing + response translation
- AWS: boto3 — CloudWatch, Cost Explorer, CloudTrail, EC2

## Setup
1. Copy `backend/.env.example` to `backend/.env` and fill in your OpenRouter API key
2. `cd frontend && npm install && npm run dev`
3. `cd backend && pip install -r requirements.txt && python -m uvicorn main:app --reload --port 8002`

By default `AWS_MOCK=true` — all read queries use local JSON fixtures and write actions run in mock mode. Set `AWS_MOCK=false` and configure AWS credentials to execute real actions (still requires user confirmation in the UI).

## Architecture

```
User message
    → Intent classifier (LLM) — picks skill + extracts entities
    → Read skills  → mock/real AWS data → plain-English summary (LLM) → chat response
    → Action skills → proposal card → user confirms → action engine executes
```

**Read skills:** `system_health`, `recent_errors`, `cloud_cost`, `recent_changes`, `service_metrics`

**Action skills:** `action_restart`, `action_stop`, `action_scale`, `action_alarm`, `action_postmortem`

See `DESIGN.md` and `PRODUCT.md` for UI and product direction.
