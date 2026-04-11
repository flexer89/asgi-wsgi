import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker

def parse_time_to_ms(val):
    if pd.isna(val) or val == '0' or val == 0: return 0.0
    val = str(val).strip()
    try:
        if val.endswith('ms'): return float(val[:-2])
        elif val.endswith('us'): return float(val[:-2]) / 1000.0
        elif val.endswith('s'): return float(val[:-1]) * 1000.0
        return float(val)
    except:
        return 0.0

df = pd.read_csv('./cpu_bound_results_4_worker_1_thread_sync_4_worker_async.csv') 

time_cols = ['Avg_Lat', 'p50', 'p99', 'Max_Lat', 'Stdev_Lat']
for col in time_cols:
    df[f'{col}_ms'] = df[col].apply(parse_time_to_ms)

df['Total_Errors'] = df['Timeouts'] + df['ConnErrors'] + df['HTTPErrors']

sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 12, 'font.family': 'sans-serif'})
architecture_colors = {'Sync': '#e74c3c', 'Async': '#2ecc71'}
plt.figure(figsize=(10, 6))
ax = sns.lineplot(data=df, x='Connections', y='RPS', hue='Server', 
                  marker='o', linewidth=2.0, markersize=5, palette=architecture_colors)

plt.title('Przepustowość (RPS) vs Liczba połączeń', fontsize=14, pad=15)
plt.xlabel('Number of concurrent connections')
plt.ylabel('RPS (Requests per second)')

plt.ylim(bottom=0)
plt.xlim(left=0)

ax.yaxis.set_major_locator(ticker.MultipleLocator(250))
sync_data = df[df['Server'] == 'Sync'].reset_index()

for i in range(0, len(sync_data), 2):
    x_val = sync_data['Connections'].iloc[i]
    y_val = sync_data['RPS'].iloc[i]
    
    ax.annotate(f'{y_val:.1f}', 
                xy=(x_val, y_val), 
                xytext=(0, 8),
                textcoords='offset points', 
                ha='center', va='bottom', 
                fontsize=9, 
                color=architecture_colors['Sync'], 
                weight='bold')

async_data = df[df['Server'] == 'Async'].reset_index()
for i in range(0, len(async_data), 2):
    x_val = async_data['Connections'].iloc[i]
    y_val = async_data['RPS'].iloc[i]
    
    ax.annotate(f'{y_val:.0f}', 
                xy=(x_val, y_val), 
                xytext=(0, 8), 
                textcoords='offset points', 
                ha='center', va='bottom', 
                fontsize=9, 
                color=architecture_colors['Async'])

plt.legend(title='Architecture', loc='upper right') 

plt.tight_layout()
plt.savefig('chart_01_rps.png', dpi=300)

plt.figure(figsize=(10, 6))
sns.lineplot(data=df, x='Connections', y='p99_ms', hue='Server', marker='s', linewidth=2.5, markersize=8, palette=architecture_colors)
plt.title('Opóźnienie 99. percentyla (p99)', fontsize=14, pad=15)
plt.xlabel('Number of concurrent connections')
plt.ylabel('p99 Response time (ms)')
plt.yscale('log')
plt.legend(title='Architecture', loc='upper left')
plt.tight_layout()
plt.savefig('chart_02_p99.png', dpi=300)

plt.figure(figsize=(10, 6))
sns.lineplot(data=df, x='Connections', y='Stdev_Lat_ms', hue='Server', marker='^', linewidth=2.5, markersize=8, palette=architecture_colors)
plt.title('Stabilność odpowiedzi (Odchylenie standardowe)', fontsize=14, pad=15)
plt.xlabel('Number of concurrent connections')
plt.ylabel('Response time variance / Jitter (ms)')
plt.legend(title='Architecture', loc='upper left')
plt.tight_layout()
plt.savefig('chart_03_stability.png', dpi=300)

plt.figure(figsize=(10, 6))
sns.lineplot(data=df, x='Connections', y='Max_Lat_ms', hue='Server', marker='D', linewidth=2.5, markersize=8, palette=architecture_colors)
plt.title('Najgorszy przypadek (Max Latency)', fontsize=14, pad=15)
plt.xlabel('Number of concurrent connections')
plt.ylabel('Maximum response time (ms)')
plt.legend(title='Architecture', loc='upper left')
plt.tight_layout()
plt.savefig('chart_04_max_latency.png', dpi=300)

plt.figure(figsize=(10, 6))
sns.lineplot(data=df, x='Connections', y='Total_Errors', hue='Server', marker='X', linewidth=2.5, markersize=10, palette=architecture_colors)
plt.title('Ilość odrzuconych zapytań i błędów', fontsize=14, pad=15)
plt.xlabel('Number of concurrent connections')
plt.ylabel('Total errors (Timeouts + Conn + HTTP)')
plt.legend(title='Architecture', loc='upper left')
plt.tight_layout()
plt.savefig('chart_05_errors.png', dpi=300)

print("✅ Successfully generated 5 charts!")