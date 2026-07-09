from datetime import datetime


def test_agent(task):
    """
    Test Agent
    Role: Disposable test agent
    """

    return {
        "agent": "Test",
        "role": "Disposable test agent",
        "status": "complete",
        "task": task,
        "result": "Test received the task and is ready to work.",
        "requires_approval": True,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }


if __name__ == "__main__":
    print(test_agent("test Test agent"))
