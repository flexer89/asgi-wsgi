import json
import argparse
import sys
import matplotlib.pyplot as plt
from datetime import datetime

parser = argparse.ArgumentParser(description="Advanced Docker stats charts (Sync vs Async).")
parser.add_argument("file", help="JSON file containing Docker stats data")
parser.add_argument("-o", "--output", default="architecture_report.png", help="Output file name (PNG)")
args = parser.parse_args()

timestamps, pids = [], []
cpu_total, cpu_user, cpu_kernel, cpu_throttled = [], [], [], []
ram_total, ram_rss = [], []
net_rx, net_tx = [], []
page_faults = []

prev_time = None
prev_rx, prev_tx = 0, 0
prev_throttled_time = None
prev_pgfault = None

print(f"Analyzing data from file: {args.file}...")

try:
    with open(args.file, 'r') as f:
        for line in f:
            try:
                data = json.loads(line)

                time_str = data['read'][:26].replace('Z', '')
                try:
                    current_time = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%f")
                except ValueError:
                    current_time = datetime.strptime(time_str[:19], "%Y-%m-%dT%H:%M:%S")

                time_diff_sec = (current_time - prev_time).total_seconds() if prev_time else 0

                sys_cpu = data['cpu_stats'].get('system_cpu_usage', 0)
                pre_sys_cpu = data['precpu_stats'].get('system_cpu_usage', 0)
                system_delta = sys_cpu - pre_sys_cpu

                if system_delta > 0 and pre_sys_cpu > 0:
                    online_cpus = data['cpu_stats'].get('online_cpus', 1)
                    multiplier = (online_cpus * 100.0) / system_delta

                    cpu_delta = data['cpu_stats']['cpu_usage'].get('total_usage', 0) - data['precpu_stats']['cpu_usage'].get('total_usage', 0)
                    cpu_total.append(cpu_delta * multiplier)
                    
                    user_delta = data['cpu_stats']['cpu_usage'].get('usage_in_usermode', 0) - data['precpu_stats']['cpu_usage'].get('usage_in_usermode', 0)
                    cpu_user.append(user_delta * multiplier)
                    
                    kernel_delta = data['cpu_stats']['cpu_usage'].get('usage_in_kernelmode', 0) - data['precpu_stats']['cpu_usage'].get('usage_in_kernelmode', 0)
                    cpu_kernel.append(kernel_delta * multiplier)
                else:
                    if not timestamps: continue
                    cpu_total.append(0); cpu_user.append(0); cpu_kernel.append(0)

                current_throttled = data['cpu_stats'].get('throttling_data', {}).get('throttled_time', 0)
                if prev_throttled_time is not None and time_diff_sec > 0:
                    throttled_ms = ((current_throttled - prev_throttled_time) / 1_000_000) / time_diff_sec
                    cpu_throttled.append(throttled_ms)
                else:
                    cpu_throttled.append(0)
                prev_throttled_time = current_throttled

                ram_total.append(data['memory_stats'].get('usage', 0) / (1024 * 1024))
                ram_rss.append(data['memory_stats'].get('stats', {}).get('rss', 0) / (1024 * 1024))

                current_pgfault = data['memory_stats'].get('stats', {}).get('pgfault', 0)
                if prev_pgfault is not None and time_diff_sec > 0:
                    pf_rate = (current_pgfault - prev_pgfault) / time_diff_sec
                    page_faults.append(max(0, pf_rate)) 
                else:
                    page_faults.append(0)
                prev_pgfault = current_pgfault

                net_data = data.get('networks', {})
                rx_total = sum(n['rx_bytes'] for n in net_data.values())
                tx_total = sum(n['tx_bytes'] for n in net_data.values())
                
                if prev_time and time_diff_sec > 0:
                    net_rx.append(((rx_total - prev_rx) / 1024) / time_diff_sec)
                    net_tx.append(((tx_total - prev_tx) / 1024) / time_diff_sec)
                else:
                    net_rx.append(0); net_tx.append(0)
                prev_rx, prev_tx = rx_total, tx_total

                pids.append(data.get('pids_stats', {}).get('current', 0))
                timestamps.append(current_time)
                prev_time = current_time

            except KeyError:
                continue

except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)

plt.figure(figsize=(18, 8))
plt.style.use('bmh')

plt.subplot(2, 2, 1)
plt.plot(timestamps, cpu_total, color='black', linewidth=1.5)
plt.title('Całkowite zużycie CPU (%)')
plt.ylabel('% (Limit = 100%)')
plt.xticks(rotation=30)

plt.subplot(2, 2, 2)
plt.plot(timestamps, cpu_user, label='User Mode (%)', color='#3498db', alpha=0.8)
plt.plot(timestamps, cpu_kernel, label='Kernel Mode (%)', color='#e74c3c', alpha=0.8)
plt.title('CPU: Tryb User vs Kernel')
plt.ylabel('%')
plt.legend()
plt.xticks(rotation=30)

# plt.subplot(2, 2, 3)
# plt.plot(timestamps, cpu_throttled, color='#8e44ad', linewidth=1.5)
# plt.title('3. Dławienie CPU (Throttled Time)')
# plt.ylabel('ms / s')
# plt.fill_between(timestamps, cpu_throttled, color='#8e44ad', alpha=0.3)
# plt.xticks(rotation=30)

plt.subplot(2, 2, 4)
plt.plot(timestamps, pids, color='#2c3e50', linewidth=2)
plt.title('PIDs (Wątki/Procesy)')
plt.ylabel('Count')
plt.xticks(rotation=30)

plt.subplot(2, 2, 3)
plt.plot(timestamps, ram_total, label='Total Usage (MB)', color='#f39c12', linestyle='--')
plt.plot(timestamps, ram_rss, label='RSS - Czysty RAM (MB)', color='#d35400', linewidth=2)
plt.title('Zużycie Pamięci RAM')
plt.ylabel('MB')
plt.legend()
plt.xticks(rotation=30)

# plt.subplot(2, 2, 6)
# plt.plot(timestamps, page_faults, color='#16a085', linewidth=1.5)
# plt.title('6. Alokacja pamięci (Page Faults)')
# plt.ylabel('Faults / s')
# plt.xticks(rotation=30)

# plt.subplot(2, 2, 7)
# plt.plot(timestamps, net_rx, label='Download (KB/s)', color='#27ae60')
# plt.title('7. Sieć: Pobieranie zapytań')
# plt.ylabel('KB/s')
# plt.fill_between(timestamps, net_rx, color='#27ae60', alpha=0.3)
# plt.xticks(rotation=30)

# plt.subplot(2, 2, 8)
# plt.plot(timestamps, net_tx, label='Upload (KB/s)', color='#c0392b')
# plt.title('8. Sieć: Wysyłanie odpowiedzi')
# plt.ylabel('KB/s')
# plt.fill_between(timestamps, net_tx, color='#c0392b', alpha=0.3)
# plt.xticks(rotation=30)

plt.tight_layout(pad=3.0)
plt.savefig(args.output, dpi=150)
print(f"✅ Finished! Check file: {args.output}")