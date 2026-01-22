from flask import Blueprint, request, session
import openai
import os
from logic.ai_helpers import build_task_prompt, parse_openai_response
from limiter_config import limiter
from openai import OpenAI

ai_bp = Blueprint("ai", __name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@ai_bp.route("/recommend", methods=["POST"])
@limiter.limit("10 per hour")
def recommend():
    if "username" not in session:
        return {"error": "Unauthorized"}, 401

    data = request.get_json()
    description = data.get("description", "")
    if not description:
        return {"error": "Missing task description"}, 400

    prompt = build_task_prompt(description)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        result = parse_openai_response(response)
        return {"recommendation": result}, 200
    except Exception as e:
        return {"error": str(e)}, 500
