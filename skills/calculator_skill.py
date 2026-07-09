# skills/calculator_skill.py — a simple math skill for PUTER

def calculate(a, b, operation):
    """Do basic math on two numbers. operation: add, subtract, multiply, or divide."""
    a = float(a)
    b = float(b)
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        return "Cannot divide by zero." if b == 0 else a / b
    else:
        return f"Unknown operation: {operation}"

if __name__ == "__main__":
    print(calculate(12, 7, "multiply"))   # 84.0