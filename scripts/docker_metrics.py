import docker
import json
import argparse
import sys

parser = argparse.ArgumentParser(description="Save Docker container statistics to a JSON file.")
parser.add_argument("container_name", help="Name or ID of the container to monitor")
parser.add_argument("-o", "--output", default="stats.json", help="Output file name (default: stats.json)")
args = parser.parse_args()
client = docker.from_env()

try:
    container = client.containers.get(args.container_name)
except docker.errors.NotFound:
    print(f"Error: Container named '{args.container_name}' was not found.")
    sys.exit(1)

try:
    with open(args.output, 'a') as f:
        for stat in container.stats(stream=True, decode=True):
            json.dump(stat, f)
            f.write('\n')
            f.flush()
except KeyboardInterrupt:
    print("\nData collection stopped. Statistics saved to file.")