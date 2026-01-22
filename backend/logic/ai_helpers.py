def build_task_prompt(description):
    return f"Categorize and estimate time for the following task: '{description}'"

def parse_openai_response(response):
    return response.choices[0].message.content
