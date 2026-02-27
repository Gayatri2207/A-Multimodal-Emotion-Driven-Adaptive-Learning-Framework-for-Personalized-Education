def evaluate_code(code: str):
    if "print" in code:
        return {"score": 100, "feedback": "Good output usage"}
    return {"score": 50, "feedback": "Needs improvement"}
