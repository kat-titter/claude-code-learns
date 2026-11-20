#!/usr/bin/env python3
"""Find columns that only say which group a row came from: constant (or nearly) inside every group, different between
groups. In an imaging table these are acquisition format (frame size, bit depth, pixel size), not biology; in any table
they let a classifier "name the group" with nothing learned. Run it before comparing inputs or claiming a signal.

Usage: constant_within_group.py TABLE [TABLE ...] --group COL [--near 0.01] [--prefix Metadata_]
  TABLE: .csv, .tsv or .parquet (several files are stacked; a directory takes every .parquet/.csv inside, recursively)
  --group: the column that holds the group (lab, site, batch, instrument)
  --near: also list columns whose within-group variance is under this share of their total variance (default 1%)
  --prefix: skip columns starting with this (identifiers), repeatable
Prints the exact-constant columns (how many distinct values across groups, which groups share a value) and the
near-constant ones. Exit status 1 when any exact-constant column is found, so a pipeline can stop and ask.
"""
import argparse, glob, os, sys
if sys.argv[1:2] in (['-h'], ['--help']):
    print(__doc__); sys.exit(0)
try:
    import numpy as np
    import pandas as pd
except ImportError as e:
    raise SystemExit(f'{e.name} missing: pip install numpy pandas (or run with the project venv that has them)')

ap = argparse.ArgumentParser()
ap.add_argument('tables', nargs='+'); ap.add_argument('--group', required=True)
ap.add_argument('--near', type=float, default=0.01); ap.add_argument('--prefix', action='append', default=['Metadata_'])
a = ap.parse_args()

files = []
for t in a.tables:
    if os.path.isdir(t):
        files += sorted(glob.glob(os.path.join(t, '**', '*.parquet'), recursive=True) + glob.glob(os.path.join(t, '**', '*.csv'), recursive=True))
    else:
        files.append(t)
read = lambda f: pd.read_parquet(f) if f.endswith('.parquet') else pd.read_csv(f, sep='\t' if f.endswith('.tsv') else ',')
d = pd.concat([read(f) for f in files], ignore_index=True)
g = d[a.group].astype(str)
cols = [c for c in d.columns if c != a.group and not any(c.startswith(p) for p in a.prefix)]
X = d[cols].apply(pd.to_numeric, errors='coerce')
X = X.loc[:, X.notna().any() & (X.nunique() > 1)]
groups = sorted(g.unique())
print(f'{len(d):,} rows, {len(groups)} groups in {a.group!r}, {X.shape[1]:,} numeric columns that vary at all')

within = X.groupby(g).nunique(dropna=True)
exact = [c for c in X.columns if (within[c] <= 1).all()]
var_total = X.var(); var_within = X.groupby(g).var().mean()
share = (var_within / var_total).replace([np.inf, -np.inf], np.nan)
near = [c for c in X.columns if c not in exact and share.get(c, np.nan) < a.near]

if exact:
    print(f'\n{len(exact)} column(s) constant inside every group but not across groups (they only say which group):')
    for c in exact:
        v = X[c].groupby(g).first()
        shared = {val: [k for k in v.index if v[k] == val] for val in v.unique()}
        same = '; '.join(f'{len(ks)} share {val:g}' for val, ks in shared.items() if len(ks) > 1)
        print(f'  {c}: {v.nunique()} values across {len(groups)} groups' + (f' ({same})' if same else ''))
else:
    print('\nno column is constant inside every group')
if near:
    print(f'\n{len(near)} column(s) with within-group variance under {a.near:.0%} of the total (check what they measure):')
    for c in sorted(near, key=lambda c: share[c])[:40]:
        print(f'  {c}: within-group share {share[c]:.4f}')
sys.exit(1 if exact else 0)
