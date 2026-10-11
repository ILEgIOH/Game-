#!/usr/bin/env python3
"""Generates all datapack/resource JSON for Extra Bees from the BEES table.

Run from forestry-extras/:  python3 tools/gen_data.py
"""
import json, os, struct, zlib

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'main', 'resources')
NS = 'extrabees'

# genus -> (english, russian) is not needed; genera are structural taxa under apidae
GENERA = ['metallum', 'gemma', 'materia', 'mixtum']

# id, genus, epithet, outline, body, comb tint, ru name, en name, desc,
# parents (a, b, chance, [conditions]), resource item, wax-comb extras, flower, temp, humidity, glint
def cond_biome(tag): return {'type': 'forestry:biome', 'biome': tag}
def cond_temp(lo, hi): return {'type': 'forestry:temperature', 'min': lo, 'max': hi}
def cond_hum(lo, hi): return {'type': 'forestry:humidity', 'min': lo, 'max': hi}

NETHER = [cond_biome('minecraft:is_nether')]

BEES = [
    dict(id='copper', genus='metallum', epithet='cuprum', outline=0xB4623A, body=0xD98B52, tint=0xC4703F,
         en='Cuprous', ru='Медная', item='minecraft:raw_copper',
         desc='Smells of green patina and old pennies.', parents=('forestry:industrious', 'forestry:meadows', 0.12, [])),
    dict(id='iron', genus='metallum', epithet='ferrum', outline=0x8A8A8A, body=0xC9C2BC, tint=0xBBB2AA,
         en='Ferrous', ru='Железная', item='minecraft:raw_iron',
         desc='Stubborn, heavy and surprisingly hard-working.', parents=('extrabees:copper', 'forestry:steadfast', 0.10, [])),
    dict(id='gold', genus='metallum', epithet='aurum', outline=0xE8B923, body=0xFFD84A, tint=0xF2C230,
         en='Auric', ru='Золотая', item='minecraft:raw_gold', glint=True,
         desc='Every wing-beat glitters.', parents=('extrabees:iron', 'forestry:noble', 0.08, [])),
    dict(id='coal', genus='materia', epithet='carbo', outline=0x2B2B2B, body=0x4A4540, tint=0x3A3632,
         en='Carbonic', ru='Угольная', item='minecraft:coal',
         desc='Leaves sooty footprints on every flower.', parents=('forestry:common', 'forestry:industrious', 0.15, [])),
    dict(id='redstone', genus='materia', epithet='rubrum', outline=0xA00000, body=0xE02B1E, tint=0xD42A1C,
         en='Redstone', ru='Редстоуновая', item='minecraft:redstone',
         desc='Buzzes with a faint electric hum.', parents=('forestry:industrious', 'forestry:tricky', 0.12, [])),
    dict(id='lapis', genus='gemma', epithet='lazuli', outline=0x1C3FA8, body=0x3D6BE0, tint=0x2F55C8,
         en='Lapis', ru='Лазуритовая', item='minecraft:lapis_lazuli',
         desc='Deep blue like a night over the sea.', parents=('forestry:noble', 'forestry:aquatic', 0.10, [])),
    dict(id='diamond', genus='gemma', epithet='adamas', outline=0x2BB7B0, body=0x7FF3EA, tint=0x5CE6DC,
         en='Adamantine', ru='Алмазная', item='minecraft:diamond', glint=True,
         desc='Cuts through everything, including your patience.', parents=('extrabees:gold', 'forestry:imperial', 0.05, [])),
    dict(id='emerald', genus='gemma', epithet='smaragdus', outline=0x118C3F, body=0x41D36B, tint=0x2FBF58,
         en='Verdant Gem', ru='Изумрудная', item='minecraft:emerald', glint=True,
         desc='The villagers will trade anything for it.', parents=('extrabees:diamond', 'forestry:tropical', 0.04, [])),
    dict(id='amethyst', genus='gemma', epithet='amethystus', outline=0x7A4FC4, body=0xB78BF2, tint=0xA06BE0,
         en='Amethyst', ru='Аметистовая', item='minecraft:amethyst_shard', flower='forestry:flower_type_cave',
         desc='Chimes softly when it is happy.', parents=('extrabees:lapis', 'forestry:glacial', 0.07, [cond_biome('c:is_cave')])),
    dict(id='quartz', genus='gemma', epithet='quartzum', outline=0xCFC5BD, body=0xF4EEE8, tint=0xE8DFD6,
         en='Quartz', ru='Кварцевая', item='minecraft:quartz', flower='forestry:flower_type_nether', temp='hellish', hum='arid',
         desc='Born in the nether, pale as bone.', parents=('extrabees:coal', 'forestry:demonic', 0.08, NETHER)),
    dict(id='glowstone', genus='materia', epithet='lucidum', outline=0xC9A12A, body=0xFFE070, tint=0xF5CE55,
         en='Glowing', ru='Светящаяся', item='minecraft:glowstone_dust', flower='forestry:flower_type_nether', temp='hellish', hum='arid',
         desc='Works the night shift without a lamp.', parents=('extrabees:redstone', 'extrabees:quartz', 0.07, NETHER)),
    dict(id='blaze', genus='materia', epithet='flammeus', outline=0xD96A00, body=0xFFB020, tint=0xF28A10,
         en='Blazing', ru='Пылающая', item='minecraft:blaze_powder', flower='forestry:flower_type_nether', temp='hellish', hum='arid',
         desc='Do not pet.', parents=('forestry:demonic', 'forestry:valiant', 0.08, NETHER)),
    dict(id='netherite', genus='metallum', epithet='antiquus', outline=0x3B2F2F, body=0x6B5A55, tint=0x52423E,
         en='Ancient', ru='Незеритовая', item='minecraft:netherite_scrap', flower='forestry:flower_type_nether', temp='hellish', hum='arid', glint=True,
         desc='Remembers a world before this one.', parents=('extrabees:diamond', 'forestry:demonic', 0.02, NETHER)),
    dict(id='slime', genus='materia', epithet='gelatinum', outline=0x4AA83A, body=0x7FD96B, tint=0x6CC95A,
         en='Gelatinous', ru='Слизистая', item='minecraft:slime_ball', hum='damp',
         desc='Bounces in place when excited.', parents=('forestry:marshy', 'forestry:common', 0.10, [cond_biome('c:is_swamp')])),
    dict(id='prismarine', genus='gemma', epithet='prismaticus', outline=0x3A9C91, body=0x78D6C6, tint=0x5CC2B2,
         en='Prismatic Reef', ru='Призмариновая', item='minecraft:prismarine_shard', flower='forestry:flower_type_sea', hum='damp',
         desc='Hums the sound of distant guardians.', parents=('forestry:aquatic', 'forestry:imperial', 0.08, [cond_hum('damp', 'damp')])),
]


