#!/usr/bin/env python3
"""Generates all data/assets/java for the Extra Trees module from the TREES table.

Run from forestry-extras/:  python3 tools/gen_trees.py
Needs Pillow and the vanilla 1.21.1 client jar (path in VANILLA_JAR, or env VANILLA_JAR).
Textures are luminance recolours of the vanilla oak textures (private/hobby use).
"""
import io, json, os, re, sys, zipfile

from PIL import Image

NS = 'extrabees'
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'main')
RES = os.path.join(ROOT, 'resources')
JAVA = os.path.join(ROOT, 'java', 'extrabees', 'trees')
VANILLA_JAR = os.environ.get('VANILLA_JAR', '/root/.gradle/caches/neoformruntime/artifacts/minecraft_1.21.1_client.jar')

# new genera: name -> parent family (families already exist in Forestry's taxonomy)
GENERA = {'fraxinus': 'oleaceae', 'cedrus': 'pinaceae'}

# shape: OVAL | CONE | COLUMN
TREES = [
    dict(id='ash', genus='fraxinus', species='excelsior', en='Ash', ru='Ясень', ru_gen='ясеня',
         desc='A broad, tough hardwood. Good for tool handles and long winters.',
         shape='OVAL', base_height=7, height_var=4, radius=3, escritoire=0x8A847A, rarity=0.003,
         temperature=None, humidity=None, height=1.0, maturation=None,
         bark=(0x3D3A34, 0x8A847A), planks=(0x9C8A6A, 0xD8C8A0), stripped=(0xA8946C, 0xE0D0A4), leaf=(0x2F5F22, 0x7AA83E),
         parents=('forestry:oak', 'forestry:elm', 0.08)),
    dict(id='cedar', genus='cedrus', species='libani', en='Cedar', ru='Кедр', ru_gen='кедра',
         desc='Tall and aromatic. Its wood keeps moths away and chests smelling pleasant.',
         shape='CONE', base_height=10, height_var=6, radius=3, escritoire=0x9A5A3E, rarity=0.002,
         temperature='cold', humidity=None, height=1.25, maturation=None,
         bark=(0x4A2A1E, 0x9A5A3E), planks=(0x8A4A30, 0xC87A50), stripped=(0x9A5636, 0xD88A5C), leaf=(0x1B4636, 0x3F7F5A),
         parents=('forestry:fir', 'forestry:pine', 0.07)),
    dict(id='aspen', genus='populus', species='tremula', en='Aspen', ru='Осина', ru_gen='осины',
         desc='Slender and pale. Its leaves tremble at the slightest breeze.',
         shape='COLUMN', base_height=8, height_var=5, radius=2, escritoire=0xD8D8CC, rarity=0.003,
         temperature=None, humidity='damp', height=1.0, maturation=None,
         bark=(0x6E6E64, 0xD8D8CC), planks=(0xC8BFA0, 0xEFE6C8), stripped=(0xD0C7A8, 0xF4ECD0), leaf=(0x5E7E1C, 0xC0C83A),
         parents=('forestry:poplar', 'forestry:birch', 0.08)),
]

KINDS = ['log', 'stripped_log', 'wood', 'stripped_wood', 'planks', 'stairs', 'slab', 'fence', 'fence_gate',
         'door', 'trapdoor', 'button', 'pressure_plate', 'leaves']
EN_KIND = dict(log='Log', stripped_log='Stripped Log', wood='Wood', stripped_wood='Stripped Wood', planks='Planks', stairs='Stairs',
               slab='Slab', fence='Fence', fence_gate='Fence Gate', door='Door', trapdoor='Trapdoor', button='Button',
               pressure_plate='Pressure Plate', leaves='Leaves')
