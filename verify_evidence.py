#!/usr/bin/env python3
"""Independently reconstruct all final statistics; requires only NumPy.

This verifies compact predictions and their reported statistics. It does not
rerun inference or authenticate the private raw phone records.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

MODELS = ('mobilenet_v2', 'resnet18')
ARMS = ('baseline', 'head-reencode', 'single', 'average', 'shared', 'refit', 'bias-refit')
PAIRS = (('shared', 'single'), ('shared', 'refit'), ('shared', 'average'),
         ('single', 'refit'), ('shared', 'head-reencode'), ('shared', 'baseline'),
         ('shared', 'bias-refit'))


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(2**20), b''):
            h.update(block)
    return h.hexdigest()


def close(actual, expected):
    if not np.allclose(actual, expected, rtol=0, atol=1e-10):
        raise AssertionError((actual, expected))


def reconstruct(data, expected):
    labels = data['labels']
    assert labels.shape == (7000,)
    classes, counts = np.unique(labels, return_counts=True)
    assert np.array_equal(classes, np.arange(1000)) and np.all(counts == 7)
    order = np.argsort(labels, kind='stable')
    # Independent multinomial-count implementation of the frozen class draws.
    rng = np.random.default_rng(2026101499)
    class_counts = np.empty((10000, 1000), dtype=np.float64)
    for start in range(0, 10000, 100):
        draws = rng.integers(0, 1000, size=(100, 1000))
        for j, draw in enumerate(draws):
            class_counts[start+j] = np.bincount(draw, minlength=1000)
    result = {'n': 7000, 'resamples': 10000, 'seed': 2026101499,
              'scope': 'Pointwise paired class intervals conditional on fixed targets.',
              'host': {}, 'native': {}, 'fp32': {}, 'verified_accuracy_cells': 0,
              'verified_intervals': 0}
    for backend, nt in (('host', 5), ('native', 2)):
        pred = data[backend]
        ties = data[backend + '_ties']
        assert pred.shape == ties.shape == (2, nt, 7, 7000)
        assert np.all((pred >= 0) & (pred < 1000)) and np.all(ties >= 1)
        for m, model in enumerate(MODELS):
            saved = expected[backend][model]
            correctness = (pred[m] == labels).astype(np.int8)
            rows, contrasts, aggregates, all_diff = [], [], [], []
            for t in range(nt):
                for a, arm in enumerate(ARMS):
                    score = 100 * correctness[t, a].mean()
                    ref = next(x for x in saved['rows'] if x['target'] == f'target-{t+1}' and x['arm'] == arm)
                    close(score, ref['top1_pct'])
                    close(score - 100*correctness[t, 0].mean(), ref['minus_baseline_pp'])
                    rows.append(dict(ref, correct=int(correctness[t, a].sum()),
                                     ties=int((ties[m, t, a] > 1).sum())))
                    result['verified_accuracy_cells'] += 1
            for left, right in PAIRS:
                difference = correctness[:, ARMS.index(left)] - correctness[:, ARMS.index(right)]
                all_diff.extend(difference)
                all_diff.append(difference.mean(axis=0))
            all_diff = np.asarray(all_diff, dtype=np.float64)
            per_class = all_diff[:, order].reshape(-1, 1000, 7).sum(axis=2).T
            boot = (100 / 7000) * (class_counts @ per_class)
            intervals = np.percentile(boot, [2.5, 97.5], axis=0).T
            for j, (left, right) in enumerate(PAIRS):
                name = left + '-minus-' + right
                block = all_diff[j*(nt+1):(j+1)*(nt+1)]
                cis = intervals[j*(nt+1):(j+1)*(nt+1)]
                effects = 100*block[:nt].mean(axis=1)
                for t in range(nt):
                    ref = next(x for x in saved['contrasts'] if x['contrast'] == name and x['target'] == f'target-{t+1}')
                    close(effects[t], ref['effect_pp'])
                    close(cis[t], ref['pointwise_ci95_pp'])
                    contrasts.append(dict(ref, improved=int((block[t] == 1).sum()),
                                          harmed=int((block[t] == -1).sum())))
                    result['verified_intervals'] += 1
                ref = next(x for x in saved['aggregates'] if x['contrast'] == name)
                close(effects.mean(), ref['mean_effect_pp'])
                close(effects.min(), ref['worst_observed_effect_pp'])
                close(effects.max(), ref['best_observed_effect_pp'])
                close(cis[-1], ref['conditional_mean_ci95_pp'])
                aggregates.append(ref)
                result['verified_intervals'] += 1
            result[backend][model] = dict(rows=rows, contrasts=contrasts, aggregates=aggregates)
    for m, model in enumerate(MODELS):
        result['fp32'][model] = {'top1_pct': float(100*(data['fp32'][m] == labels).mean()),
                                'ties': int((data['fp32_ties'][m] > 1).sum())}
    assert result['verified_accuracy_cells'] == 98 and result['verified_intervals'] == 126
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    evidence = args.root / 'evidence'
    inventory = json.loads((evidence / 'inventory.json').read_text())
    for relative, expected_hash in inventory.items():
        assert digest(args.root / relative) == expected_hash, relative
    expected = json.loads((evidence / 'expected-statistics.json').read_text())
    with np.load(evidence / 'predictions.npz', allow_pickle=False) as data:
        with (evidence / 'final.csv').open() as f:
            manifest_labels = np.array([int(row['label']) for row in csv.DictReader(f)])
        assert np.array_equal(data['labels'], manifest_labels)
        result = reconstruct(data, expected)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    print('PASS: 98 accuracy cells, 126 paired bootstrap intervals, both FP32 references, and inventory hashes.')
    print(json.dumps(result['fp32']))


if __name__ == '__main__':
    main()