NETHER_T = dict(temp='hellish', hum='arid')
COMPAT = [
    # Create
    dict(pack='create', id='zinc', genus='metallum', epithet='zincum', outline=0x7E8F8C, body=0xB8C9C5, tint=0xA9BDB9,
         en='Zincic', ru='Цинковая', item='create:raw_zinc', desc='Quiet, cold and very good at conducting gossip.',
         parents=('extrabees:copper', 'forestry:rural', 0.10, [])),
    dict(pack='create', id='brass', genus='metallum', epithet='orichalcum', outline=0xB8872E, body=0xE8C060, tint=0xD6A940,
         en='Brassy', ru='Латунная', item='create:brass_ingot', desc='Gears turn better when it hums.',
         parents=('extrabees:zinc', 'extrabees:copper', 0.08, [])),
    dict(pack='create', id='andesite', genus='mixtum', epithet='andesitum', outline=0x7A7A76, body=0xA9A9A3, tint=0x9A9A94,
         en='Andesite', ru='Андезитовая', item='create:andesite_alloy', desc='A hobbyist engineer in a bee suit.',
         parents=('forestry:common', 'forestry:steadfast', 0.12, [])),
    # The Aether
    dict(pack='aether', id='ambrosium', genus='mixtum', epithet='ambrosius', outline=0xD8B94A, body=0xFFE890, tint=0xF2D468,
         en='Ambrosial', ru='Амброзиевая', item='aether:ambrosium_shard', desc='Floats a little when nobody is looking.',
         parents=('forestry:cultivated', 'extrabees:gold', 0.10, [])),
    dict(pack='aether', id='zanite', genus='gemma', epithet='zanites', outline=0x6A4FC4, body=0xA68BF2, tint=0x9070E0, glint=True,
         en='Zanitic', ru='Занитовая', item='aether:zanite_gemstone', desc='Gets stronger the more it is used.',
         parents=('extrabees:ambrosium', 'extrabees:diamond', 0.06, [])),
    # Mystical Agriculture
    dict(pack='mysticalagriculture', id='inferium', genus='mixtum', epithet='inferium', outline=0x4C8F2E, body=0x86D063, tint=0x6FBF48,
         en='Inferium', ru='Инфериумная', item='mysticalagriculture:inferium_essence', desc='Grows crops by staring at them.',
         parents=('forestry:diligent', 'forestry:common', 0.20, [])),
    dict(pack='mysticalagriculture', id='prosperity', genus='mixtum', epithet='prosperus', outline=0x2FA882, body=0x6FE6C0, tint=0x4DD4A8, glint=True,
         en='Prosperous', ru='Процветающая', item='mysticalagriculture:prosperity_shard', desc='Smells like a good harvest.',
         parents=('extrabees:inferium', 'extrabees:emerald', 0.07, [])),
    # DivineRPG
    dict(pack='divinerpg', id='arlemite', genus='gemma', epithet='arlemitus', outline=0x2E7AB8, body=0x6FB8F0, tint=0x4F9DDC,
         en='Arlemite', ru='Арлемитовая', item='divinerpg:arlemite_ingot', desc='Blue and unbothered.',
         parents=('extrabees:iron', 'extrabees:lapis', 0.08, [])),
    dict(pack='divinerpg', id='realmite', genus='gemma', epithet='realmitus', outline=0xC43A3A, body=0xF07878, tint=0xDC5858,
         en='Realmite', ru='Реалмитовая', item='divinerpg:realmite_ingot', desc='Takes itself very seriously.',
         parents=('extrabees:arlemite', 'extrabees:diamond', 0.05, [])),
    dict(pack='divinerpg', id='rupee', genus='gemma', epithet='rupeus', outline=0x2FB04A, body=0x7FE88C, tint=0x58D468,
         en='Rupee', ru='Рупиевая', item='divinerpg:rupee_ingot', desc='Counts everything twice.',
         parents=('extrabees:emerald', 'forestry:noble', 0.06, [])),
    dict(pack='divinerpg', id='bloodgem', genus='gemma', epithet='sanguineus', outline=0x8A0F1C, body=0xD22A3A, tint=0xB81E2E, flower='forestry:flower_type_nether', **NETHER_T,
         en='Bloodgem', ru='Кровавая', item='divinerpg:bloodgem', desc='Do not ask where the honey comes from.',
         parents=('extrabees:redstone', 'forestry:demonic', 0.07, NETHER)),
    dict(pack='divinerpg', id='torridite', genus='materia', epithet='torridus', outline=0xC24A0A, body=0xFF8A30, tint=0xE86A18, flower='forestry:flower_type_nether', glint=True, **NETHER_T,
         en='Torrid', ru='Торридитовая', item='divinerpg:torridite_ingot', desc='Burning with ambition.',
         parents=('extrabees:realmite', 'extrabees:bloodgem', 0.03, NETHER)),
]
COMPAT_MODS = {'create': 'Create', 'aether': 'The Aether', 'mysticalagriculture': 'Mystical Agriculture', 'divinerpg': 'DivineRPG'}
BEES += COMPAT

