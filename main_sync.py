import falcon
import time
from cpu_module import compute_heavy_task

class HealthResource:
    def on_get(self, req, resp):
        resp.media = {"status": "ok"}

class IOTaskResource:
    def on_get(self, req, resp):
        time.sleep(0.1)
        resp.media = {"result": "io_completed"}

class CPUTaskResource:
    def on_get(self, req, resp):
        result = compute_heavy_task()
        resp.media = {"result": result}

app = falcon.App()
app.add_route('/health', HealthResource())
app.add_route('/io-task', IOTaskResource())
app.add_route('/cpu-task', CPUTaskResource())