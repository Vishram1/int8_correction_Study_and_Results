#!/usr/bin/env python3
"""Create manuscript tables/figure from independently verified observations."""
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
MODELS = ('mobilenet_v2', 'resnet18')
NAMES = {'mobilenet_v2': 'MobileNetV2', 'resnet18': 'ResNet18'}
ARMS = ('baseline', 'head-reencode', 'single', 'average', 'shared', 'refit', 'bias-refit')
LABELS = {'baseline': 'Base', 'head-reencode': 'Re-enc.', 'single': 'Single',
          'average': 'Average', 'shared': 'Shared', 'refit': 'Refit', 'bias-refit': 'Bias'}


def interval(v):
    return '[' + ', '.join(f'{x:+.3f}' for x in v) + ']'


def tex_table(name, columns, header, rows):
    content = ['\\begin{tabular}{' + columns + '}', '\\toprule', ' & '.join(header) + r' \\', '\\midrule']
    content.extend(' & '.join(map(str, row)) + r' \\' for row in rows)
    content += ['\\bottomrule', '\\end{tabular}']
    (ROOT / 'tables' / name).write_text('\n'.join(content) + '\n')


def main():
    for name in ('tables', 'figures'):
        (ROOT / name).mkdir(exist_ok=True)
    r = json.loads((ROOT / 'evidence/verified-statistics.json').read_text())
    flat = []
    for backend in ('native', 'host'):
        rows = []
        for model in MODELS:
            values = r[backend][model]
            targets = list(dict.fromkeys(x['target'] for x in values['rows']))
            for target in targets:
                records = [next(x for x in values['rows'] if x['target'] == target and x['arm'] == a) for a in ARMS]
                rows.append([NAMES[model], target[-1]] + [f"{x['top1_pct']:.2f}" for x in records])
                flat.extend(dict(backend=backend, model=model, **x) for x in records)
        tex_table(backend + '-accuracies.tex', 'llrrrrrrr', ['Model', 'Target'] + [LABELS[a] for a in ARMS], rows)
    with (ROOT / 'evidence/all-accuracies.csv').open('w') as f:
        writer = csv.DictWriter(f, fieldnames=list(flat[0])); writer.writeheader(); writer.writerows(flat)
    rows, secondary, per_target, flat = [], [], [], []
    for backend in ('native', 'host'):
        for model in MODELS:
            p = r[backend][model]
            for a in p['aggregates']:
                name = a['contrast'].replace('-minus-', ' -- ')
                item = [backend.capitalize(), NAMES[model], name,
                        f"{a['mean_effect_pp']:+.3f}", interval(a['conditional_mean_ci95_pp'])]
                if a['contrast'] in ('shared-minus-single', 'shared-minus-refit'):
                    rows.append(item)
                else:
                    secondary.append(item)
            for c in p['contrasts']:
                flat.append(dict(backend=backend, model=model, **c))
            targets = list(dict.fromkeys(x['target'] for x in p['rows']))
            for target in targets:
                cs = [next(x for x in p['contrasts'] if x['target'] == target and x['contrast'] == name)
                      for name in ('shared-minus-single', 'shared-minus-refit', 'single-minus-refit')]
                per_target.append([backend.capitalize(), NAMES[model], target[-1]] +
                                  [f"{x['effect_pp']:+.3f} {interval(x['pointwise_ci95_pp'])}" for x in cs])
    header = ['Backend', 'Model', 'Contrast', 'Mean (pp)', '95\\% interval (pp)']
    tex_table('primary.tex', 'lllrr', header, rows)
    tex_table('secondary.tex', 'lllrr', header, secondary)
    tex_table('per-target.tex', 'lllrrr', ['Backend', 'Model', 'Target', 'Shared -- single', 'Shared -- refit', 'Single -- refit'], per_target)
    with (ROOT / 'evidence/all-target-contrasts.csv').open('w') as f:
        writer = csv.DictWriter(f, fieldnames=list(flat[0])); writer.writeheader(); writer.writerows(flat)
    plt.rcParams.update({'font.size': 9, 'pdf.fonttype': 42, 'ps.fonttype': 42})
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 2.65), sharey=True)
    panels = [('native', 'mobilenet_v2'), ('native', 'resnet18'), ('host', 'mobilenet_v2'), ('host', 'resnet18')]
    for ax, contrast, title in zip(axes, ('shared-minus-single', 'shared-minus-refit'), ('Shared − single', 'Shared − target refit')):
        for i, (backend, model) in enumerate(panels):
            c = next(x for x in r[backend][model]['aggregates'] if x['contrast'] == contrast)
            mean, (lo, hi) = c['mean_effect_pp'], c['conditional_mean_ci95_pp']
            ax.errorbar(mean, 3-i, xerr=[[mean-lo], [hi-mean]], fmt='o', capsize=3,
                        color='#176477' if backend == 'native' else '#985619', markersize=4)
        ax.axvline(0, color='0.45', lw=.8, linestyle='--')
        ax.set_title(title); ax.set_xlabel('Accuracy difference (percentage points)')
        ax.set_xlim(-.26, .26); ax.set_ylim(-.55, 3.55)
        ax.grid(axis='x', alpha=.18); ax.spines[['right', 'top']].set_visible(False)
        ax.set_yticks([3,2,1,0], ['NPU · MobileNetV2', 'NPU · ResNet18', 'Host · MobileNetV2', 'Host · ResNet18'])
    fig.tight_layout()
    for suffix in ('pdf', 'png'):
        fig.savefig(ROOT / 'figures' / ('primary-effects.' + suffix), dpi=180, bbox_inches='tight')
    print('Rendered all result tables, full CSVs, and paired-effects figure.')


if __name__ == '__main__':
    main()
