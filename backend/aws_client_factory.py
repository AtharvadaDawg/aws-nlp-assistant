import os
import contextvars
import boto3
from typing import Optional

# Define a ContextVar to store current request's dynamic credentials in a thread-safe / async-safe manner.
aws_credentials_context = contextvars.ContextVar("aws_credentials", default=None)

def get_aws_client(service_name: str, region_name: Optional[str] = None):
    ctx = aws_credentials_context.get()
    kwargs = {}
    
    # 1. Check if we have credentials in the current request context
    if ctx and ctx.get("access_key_id") and ctx.get("secret_access_key"):
        kwargs["aws_access_key_id"] = ctx["access_key_id"]
        kwargs["aws_secret_access_key"] = ctx["secret_access_key"]
        
        # Region priority: function parameter region_name > context region > default env region
        req_region = region_name or ctx.get("region") or os.getenv("AWS_REGION", "ap-south-1")
        kwargs["region_name"] = req_region
    else:
        # 2. Fallback to default credentials from local environment
        kwargs["region_name"] = region_name or os.getenv("AWS_REGION", "ap-south-1")
    
    # Special constraint: Cost Explorer (ce) must always run in us-east-1
    if service_name == "ce":
        kwargs["region_name"] = "us-east-1"
        
    return boto3.client(service_name, **kwargs)
