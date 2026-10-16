"""One command: clean the data, run EDA, evaluate one model, export for Tableau."""
import argparse
import json
from pathlib import Path
from src.clean import DEFAULT_DATA, ROOT, load_crashes, tableau_export
from src.eda import create_eda
from src.model import train_and_evaluate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=DEFAULT_DATA)
    parser.add_argument('--output', type=Path, default=ROOT / 'outputs')
    args = parser.parse_args()

    crashes, quality = load_crashes(args.data)
    print(f"1. Clean: {len(crashes):,} unique crashes; {quality['invalid_time_rows']} invalid times.", flush=True)
    create_eda(crashes, args.output)
    print('2. EDA: time-of-day and jurisdiction summaries saved.', flush=True)
    metrics = train_and_evaluate(crashes, args.output)
    print(f"3. Model: ROC AUC {metrics['roc_auc']:.4f}; PR AUC {metrics['pr_auc_trapezoidal']:.4f}.", flush=True)
    export = tableau_export(crashes)
    export.to_csv(args.output / 'tableau_proportional_severity_data.csv', index=False)
    quality.update(temporal_rows=int(crashes.HOUR.notna().sum()), model_rows=metrics['model_rows'], tableau_export_rows=len(export))
    (args.output / 'data_quality.json').write_text(json.dumps(quality, indent=2) + '\n')
    print(f'4. Tableau: {len(export):,} rows exported. Results: {args.output.resolve()}', flush=True)


if __name__ == '__main__':
    main()