def write(path, data, raw=False):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, 'w', encoding='utf-8') as f:
        f.write(data if raw else json.dumps(data, indent=2, ensure_ascii=False) + '\n')

def png(path, w, h, px):
    raw = b''.join(b'\x00' + b''.join(struct.pack('4B', *px(x, y)) for x in range(w)) for y in range(h))
    def chunk(t, d):
        c = struct.pack('>I', len(d)) + t + d
        return c + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    data = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>2I5B', w, h, 8, 6, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b'')
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'wb').write(data)

import random

def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)

def rgb(h): return ((h >> 16) & 255, (h >> 8) & 255, h & 255)

MOTIF = {'metallum': 'streak', 'gemma': 'facet', 'materia': 'dots', 'mixtum': 'ring'}

def comb_texture(b):
    base, accent, rim = rgb(b['tint']), rgb(b['outline']), rgb(b['body'])
    rnd = random.Random(b['id'])
    px = [[(0, 0, 0, 0)] * 16 for _ in range(16)]
    def inside(x, y):
        dx, dy = abs(x - 7.5), abs(y - 7.5)
        return dx <= 7 and dy <= 6.5 and dx + dy <= 11
    def edge(x, y):
        return any(not inside(x + a, y + c) for a, c in ((1, 0), (-1, 0), (0, 1), (0, -1)))
    for y in range(16):
        for x in range(16):
            if not inside(x, y): continue
            if edge(x, y):
                px[y][x] = shade(base, 0.45) + (255,); continue
            off = 2 if (y // 4) % 2 else 0
            wall = y % 4 == 0 or (x + off) % 4 == 0
            cell = ((x + off) // 4 + y // 4) % 2
            col = shade(base, 0.72) if wall else (shade(base, 1.12) if cell else base)
            if x + y < 11 and not wall: col = shade(col, 1.12)  # top-left light
            px[y][x] = col + (255,)
    m = MOTIF[b['genus']]
    def put(x, y, c):
        if 0 < x < 15 and 0 < y < 15 and inside(x, y) and not edge(x, y): px[y][x] = c + (255,)
    hi = shade(rim, 1.15)
    spots = [(rnd.randint(3, 12), rnd.randint(3, 12)) for _ in range(5)]
    for (x, y) in spots:
        if m == 'streak':
            for i in range(3): put(x + i, y, accent); put(x + i, y - 1, hi)
        elif m == 'facet':
            put(x, y, hi); put(x + 1, y, accent); put(x, y + 1, accent); put(x + 1, y + 1, shade(accent, 0.7))
        elif m == 'dots':
            put(x, y, accent); put(x + 1, y, hi)
        else:
            for dx, dy in ((0, 1), (1, 0), (2, 1), (1, 2)): put(x + dx, y + dy, accent)
            put(x + 1, y + 1, hi)
    if b.get('glint'):
        for (x, y) in spots[:2]: put(x, y, (255, 255, 255)); put(x + 1, y, (255, 255, 255))
    return px

def main():
    for g in GENERA:
        write(f'data/{NS}/taxon/{g}.json', {'parent': 'apidae', 'name': g, 'rank': 'genus'})

    en, ru = {}, {}
    comb_ids = []
    for b in BEES:
        bid = b['id']
        comb = f'{bid}_comb'
        comb_ids.append(comb)
        genome = {
            'forestry:flower_type': {'value': b.get('flower', 'forestry:flower_type_vanilla')},
            'forestry:lifespan': {'value': 40},
            'forestry:speed': {'value': 0.6},
        }
        sp = {
            'authority': 'Extra Bees',
            'body': b['body'],
            'dominant': False,
            'genome': genome,
            'genus': b['genus'],
            'outline': b['outline'],
            'products': [{'chance': 0.30, 'item': f'{NS}:{comb}'}],
            'specialties': [{'chance': 0.15, 'item': b['item']}],
            'species': b['epithet'],
        }
        if b.get('glint'): sp['glint'] = True
        if b.get('temp'): sp['temperature'] = b['temp']
        if b.get('hum'): sp['humidity'] = b['hum']
        droot = f'compat/{b["pack"]}/data' if b.get('pack') else 'data'
        write(f'{droot}/{NS}/bee_species/{bid}.json', sp)

        a, c, chance, conds = b['parents']
        mut = {'type': 'forestry:bee_mutation', 'id': f'{NS}:bee_mutation/{bid}', 'chance': chance, 'first': a, 'second': c, 'result': f'{NS}:{bid}'}
        if conds: mut['conditions'] = conds
        write(f'{droot}/{NS}/recipe/bee_mutation/{bid}.json', mut)

        write(f'{droot}/{NS}/recipe/centrifuge/{comb}.json', {
            'type': 'forestry:centrifuge',
            'id': f'{NS}:centrifuge/{comb}',
            'input': {'item': f'{NS}:{comb}'},
            'products': [{'chance': 1.0, 'item': 'forestry:beeswax'}, {'chance': 0.4, 'item': b['item']}],
            'time': 20,
        })
        write(f'assets/{NS}/models/item/{comb}.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'{NS}:item/comb/{bid}'}})
        tex = comb_texture(b)
        png(f'assets/{NS}/textures/item/comb/{bid}.png', 16, 16, lambda x, y, t=tex: t[y][x])

        en[f'allele.{NS}.bee_species.{bid}'] = b['en']
        en[f'allele.{NS}.bee_species.{bid}.desc'] = f'"{b["desc"]}"|Extra Bees'
        en[f'item.{NS}.{comb}'] = f'{b["en"]} Comb'
        ru[f'allele.{NS}.bee_species.{bid}'] = b['ru']
        ru[f'allele.{NS}.bee_species.{bid}.desc'] = f'"{b["desc"]}"|Extra Bees'
        ru[f'item.{NS}.{comb}'] = f'Сота: {b["ru"].lower()}'

    en[f'itemGroup.{NS}.main'] = 'Extra Bees'
    ru[f'itemGroup.{NS}.main'] = 'Extra Bees'
    write(f'assets/{NS}/lang/en_us.json', en)
    write(f'assets/{NS}/lang/ru_ru.json', ru)
    # lets Forestry treat our combs as combs (crates, tooltips, etc.)
    write('data/forestry/tags/item/combs.json', {'replace': False, 'values': [f'{NS}:{c}' for c in comb_ids]})
    
    for pid, title in COMPAT_MODS.items():
        write(f'compat/{pid}/pack.mcmeta', {'pack': {'description': f'Extra Bees: {title} bees', 'pack_format': 48}})
    # Java side reads this list
    java = 'package extrabees;\n\n// generated by tools/gen_data.py, do not edit\nfinal class GeneratedCombs {\n'
    java += '\tstatic final String[] IDS = {\n' + ''.join(f'\t\t"{c}",\n' for c in comb_ids) + '\t};\n'
    java += '\tstatic final String[][] PACKS = {\n' + ''.join(f'\t\t{{"{k}", "{v}"}},\n' for k, v in COMPAT_MODS.items()) + '\t};\n'
    java += '}\n'
    full = os.path.join(ROOT, '..', 'java', 'extrabees', 'GeneratedCombs.java')
    open(full, 'w').write(java)
    print(f'{len(BEES)} bees generated')

main()
