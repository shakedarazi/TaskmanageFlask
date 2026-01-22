from datetime import datetime

def is_task_overdue(task):
    try:
        due = datetime.strptime(task["due_date"], "%Y-%m-%d")
        return datetime.now() > due
    except:
        return False