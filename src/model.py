"""The project's existing random forest, evaluated on a chronological holdout."""
import json
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (roc_auc_score, precision_recall_curve, auc,
                             classification_report, confusion_matrix)
from .clean import model_frame
from .eda import plt, NAVY, TEAL, ORANGE

RF_FEATURES = ['HOUR', 'MONTH', 'DAY_OF_MONTH', 'DAY_OF_WEEK_NUM', 'IS_WEEKEND',
               'IS_EVENING_PEAK', 'IS_LATE_NIGHT', 'IS_INTERSECTION',
               'IS_SURFACE_STREET', 'IS_NO_CONTROL', 'IS_FELONY_HR',
               'HOUR_SIN', 'HOUR_COS', 'DOW_SIN', 'DOW_COS', 'MONTH_SIN', 'MONTH_COS']


def train_and_evaluate(df, output):
    """Copy of Time Series Modeling.ipynb, cell 27; original 80/20 split."""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    frame = model_frame(df).sort_values('DATETIME').reset_index(drop=True)
    split = int(len(frame) * .8)
    train, test = frame.iloc[:split], frame.iloc[split:]
    if train.IS_SEVERE.nunique() < 2 or test.IS_SEVERE.nunique() < 2:
        raise ValueError('Both temporal partitions must contain both target classes.')
    model = RandomForestClassifier(n_estimators=300, max_depth=12,
        min_samples_split=10, min_samples_leaf=5, class_weight='balanced',
        random_state=42, n_jobs=2)
    model.fit(train[RF_FEATURES], train.IS_SEVERE)
    probs = model.predict_proba(test[RF_FEATURES])[:, 1]
    predicted = model.predict(test[RF_FEATURES])
    precision, recall, _ = precision_recall_curve(test.IS_SEVERE, probs)
    metrics = {
        'source': 'Copy of Time Series Modeling.ipynb, cell 27 (zero-based)',
        'purpose': 'Retrospective classification of recorded crash severity; not prospective deployment forecasting',
        'model_rows': len(frame), 'train_rows': len(train), 'test_rows': len(test),
        'train_start': str(train.DATETIME.min()), 'train_end': str(train.DATETIME.max()),
        'test_start': str(test.DATETIME.min()), 'test_end': str(test.DATETIME.max()),
        'train_test_timestamp_overlap': bool(train.DATETIME.max() >= test.DATETIME.min()),
        'threshold': .5, 'roc_auc': float(roc_auc_score(test.IS_SEVERE, probs)),
        'pr_auc_trapezoidal': float(auc(recall, precision)),
        'test_prevalence': float(test.IS_SEVERE.mean()),
        'majority_class_accuracy_reference': float(1 - test.IS_SEVERE.mean()),
        'confusion_matrix_labels': [0, 1],
        'confusion_matrix': confusion_matrix(test.IS_SEVERE, predicted, labels=[0, 1]).tolist(),
        'classification_report': classification_report(test.IS_SEVERE, predicted, output_dict=True, zero_division=0),
    }
    (output / 'model_metrics.json').write_text(json.dumps(metrics, indent=2) + '\n')
    plot_evaluation(test.IS_SEVERE, predicted, precision, recall, metrics, output)
    return metrics


def plot_evaluation(actual, predicted, precision, recall, metrics, output):
    """Display the existing model's precision/recall tradeoff and error counts."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), layout='constrained')
    axes[0].plot(recall, precision, color=TEAL, label='Random forest')
    axes[0].axhline(metrics['test_prevalence'], color=ORANGE, linestyle='--', label='Test prevalence')
    axes[0].set(xlabel='Recall', ylabel='Precision', xlim=(0, 1), ylim=(0, 1), title='Severe-class precision and recall')
    axes[0].legend(frameon=False)
    matrix = confusion_matrix(actual, predicted, labels=[0, 1])
    axes[1].imshow(matrix, cmap='Blues')
    for row in range(2):
        for col in range(2):
            axes[1].text(col, row, f'{matrix[row, col]:,}', ha='center', va='center',
                         color='white' if matrix[row, col] > matrix.max() / 2 else NAVY, fontsize=14)
    axes[1].set_xticks([0, 1], ['Other injury', 'Severe/fatal'])
    axes[1].set_yticks([0, 1], ['Other injury', 'Severe/fatal'])
    axes[1].set(xlabel='Predicted', ylabel='Actual', title='Holdout results at threshold 0.50')
    fig.savefig(output / 'model_evaluation.png', dpi=170)
    plt.close(fig)
