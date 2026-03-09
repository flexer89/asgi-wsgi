import time
from cpu_module import compute_heavy_task

start = time.time()
compute_heavy_task(100_000)
end = time.time()
print(f"Execution time: {end - start} seconds")