### task_routes.py
from flask import Blueprint, request, session
from db import mongo
from bson import ObjectId
from datetime import datetime
from logic.validators import validate_user_input
from logic.task_utills import is_task_overdue
from logic.telegram_notifier import send_telegram_message
from logic.ai_helpers import parse_openai_response
import openai
import os
import logging
from flask_cors import cross_origin
from datetime import datetime

openai.api_key = os.getenv("OPENAI_API_KEY")

task_bp = Blueprint("tasks", __name__)

def serialize_task(task):
    task["_id"] = str(task["_id"])
    return task

@task_bp.route("/", methods=["GET", "OPTIONS"])
@cross_origin(supports_credentials=True)
def get_tasks():
    username = session.get("username")
    if not username:
        return {"error": "Unauthorized"}, 401

    query = {"user": username}
    if "status" in request.args:
        query["status"] = request.args["status"]
    if "category" in request.args:
        query["category"] = request.args["category"]

    tasks = mongo.db.tasks.find(query)
    return [serialize_task(t) for t in tasks], 200

@task_bp.route("/", methods=["POST", "OPTIONS"])
@cross_origin(supports_credentials=True)
def create_task():
    username = session.get("username")
    if not username:
        return {"error": "Unauthorized"}, 401

    data = request.get_json()
    valid, error = validate_user_input(data, ["title", "description", "due_date"])
    if not valid:
        return {"error": error}, 400

    task = {
        "user": username,
        "title": data["title"],
        "description": data["description"],
        "due_date": data["due_date"],
        "created_at": datetime.utcnow().isoformat(),
        "status": "open",
        "category": data.get("category", ""),
        "estimated_time": data.get("estimated_time", "")
    }

    result = mongo.db.tasks.insert_one(task)
    task["_id"] = str(result.inserted_id)
    logging.info(f"Task created for user '{username}': {task['title']}")

    user = mongo.db.users.find_one({"username": username})
    if user and user.get("telegram_chat_id"):
        message = f"📝 New task created: '{task['title']}' due on {task['due_date']}"
        send_telegram_message(message, user["telegram_chat_id"])

    return task, 201

@task_bp.route("/<task_id>", methods=["GET", "OPTIONS"])
@cross_origin(supports_credentials=True)
def get_task(task_id):
    username = session.get("username")
    if not username:
        return {"error": "Unauthorized"}, 401

    task = mongo.db.tasks.find_one({"_id": ObjectId(task_id), "user": username})
    if not task:
        return {"error": "Task not found"}, 404

    return serialize_task(task), 200

@task_bp.route("/<task_id>", methods=["PUT", "OPTIONS"])
@cross_origin(supports_credentials=True)
def update_task(task_id):
    username = session.get("username")
    if not username:
        return {"error": "Unauthorized"}, 401

    data = request.get_json()
    task = mongo.db.tasks.find_one({"_id": ObjectId(task_id), "user": username})
    if not task:
        return {"error": "Task not found"}, 404

    updates = {k: v for k, v in data.items() if k in ["title", "description", "due_date", "status", "category", "estimated_time"]}
    mongo.db.tasks.update_one({"_id": ObjectId(task_id)}, {"$set": updates})
    logging.info(f"Task updated for user '{username}': {task_id}")

    if task["status"] != "done" and updates.get("status") == "done":
        user = mongo.db.users.find_one({"username": username})
        if user and user.get("telegram_chat_id"):
            message = f"✅ Task marked as done: '{task['title']}'"
            send_telegram_message(message, user["telegram_chat_id"])

    updated_task = mongo.db.tasks.find_one({"_id": ObjectId(task_id)})
    return serialize_task(updated_task), 200

@task_bp.route("/<task_id>", methods=["DELETE", "OPTIONS"])
@cross_origin(supports_credentials=True)
def delete_task(task_id):
    username = session.get("username")
    if not username:
        return {"error": "Unauthorized"}, 401

    result = mongo.db.tasks.delete_one({"_id": ObjectId(task_id), "user": username})
    if result.deleted_count == 0:
        return {"error": "Task not found or not authorized"}, 404

    return {"message": "Task deleted"}, 200

@task_bp.route("/weekly-summary", methods=["POST", "OPTIONS"])
@cross_origin(supports_credentials=True)
def send_weekly_summary():
    users = mongo.db.users.find({"telegram_chat_id": {"$exists": True}})
    for user in users:
        username = user["username"]
        chat_id = user["telegram_chat_id"]
        tasks = list(mongo.db.tasks.find({"user": username, "status": "open"}))

        if not tasks:
            print(f"[{username}] No open tasks found.")
            continue

        task_lines = []
        for t in tasks:
            title = t.get("title", "").strip()
            due = t.get("due_date", "").strip()
            desc = t.get("description", "").strip()
            category = t.get("category", "No Category").strip()
            if not title or not due:
                continue
            task_lines.append(f"- Title: {title} | Category: {category} | Due: {due} | Description: {desc}")

        today_str = datetime.now().strftime("%Y-%m-%d")
        prompt = (
            f"Today is {today_str}.\n"
            "Summarize the following tasks in markdown.\n"
            "- Group by category (use 'General' if missing)\n"
            "- For each task, include: title (bold), due date, description, and estimated time\n"
            "- Mark tasks due in the next 7 days as '**Due Soon**'\n"
            "- No greetings or extra commentary\n\n"
            "Tasks:\n" +
            "\n".join(task_lines)
        )

        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=650,
                temperature=0.7
            )
            summary = response.choices[0].message.content.strip()
            send_telegram_message(f"📊 Weekly Summary for {username}:\n\n{summary}", chat_id)
        except Exception as e:
            print(f"Failed to send summary to {username}: {e}")

    return {"message": "Summaries sent"}, 200



@task_bp.route("/update-chat-id", methods=["POST", "OPTIONS"])
@cross_origin(supports_credentials=True)
def update_telegram_chat_id():
    username = session.get("username")
    if not username:
        return {"error": "Unauthorized"}, 401

    data = request.get_json()
    chat_id = data.get("telegram_chat_id")
    if not chat_id:
        return {"error": "Missing telegram_chat_id"}, 400

    mongo.db.users.update_one({"username": username}, {"$set": {"telegram_chat_id": chat_id}})
    return {"message": "Telegram chat ID updated"}, 200



