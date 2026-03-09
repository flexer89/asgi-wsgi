import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def parse_time_to_ms(val):
    if pd.isna(val) or val == '0': return 0.0
    val = str(val).strip()
    try:
        if val.endswith('ms'): return float(val[:-2])
        elif val.endswith('us'): return float(val[:-2]) / 1000.0
        elif val.endswith('s'): return float(val[:-1]) * 1000.0
        return float(val)
    except:
        return 0.0

df = pd.read_csv('wyniki_io_bound.csv')

df['p50_ms'] = df['p50'].apply(parse_time_to_ms)
df['p99_ms'] = df['p99'].apply(parse_time_to_ms)

sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 12, 'font.family': 'serif'})

plt.figure(figsize=(10, 6))
sns.lineplot(data=df, x='Polaczenia', y='RPS', hue='Serwer', marker='o', linewidth=2.5, markersize=8)
plt.title('Scenariusz A: Przepustowość (RPS) vs Liczba połączeń (I/O-bound)', fontsize=14, pad=15)
plt.xlabel('Liczba jednoczesnych połączeń', fontsize=12)
plt.ylabel('Przepustowość (Zapytania / sekundę)', fontsize=12)
plt.legend(title='Architektura', loc='upper right')
plt.tight_layout()
plt.savefig('wykres_io_rps.png', dpi=300)
print("Zapisano wykres: wykres_io_rps.png")

plt.figure(figsize=(10, 6))
sns.lineplot(data=df, x='Polaczenia', y='p99_ms', hue='Serwer', marker='s', linewidth=2.5, markersize=8, palette=['#e74c3c', '#2ecc71'])
plt.title('Scenariusz A: Opóźnienie 99. percentyla vs Liczba połączeń', fontsize=14, pad=15)
plt.xlabel('Liczba jednoczesnych połączeń', fontsize=12)
plt.ylabel('Opóźnienie p99 (ms)', fontsize=12)
plt.yscale('log')
plt.legend(title='Architektura', loc='upper left')
plt.tight_layout()
plt.savefig('wykres_io_p99.png', dpi=300)
print("Zapisano wykres: wykres_io_p99.png")