#!/usr/bin/env python3
"""Checks that every model/texture referenced by blockstates and models exists, and every block has loot, item model and lang."""
import json, os, glob, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'main', 'resources')
R = os.path.join(ROOT, 'assets', 'extrabees')
have_models = {os.path.relpath(p, R + '/models')[:-5] for p in glob.glob(R + '/models/**/*.json', recursive=True)}
have_tex = {os.path.relpath(p, R + '/textures')[:-4] for p in glob.glob(R + '/textures/**/*.png', recursive=True)}
bad = 0

def check(ref, have, what, where):
    global bad
    ns, _, path = ref.partition(':')
    if ns == 'extrabees' and path not in have:
        print('MISSING', what, ref, 'in', where); bad += 1

def walk(o, where):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ('model', 'parent') and isinstance(v, str): check(v, have_models, 'model', where)
            elif k == 'textures' and isinstance(v, dict):
                for t in v.values():
                    if isinstance(t, str) and not t.startswith('#'): check(t, have_tex, 'texture', where)
            else: walk(v, where)
    elif isinstance(o, list):
        for i in o: walk(i, where)

for p in glob.glob(R + '/blockstates/*.json') + glob.glob(R + '/models/**/*.json', recursive=True):
    walk(json.load(open(p)), os.path.relpath(p, R))
lang = json.load(open(R + '/lang/en_us.json'))
names = [os.path.basename(p)[:-5] for p in glob.glob(R + '/blockstates/*.json')]
for n in names:
    for what, path in (('loot', f'{ROOT}/data/extrabees/loot_table/blocks/{n}.json'), ('item model', f'{R}/models/item/{n}.json')):
        if not os.path.exists(path): print('MISSING', what, n); bad += 1
    if f'block.extrabees.{n}' not in lang: print('MISSING lang', n); bad += 1
print('blocks:', len(names), 'models:', len(have_models), 'textures:', len(have_tex), 'problems:', bad)
sys.exit(1 if bad else 0)
