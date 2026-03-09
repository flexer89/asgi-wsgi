from locust import FastHttpUser, task

class BenchmarkUser(FastHttpUser):
    @task
    def test_endpoint(self):
        self.client.get("/io-task", name="/io-task")
        # self.client.get("/cpu-task", name="/cpu-task")
        # self.client.get("/health", name="/health")