RU_KIND = dict(log='Бревно {}', stripped_log='Обтёсанное бревно {}', wood='Древесина {}', stripped_wood='Обтёсанная древесина {}',
               planks='Доски {}', stairs='Ступени {}', slab='Плита {}', fence='Забор {}', fence_gate='Калитка {}',
               door='Дверь {}', trapdoor='Люк {}', button='Кнопка {}', pressure_plate='Нажимная плита {}', leaves='Листва {}')


def block_name(tid, kind):
    return f'stripped_{tid}_{kind[9:]}' if kind.startswith('stripped_') else f'{tid}_{kind}'


def write(path, data, raw=False):
    full = os.path.join(RES, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(data if raw else json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def rgb(h): return ((h >> 16) & 255, (h >> 8) & 255, h & 255)


def recolor(img, pal):
    """map the luminance of a vanilla texture onto a dark->light ramp, keep alpha"""
    img = img.convert('RGBA')
    px = img.load()
    lums = [(0.299 * r + 0.587 * g + 0.114 * b) for x in range(img.width) for y in range(img.height)
            for (r, g, b, a) in [px[x, y]] if a > 0]
    lo, hi = min(lums), max(lums)
    span = max(hi - lo, 1)
    d, l = rgb(pal[0]), rgb(pal[1])
    out = Image.new('RGBA', img.size)
    op = out.load()
    for x in range(img.width):
        for y in range(img.height):
            r, g, b, a = px[x, y]
            if a == 0:
                op[x, y] = (0, 0, 0, 0); continue
            t = ((0.299 * r + 0.587 * g + 0.114 * b) - lo) / span
            op[x, y] = (int(d[0] + (l[0] - d[0]) * t), int(d[1] + (l[1] - d[1]) * t), int(d[2] + (l[2] - d[2]) * t), a)
    return out


def xform(text, tid):
    t = text
    t = t.replace('minecraft:oak_logs', f'{NS}:{tid}_logs')
    t = re.sub(r'minecraft:(block|item)/stripped_oak', rf'{NS}:\1/stripped_{tid}', t)
    t = re.sub(r'minecraft:(block|item)/oak', rf'{NS}:\1/{tid}', t)
    t = t.replace('minecraft:stripped_oak_', f'{NS}:stripped_{tid}_')
    t = t.replace('minecraft:oak_', f'{NS}:{tid}_')
    return t


def main():
    z = zipfile.ZipFile(VANILLA_JAR)
    def vtext(p): return z.read(p).decode('utf-8')
    def vimg(p): return Image.open(io.BytesIO(z.read(p)))

    en, ru = {}, {}
    block_tags = {}  # tag -> list of ids
    def tag(name, bid):
        block_tags.setdefault(name, []).append(f'{NS}:{bid}')

    mut_lines = []
    for T in TREES:
        tid = T['id']
        # ---- blockstates / models / loot / recipes by transforming vanilla oak files ----
        vanilla_blocks = {'log': 'oak_log', 'stripped_log': 'stripped_oak_log', 'wood': 'oak_wood', 'stripped_wood': 'stripped_oak_wood',
                          'planks': 'oak_planks', 'stairs': 'oak_stairs', 'slab': 'oak_slab', 'fence': 'oak_fence', 'fence_gate': 'oak_fence_gate',
                          'door': 'oak_door', 'trapdoor': 'oak_trapdoor', 'button': 'oak_button', 'pressure_plate': 'oak_pressure_plate',
                          'leaves': 'oak_leaves'}
        for kind, vname in vanilla_blocks.items():
            bname = block_name(tid, kind)
            write(f'assets/{NS}/blockstates/{bname}.json', xform(vtext(f'assets/minecraft/blockstates/{vname}.json'), tid), raw=True)
            lootsrc = vtext(f'data/minecraft/loot_table/blocks/{vname}.json')
            if kind == 'leaves':
                d = json.loads(xform(lootsrc, tid))
                for pool in d['pools']:
                    for entry in pool['entries']:
                        if entry.get('type') == 'minecraft:alternatives':
                            entry['children'] = [c for c in entry['children'] if not c.get('name', '').endswith('_sapling')]
                write(f'data/{NS}/loot_table/blocks/{bname}.json', d)
            else:
                write(f'data/{NS}/loot_table/blocks/{bname}.json', xform(lootsrc, tid), raw=True)
            item_model = f'assets/minecraft/models/item/{vname}.json'
            write(f'assets/{NS}/models/item/{bname}.json', xform(vtext(item_model), tid), raw=True)
            try:
                write(f'data/{NS}/recipe/{bname}.json', xform(vtext(f'data/minecraft/recipe/{vname}.json'), tid), raw=True)
            except KeyError:
                pass
        # block models referenced by the blockstates
        for n in z.namelist():
            m = re.match(r'assets/minecraft/models/block/((stripped_)?oak(?:_[a-z_]*)?)\.json$', n)
            if m and not any(s in m.group(1) for s in ('sign', 'hanging', 'sapling')):
                newname = xform('minecraft:block/' + m.group(1), tid).split('/')[-1]
                write(f'assets/{NS}/models/block/{newname}.json', xform(z.read(n).decode('utf-8'), tid), raw=True)
        # leaves item model is `parent: block/<leaves>`, already handled by xform of item model
        # sapling models (used through Forestry's client API)
        write(f'assets/{NS}/models/block/sapling/{tid}.json', {'parent': 'minecraft:block/cross', 'textures': {'cross': f'{NS}:block/{tid}_sapling'}})
        write(f'assets/{NS}/models/item/sapling/{tid}.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'{NS}:block/{tid}_sapling'}})

        # ---- textures ----
        def tex(src, dst, pal, kind='block'):
            img = recolor(vimg(f'assets/minecraft/textures/{kind}/{src}.png'), pal)
            full = os.path.join(RES, f'assets/{NS}/textures/{kind}/{dst}.png')
            os.makedirs(os.path.dirname(full), exist_ok=True)
            img.save(full)
        tex('oak_log', f'{tid}_log', T['bark']); tex('oak_log_top', f'{tid}_log_top', T['planks'])
        tex('stripped_oak_log', f'stripped_{tid}_log', T['stripped']); tex('stripped_oak_log_top', f'stripped_{tid}_log_top', T['planks'])
        tex('oak_planks', f'{tid}_planks', T['planks'])
        tex('oak_leaves', f'{tid}_leaves', T['leaf']); tex('oak_sapling', f'{tid}_sapling', T['leaf'])
        tex('oak_door_top', f'{tid}_door_top', T['planks']); tex('oak_door_bottom', f'{tid}_door_bottom', T['planks'])
        tex('oak_trapdoor', f'{tid}_trapdoor', T['planks']); tex('oak_door', f'{tid}_door', T['planks'], 'item')

        # ---- lang ----
        for kind in KINDS:
            bname = block_name(tid, kind)
            en[f'block.{NS}.{bname}'] = f'{T["en"]} {EN_KIND[kind]}' if not kind.startswith('stripped') else f'Stripped {T["en"]} {EN_KIND[kind][9:]}'
            ru[f'block.{NS}.{bname}'] = RU_KIND[kind].format(T['ru_gen'])
        en[f'allele.{NS}.tree_species.{tid}'] = T['en']; ru[f'allele.{NS}.tree_species.{tid}'] = T['ru']
        en[f'allele.{NS}.tree_species.{tid}.desc'] = f'{T["desc"]}|Extra Trees'; ru[f'allele.{NS}.tree_species.{tid}.desc'] = f'{T["desc"]}|Extra Trees'

        # ---- tags ----
        logs = ['log', 'stripped_log', 'wood', 'stripped_wood']
        for k in logs:
            tag(f'{tid}_logs', block_name(tid, k)); tag('logs', block_name(tid, k)); tag('logs_that_burn', block_name(tid, k)); tag('mineable/axe', block_name(tid, k))
        for k, tg in (('planks', 'planks'), ('stairs', 'wooden_stairs'), ('slab', 'wooden_slabs'), ('fence', 'wooden_fences'),
                      ('fence_gate', 'fence_gates'), ('door', 'wooden_doors'), ('trapdoor', 'wooden_trapdoors'),
                      ('button', 'wooden_buttons'), ('pressure_plate', 'wooden_pressure_plates')):
            tag(tg, block_name(tid, k)); tag('mineable/axe', block_name(tid, k))
        tag('fences', block_name(tid, 'fence')); tag('doors', block_name(tid, 'door')); tag('wooden_doors', block_name(tid, 'door'))
        tag('leaves', block_name(tid, 'leaves')); tag('mineable/hoe', block_name(tid, 'leaves'))
        tag('planks', block_name(tid, 'planks'))

        # ---- species data ----
        genome = {'forestry:height': {'value': T['height']}}
        if T.get('maturation'): genome['forestry:maturation'] = {'value': T['maturation']}
        genome['forestry:saplings'] = {'dominant': True, 'value': 0.035}
        genome['forestry:sappiness'] = {'dominant': True, 'value': 0.2}
        sp = {'dominant': True, 'escritoire_color': T['escritoire'], 'genome': genome, 'genus': T['genus'], 'rarity': T['rarity'], 'species': T['species']}
        if T['temperature']: sp['temperature'] = T['temperature']
        if T['humidity']: sp['humidity'] = T['humidity']
        write(f'data/{NS}/tree_species/{tid}.json', sp)
        a, b, chance = T['parents']
        write(f'data/{NS}/recipe/tree_mutation/{tid}.json', {'type': 'forestry:tree_mutation', 'id': f'{NS}:tree_mutation/{tid}',
                                                              'chance': chance, 'first': a, 'second': b, 'result': f'{NS}:{tid}'})

    for g, parent in GENERA.items():
        write(f'data/{NS}/taxon/{g}.json', {'parent': parent, 'name': g, 'rank': 'genus'})

    item_tags = {k: v for k, v in block_tags.items() if not k.startswith('mineable/')}
    for name, ids in block_tags.items():
        ns_tag = 'minecraft' if not name.endswith('_logs') else NS
        write(f'data/{ns_tag}/tags/block/{name}.json', {'replace': False, 'values': sorted(set(ids))})
    for name, ids in item_tags.items():
        ns_tag = 'minecraft' if not name.endswith('_logs') else NS
        write(f'data/{ns_tag}/tags/item/{name}.json', {'replace': False, 'values': sorted(set(ids))})

    # ---- lang merge (bees already wrote en_us/ru_ru; merge) ----
    for fname, d in (('en_us', en), ('ru_ru', ru)):
        path = os.path.join(RES, f'assets/{NS}/lang/{fname}.json')
        base = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else {}
        base.update(d)
        base[f'itemGroup.{NS}.trees'] = 'Extra Trees'
        write(f'assets/{NS}/lang/{fname}.json', base)

    # ---- java ----
    os.makedirs(JAVA, exist_ok=True)
    j = 'package extrabees.trees;\n\n// generated by tools/gen_trees.py, do not edit\nfinal class GeneratedTrees {\n'
    j += '\tstatic final TreeDef[] DEFS = {\n'
    for T in TREES:
        j += (f'\t\tnew TreeDef("{T["id"]}", "{T["genus"]}", "{T["species"]}", TreeDef.Shape.{T["shape"]}, {T["base_height"]}, '
              f'{T["height_var"]}, {T["radius"]}, 0x{T["escritoire"]:06X}, 0x{rgb_to_int(T["leaf"][1]):06X}),\n')
    j += '\t};\n}\n'
    open(os.path.join(JAVA, 'GeneratedTrees.java'), 'w').write(j)
    print(f'{len(TREES)} trees generated')


def rgb_to_int(v): return v


main()
