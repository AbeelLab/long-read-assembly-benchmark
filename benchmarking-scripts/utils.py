import re

def convert_runtime(runtime_in_seconds):
    if runtime_in_seconds < 3600:
        # Minutes
        return 1
    elif runtime_in_seconds < 86400:
        # Hours
        return 2
    elif runtime_in_seconds < 86400 * 3:
        # 1 - 3 days
        return 3
    elif runtime_in_seconds < 86400 * 4:
        # 3 - 7 days
        return 4
    else:
        # > 7 days
        return 5

def parse_memory(memory):
    result = int(re.findall(r'\d+', memory)[0])
    if memory.endswith("K"):
        return result
    elif memory.endswith("M"):
        return result * 1000
    else:
        return int(memory)

def convert_memory(memory_in_kb):
    memory_in_gb = float(memory_in_kb) / 1000000
    if memory_in_gb < 8:
        return 1
    elif memory_in_gb < 16:
        return 2
    elif memory_in_gb < 32:
        return 3
    elif memory_in_gb < 128:
        print(memory_in_gb)
        return 4
    else:
        return 5
