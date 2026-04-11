python scripts/docker_metrics.py falcon_sync -o falcon_sync_cpu_docker_metrics.json
python scripts/docker_metrics.py falcon_async -o falcon_async_cpu_docker_metrics.json

docker compose up --build -d
./tests/run_cpu_tests.sh    