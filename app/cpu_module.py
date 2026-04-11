import time

import time

def compute_heavy_task(duration_seconds: float = 0.1) -> str:
    end_time = time.perf_counter() + duration_seconds

    while time.perf_counter() < end_time:
        pass 
        
    return "cpu_completed"

if __name__ == "__main__":
    start = time.time()
    compute_heavy_task()
    stop = time.time()
    print(stop - start)