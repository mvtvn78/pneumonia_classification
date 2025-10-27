from datetime import datetime


def generateUniqueTimestamp():
    timestamp = datetime.now().timestamp()
    return f"file_{timestamp}"
