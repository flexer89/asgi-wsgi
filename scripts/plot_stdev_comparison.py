import pandas as pd
import matplotlib.pyplot as plt

df_4w = pd.read_csv('cpu_bound_results_4_worker_1_thread_sync_4_worker_async.csv')
sync_4w = df_4w[df_4w['Server'] == 'Sync'].sort_values('Connections')

df_4t = pd.read_csv('cpu_bound_results_1_worker_4_thread_sync_1_worker_async.csv')
sync_4t = df_4t[df_4t['Server'] == 'Sync'].sort_values('Connections')

plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(sync_4w['Connections'], sync_4w['RPS'], 
        color='#2980b9', marker='o', linestyle='-', linewidth=2, markersize=6, 
        label='Multiprocessing (4 workers, 1 thread)')

ax.plot(sync_4t['Connections'], sync_4t['RPS'], 
        color='#e67e22', marker='o', linestyle='-', linewidth=2, markersize=6, 
        label='Multithreading (1 worker, 4 threads)')

ax.set_title('Przepustowość (RPS) - wpływ GIL w architekturze synchronicznej', fontsize=14, pad=15)
ax.set_xlabel('Number of concurrent connections', fontsize=12)
ax.set_ylabel('RPS (Requests per second)', fontsize=12)

legend = ax.legend(title='Configuration (WSGI)', loc='lower right', fontsize=11, title_fontsize=12, frameon=True)
legend.get_frame().set_facecolor('white')
legend.get_frame().set_edgecolor('lightgray')

ax.grid(True, linestyle='-', alpha=0.7)
ax.set_facecolor('#fafafa')

ax.annotate(f"{sync_4w['RPS'].iloc[-1]} RPS", 
            xy=(sync_4w['Connections'].iloc[-1], sync_4w['RPS'].iloc[-1]),
            xytext=(-45, 10), textcoords='offset points', color='#2980b9', fontweight='bold')

ax.annotate(f"{sync_4t['RPS'].iloc[-1]} RPS", 
            xy=(sync_4t['Connections'].iloc[-1], sync_4t['RPS'].iloc[-1]),
            xytext=(-45, -15), textcoords='offset points', color='#e67e22', fontweight='bold')

plt.tight_layout()

file_name = 'cpu_sync_processes_vs_threads_rps.png'
plt.savefig(file_name, dpi=300, bbox_inches='tight')
print(f"Chart has been generated and saved as '{file_name}'")