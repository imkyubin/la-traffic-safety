"""Three summaries and two figures that tell the project's central story."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from .clean import summarize

NAVY, TEAL, ORANGE = '#19334a', '#137f83', '#d95d39'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.titleweight': 'bold'})


def create_eda(crashes, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    temporal = crashes[crashes.HOUR.notna()]
    tables = {
        'by_hour': summarize(temporal, ['HOUR']),
        'by_time_period': summarize(temporal, ['TIME_PERIOD']),
        'by_city': summarize(crashes, ['CITY']).sort_values('severe_crashes', ascending=False),
    }
    for name, table in tables.items():
        table.to_csv(output / f'{name}.csv', index=False)

    hourly = tables['by_hour']
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), layout='constrained')
    axes[0].bar(hourly.HOUR, hourly.severe_crashes, color=TEAL)
    axes[0].set(title='Severe crash volume', xlabel='Hour of day', ylabel='Severe/fatal crashes')
    axes[1].plot(hourly.HOUR, hourly.severe_share, color=ORANGE, marker='o', markersize=4)
    axes[1].axhline(temporal.IS_SEVERE.mean(), color=NAVY, linestyle='--', label='Overall severity share')
    axes[1].yaxis.set_major_formatter(PercentFormatter(1))
    axes[1].set(title='Severity share among recorded injury crashes', xlabel='Hour of day', ylabel='Severe/fatal share')
    axes[1].legend(frameon=False, fontsize=8)
    for ax in axes:
        ax.set_xticks(range(0, 24, 3))
    fig.suptitle('LA County, 2024–2025 | Counts and proportions answer different questions', color=NAVY, fontsize=14)
    fig.savefig(output / 'hourly_patterns.png', dpi=170)
    plt.close(fig)

    top = tables['by_city'].head(10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(10, 5.5), layout='constrained')
    bars = ax.barh(top.CITY, top.severe_crashes, color=TEAL)
    ax.bar_label(bars, fmt='%d', padding=4, fontsize=9)
    ax.set(title='Where are severe crashes concentrated?', xlabel='Recorded severe/fatal crashes, 2024–2025')
    ax.set_xlim(0, top.severe_crashes.max() * 1.15)
    fig.savefig(output / 'top_jurisdictions.png', dpi=170)
    plt.close(fig)
    return tables
