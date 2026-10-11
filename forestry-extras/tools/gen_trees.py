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
GENERA = {'fraxinus': 'oleaceae', 'cedrus': 'pinaceae', 'alnus': 'betulaceae', 'corylus': 'betulaceae', 'carpinus': 'betulaceae',
          'crataegus': 'rosaceae', 'sorbus': 'rosaceae', 'juniperus': 'cupressaceae', 'cupressus': 'cupressaceae',
          'aesculus': 'sapindaceae', 'eucalyptus': 'myrtaceae', 'ilex': 'aquifoliaceae', 'taxus': 'taxaceae',
          'ostrya': 'betulaceae', 'syringa': 'oleaceae', 'tsuga': 'pinaceae', 'pseudotsuga': 'pinaceae', 'taxodium': 'cupressaceae',
          'thuja': 'cupressaceae', 'robinia': 'fabaceae', 'laburnum': 'fabaceae', 'gleditsia': 'fabaceae', 'carya': 'juglandaceae',
          'cinnamomum': 'lauraceae', 'laurus': 'lauraceae', 'zelkova': 'ulmaceae', 'celtis': 'ulmaceae', 'azadirachta': 'meliaceae',
          'ficus': 'moraceae', 'morus': 'moraceae', 'cydonia': 'rosaceae', 'mespilus': 'rosaceae'}
# taxa above genus that Forestry does not have yet: name -> parent (rank is derived from the parent)
EXTRA_TAXA = {'aquifoliales': 'magnoliopsida', 'aquifoliaceae': 'aquifoliales', 'taxaceae': '%CUPRESSALES%', 'moraceae': '%ROSALES%'}

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

def tree(id, genus, species, en, ru, ru_gen, desc, shape, base, var, radius, color, bark, planks, stripped, leaf, parents,
         rarity=0.003, temperature=None, humidity=None, height=1.0):
    return dict(id=id, genus=genus, species=species, en=en, ru=ru, ru_gen=ru_gen, desc=desc, shape=shape, base_height=base, height_var=var,
                radius=radius, escritoire=color, rarity=rarity, temperature=temperature, humidity=humidity, height=height, maturation=None,
                bark=bark, planks=planks, stripped=stripped, leaf=leaf, parents=parents)

TREES += [
    tree('alder', 'alnus', 'glutinosa', 'Alder', 'Ольха', 'ольхи', 'Loves wet feet. Its wood turns red when cut.', 'OVAL', 6, 4, 3, 0x5A4A3A,
         (0x2E2620, 0x6E5A48), (0xB07A50, 0xE0AE7C), (0xBC8658, 0xEBB886), (0x244A22, 0x5E9438), ('forestry:birch', 'forestry:willow', 0.08), humidity='damp'),
    tree('hazel', 'corylus', 'avellana', 'Hazel', 'Лещина', 'лещины', 'A bushy little tree, forever shedding nuts into the grass.', 'OVAL', 4, 3, 2, 0x8A6A44,
         (0x4A3826, 0x9A7A52), (0xC8A06A, 0xEEC890), (0xD0A870, 0xF2D09A), (0x3E6E26, 0x86B040), ('forestry:birch', 'extrabees:alder', 0.08)),
    tree('hornbeam', 'carpinus', 'betulus', 'Hornbeam', 'Граб', 'граба', 'Dense, hard wood. Hedges made of it outlast their gardeners.', 'OVAL', 7, 4, 3, 0x909088,
         (0x504E48, 0xA6A49A), (0xD0C09C, 0xF0E4C0), (0xD8C8A4, 0xF4E8C8), (0x2C5A24, 0x6A9C3C), ('forestry:beech', 'forestry:birch', 0.07)),
    tree('hawthorn', 'crataegus', 'monogyna', 'Hawthorn', 'Боярышник', 'боярышника', 'Thorny and stubborn, with blossoms that smell faintly of trouble.', 'OVAL', 4, 3, 2, 0xD8A0A8,
         (0x3C3028, 0x806C58), (0xB89068, 0xE8C090), (0xC49A70, 0xF0CA9A), (0x2A5624, 0x6EA040), ('forestry:plum', 'forestry:pear', 0.07)),
    tree('rowan', 'sorbus', 'aucuparia', 'Rowan', 'Рябина', 'рябины', 'Wards off bad luck, and sometimes bad bees.', 'OVAL', 5, 3, 2, 0xC8402C,
         (0x6A6058, 0xB8AEA2), (0xC09468, 0xEAC692), (0xCA9E70, 0xF2D09C), (0x486A24, 0xC09A38), ('extrabees:hawthorn', 'forestry:birch', 0.07), temperature='cold'),
    tree('juniper', 'juniperus', 'communis', 'Juniper', 'Можжевельник', 'можжевельника', 'A prickly evergreen that survives where nothing else will.', 'CONE', 5, 3, 2, 0x3C6A5C,
         (0x5A4234, 0xA68468), (0xC8A478, 0xEED0A2), (0xD0AC80, 0xF2D8AA), (0x264A44, 0x5C9488), ('extrabees:cedar', 'forestry:spruce', 0.08), temperature='cold'),
    tree('cypress', 'cupressus', 'sempervirens', 'Cypress', 'Кипарис', 'кипариса', 'A tall dark candle of a tree, favoured by cemeteries and poets.', 'COLUMN', 12, 6, 2, 0x2C4A38,
         (0x4E3C30, 0x92705A), (0xBE9060, 0xE8BE8C), (0xC89A6A, 0xF0C896), (0x1E3A2A, 0x3F6A4C), ('extrabees:juniper', 'forestry:olive', 0.06), temperature='warm', height=1.25),
    tree('sycamore', 'acer', 'pseudoplatanus', 'Sycamore', 'Явор', 'явора', 'Wide and shady. Its seeds spin like tiny helicopters.', 'BROAD', 6, 4, 4, 0xA0884C,
         (0x56483A, 0xB0A090), (0xCCB88A, 0xF2E4B6), (0xD4C092, 0xF6E8BE), (0x2E5E26, 0x7EAE3A), ('forestry:maple', 'extrabees:ash', 0.07)),
    tree('horse_chestnut', 'aesculus', 'hippocastanum', 'Horse Chestnut', 'Конский каштан', 'конского каштана', 'Candle-like flowers in spring, conkers in autumn.', 'BROAD', 7, 4, 4, 0xB89060,
         (0x46382C, 0x907A62), (0xC8A272, 0xEECC9C), (0xD0AA7A, 0xF2D4A4), (0x2A5C22, 0x70A83A), ('forestry:chestnut', 'extrabees:sycamore', 0.06)),
    tree('eucalyptus', 'eucalyptus', 'globulus', 'Eucalyptus', 'Эвкалипт', 'эвкалипта', 'Sheds its bark in ribbons and smells of medicine.', 'COLUMN', 12, 7, 3, 0x7E9C98,
         (0x6E6E5E, 0xC4CAB8), (0xC8A884, 0xEED2AA), (0xD0B08C, 0xF2DAB4), (0x4A6E5E, 0x9CBFAA), ('forestry:acacia', 'forestry:jacaranda', 0.06), temperature='warm', humidity='arid', height=1.25),
    tree('holly', 'ilex', 'aquifolium', 'Holly', 'Падуб', 'падуба', 'Glossy leaves with a bad attitude. Stays green all winter.', 'CONE', 5, 3, 2, 0x1E5A32,
         (0x4A4036, 0x948672), (0xD4C8A8, 0xF4ECD2), (0xDCD0B0, 0xF8F0D8), (0x16401E, 0x2C7A40), ('extrabees:hawthorn', 'forestry:spruce', 0.07), temperature='cold'),
    tree('yew', 'taxus', 'baccata', 'Yew', 'Тис', 'тиса', 'Ancient, poisonous and patient. Some stand for a thousand years.', 'OVAL', 6, 3, 3, 0x2E4A2E,
         (0x5A3A2A, 0xA06848), (0xC49064, 0xEEC090), (0xCC9A6C, 0xF2CA9A), (0x1A3A22, 0x3C6A44), ('extrabees:juniper', 'extrabees:holly', 0.05), humidity='damp'),
]

def ramp(c, lo, hi):
    def sc(f): return ((min(255, int(((c >> 16) & 255) * f)) << 16) | (min(255, int(((c >> 8) & 255) * f)) << 8) | min(255, int((c & 255) * f)))
    return (sc(lo), sc(hi))

def tree2(id, genus, species, en, ru, ru_gen, desc, shape, base, var, radius, bark, plank, leaf, parents,
          rarity=0.003, temperature=None, humidity=None, height=1.0, fruit=None):
    t = tree(id, genus, species, en, ru, ru_gen, desc, shape, base, var, radius, leaf, ramp(bark, 0.45, 1.25), ramp(plank, 0.75, 1.15),
             ramp(plank, 0.8, 1.2), ramp(leaf, 0.55, 1.2), parents, rarity, temperature, humidity, height)
    t['fruit'] = fruit
    return t

# id, en, ru, colour, ripening ticks, nutrition, saturation
FRUITS = [
    ('hazelnut', 'Hazelnut', 'Лесной орех', 0xA0713C, 6, 3, 0.3), ('haw', 'Haw', 'Плод боярышника', 0xC02828, 6, 2, 0.3),
    ('rowanberry', 'Rowanberry', 'Рябина', 0xE0561E, 6, 2, 0.3), ('conker', 'Conker', 'Конский каштан', 0x7A4A28, 6, 1, 0.2),
    ('sloe', 'Sloe', 'Терн', 0x2C3A78, 6, 2, 0.3), ('medlar', 'Medlar', 'Мушмула', 0xB07A3C, 6, 4, 0.4),
    ('mulberry', 'Mulberry', 'Шелковица', 0x5A2A5A, 6, 3, 0.3), ('apricot', 'Apricot', 'Абрикос', 0xF0A030, 8, 4, 0.5),
    ('peach', 'Peach', 'Персик', 0xF2A27A, 8, 4, 0.5), ('quince', 'Quince', 'Айва', 0xE0C838, 8, 3, 0.4),
    ('fig', 'Fig', 'Инжир', 0x6A3A5A, 8, 4, 0.4), ('pecan', 'Pecan', 'Орех пекан', 0x8A5A32, 8, 4, 0.4),
]
FRUIT_OF = {'hazel': 'hazelnut', 'hawthorn': 'haw', 'rowan': 'rowanberry', 'horse_chestnut': 'conker'}
for _t in TREES:
    _t['fruit'] = FRUIT_OF.get(_t['id'])

TREES += [
    tree2('cork_oak', 'quercus', 'suber', 'Cork Oak', 'Пробковый дуб', 'пробкового дуба', 'Thick, springy bark that can be peeled without killing it.', 'OVAL', 7, 4, 3, 0x5A4636, 0xBC8E5C, 0x4A6E2A, ('forestry:oak', 'forestry:olive', 0.06), temperature='warm'),
    tree2('red_oak', 'quercus', 'rubra', 'Red Oak', 'Красный дуб', 'красного дуба', 'Its leaves turn the colour of embers in autumn.', 'OVAL', 8, 4, 4, 0x4E4036, 0xB8825A, 0x4C7A28, ('forestry:oak', 'forestry:maple', 0.07)),
    tree2('whitebeam', 'sorbus', 'aria', 'Whitebeam', 'Белая рябина', 'белой рябины', 'Leaves silver on the underside, flashing in the wind.', 'OVAL', 6, 3, 3, 0x6A6258, 0xC8A878, 0x6E8A5A, ('extrabees:rowan', 'forestry:birch', 0.07), temperature='cold'),
    tree2('hop_hornbeam', 'ostrya', 'carpinifolia', 'Hop Hornbeam', 'Хмелеграб', 'хмелеграба', 'Its seed clusters look like hops.', 'OVAL', 6, 3, 3, 0x6A5A48, 0xCCB48A, 0x4A7A30, ('extrabees:hornbeam', 'forestry:elm', 0.07)),
    tree2('field_maple', 'acer', 'campestre', 'Field Maple', 'Клён полевой', 'клёна полевого', 'A modest hedgerow maple, golden in autumn.', 'BROAD', 5, 3, 3, 0x6E5E4C, 0xD0B484, 0x5E8A2C, ('forestry:maple', 'extrabees:hornbeam', 0.07)),
    tree2('norway_maple', 'acer', 'platanoides', 'Norway Maple', 'Клён остролистный', 'клёна остролистного', 'Large and dense. Casts a deep shade.', 'BROAD', 7, 4, 4, 0x5E5044, 0xD8BE8A, 0x3E7A2A, ('forestry:maple', 'extrabees:sycamore', 0.06)),
    tree2('box_elder', 'acer', 'negundo', 'Box Elder', 'Клён ясенелистный', 'клёна ясенелистного', 'A maple that pretends to be an ash.', 'OVAL', 6, 3, 3, 0x7A6E5A, 0xE0CC9C, 0x6A9A3A, ('forestry:maple', 'extrabees:ash', 0.07)),
    tree2('black_poplar', 'populus', 'nigra', 'Black Poplar', 'Чёрный тополь', 'чёрного тополя', 'Tall, dark-barked, and always leaning a little.', 'COLUMN', 11, 5, 3, 0x3E382E, 0xB89E70, 0x4E7E2E, ('forestry:poplar', 'extrabees:aspen', 0.07), humidity='damp'),
    tree2('crack_willow', 'salix', 'fragilis', 'Crack Willow', 'Ива ломкая', 'ивы ломкой', 'Branches snap with a sound like a shot.', 'BROAD', 6, 3, 4, 0x5E5240, 0xC4A878, 0x5E8E3A, ('forestry:willow', 'extrabees:alder', 0.07), humidity='damp'),
    tree2('lilac', 'syringa', 'vulgaris', 'Lilac', 'Сирень', 'сирени', 'Heavy with scent every spring.', 'OVAL', 3, 2, 2, 0x5A4A3E, 0xC8AE86, 0x4E8A44, ('extrabees:ash', 'extrabees:hawthorn', 0.07)),
    tree2('white_ash', 'fraxinus', 'americana', 'White Ash', 'Белый ясень', 'белого ясеня', 'The wood of baseball bats and old tool handles.', 'OVAL', 8, 4, 3, 0x4A443C, 0xD4BE90, 0x3E7A32, ('extrabees:ash', 'forestry:oak', 0.07)),
    tree2('hemlock', 'tsuga', 'canadensis', 'Hemlock', 'Тсуга', 'тсуги', 'Soft needles and drooping tips. Loves shade and cold.', 'CONE', 9, 5, 3, 0x4E3C30, 0xC8A07A, 0x1E4A34, ('forestry:spruce', 'forestry:fir', 0.07), temperature='cold'),
    tree2('douglas_fir', 'pseudotsuga', 'menziesii', 'Douglas Fir', 'Дугласова пихта', 'дугласовой пихты', 'Towers over the forest and smells of resin.', 'CONE', 14, 7, 3, 0x4A3A2E, 0xC89A68, 0x26503A, ('forestry:fir', 'forestry:pine', 0.06), height=1.25),
    tree2('bald_cypress', 'taxodium', 'distichum', 'Bald Cypress', 'Болотный кипарис', 'болотного кипариса', 'Stands in water, drops its needles each autumn.', 'CONE', 9, 4, 3, 0x6A4A38, 0xCC9468, 0x4E7A3A, ('extrabees:cypress', 'forestry:willow', 0.06), temperature='warm', humidity='damp'),
    tree2('thuja', 'thuja', 'occidentalis', 'Arborvitae', 'Туя', 'туи', 'A dense green column, the hedge of choice.', 'COLUMN', 7, 3, 2, 0x6E5240, 0xD0A678, 0x2E6A3C, ('extrabees:cypress', 'extrabees:juniper', 0.07)),
    tree2('basswood', 'tilia', 'americana', 'Basswood', 'Американская липа', 'американской липы', 'Soft wood, sweet flowers, busy bees.', 'BROAD', 7, 4, 4, 0x5E5648, 0xE0CCA0, 0x4A8A38, ('forestry:lime', 'forestry:maple', 0.07)),
    tree2('black_locust', 'robinia', 'pseudoacacia', 'Black Locust', 'Робиния', 'робинии', 'Rot-proof wood and flowers bees adore.', 'OVAL', 8, 4, 3, 0x4A3E34, 0xC8B070, 0x5E9A3A, ('forestry:acacia', 'extrabees:ash', 0.07)),
    tree2('laburnum', 'laburnum', 'anagyroides', 'Laburnum', 'Бобовник', 'бобовника', 'Golden chains of flowers. Every part is poisonous.', 'OVAL', 4, 2, 2, 0x5A4A38, 0xBC9460, 0x58903C, ('extrabees:black_locust', 'extrabees:lilac', 0.07)),
    tree2('honey_locust', 'gleditsia', 'triacanthos', 'Honey Locust', 'Гледичия', 'гледичии', 'Thorned trunk, light feathery leaves.', 'OVAL', 9, 4, 3, 0x483C32, 0xC09468, 0x6AA040, ('extrabees:black_locust', 'forestry:acacia', 0.06)),
    tree2('hickory', 'carya', 'ovata', 'Shagbark Hickory', 'Гикори', 'гикори', 'Peeling bark and wood tough enough to outlast any axe.', 'OVAL', 9, 4, 3, 0x5E5248, 0xC8A074, 0x46742C, ('forestry:walnut', 'forestry:chestnut', 0.06)),
    tree2('camphor', 'cinnamomum', 'camphora', 'Camphor Tree', 'Камфорное дерево', 'камфорного дерева', 'Every leaf smells like a medicine cabinet.', 'BROAD', 7, 4, 4, 0x6A5444, 0xD0A878, 0x3E7438, ('forestry:mahogany', 'extrabees:bay_laurel', 0.06), temperature='warm'),
    tree2('bay_laurel', 'laurus', 'nobilis', 'Bay Laurel', 'Лавр', 'лавра', 'Aromatic evergreen once woven into crowns.', 'OVAL', 4, 3, 2, 0x5A4C3E, 0xC8A878, 0x2E6A34, ('forestry:olive', 'extrabees:holly', 0.07), temperature='warm'),
    tree2('zelkova', 'zelkova', 'serrata', 'Zelkova', 'Зельква', 'зельквы', 'A vase-shaped elm lookalike that shrugs off disease.', 'OVAL', 8, 4, 3, 0x6A5A4C, 0xD0B07C, 0x4E8230, ('forestry:elm', 'forestry:beech', 0.07)),
    tree2('hackberry', 'celtis', 'occidentalis', 'Hackberry', 'Каркас', 'каркаса', 'Warty bark and sweet little berries for the birds.', 'BROAD', 7, 4, 4, 0x6E6254, 0xD4B888, 0x58903A, ('forestry:elm', 'extrabees:hornbeam', 0.07)),
    tree2('neem', 'azadirachta', 'indica', 'Neem', 'Ним', 'нима', 'Bitter and useful. Insects keep their distance.', 'BROAD', 7, 4, 4, 0x6E5844, 0xC89E70, 0x3E8030, ('forestry:mahogany', 'forestry:acacia', 0.06), temperature='hot', humidity='arid'),
    # fruit trees
    tree2('blackthorn', 'prunus', 'spinosa', 'Blackthorn', 'Тёрн', 'терна', 'Thorny and tough. Its sloes are best after a frost.', 'OVAL', 3, 2, 2, 0x3A3028, 0xB8906A, 0x3C6A2C, ('forestry:plum', 'extrabees:hawthorn', 0.07), fruit='sloe', rarity=0.002),
    tree2('medlar', 'mespilus', 'germanica', 'Medlar', 'Мушмула', 'мушмулы', 'Its fruit is only edible once it has begun to rot.', 'OVAL', 4, 2, 2, 0x5E5040, 0xC4A070, 0x4E7E34, ('forestry:pear', 'extrabees:hawthorn', 0.07), fruit='medlar', rarity=0.002),
    tree2('mulberry', 'morus', 'alba', 'Mulberry', 'Шелковица', 'шелковицы', 'Sweet dark berries that stain everything they touch.', 'BROAD', 5, 3, 3, 0x6A5A46, 0xD4B07C, 0x4E8C34, ('forestry:plum', 'forestry:elm', 0.07), fruit='mulberry', rarity=0.002),
    tree2('apricot', 'prunus', 'armeniaca', 'Apricot', 'Абрикос', 'абрикоса', 'Early blossom and golden fruit.', 'OVAL', 4, 2, 3, 0x5A4034, 0xCC9468, 0x5A9038, ('forestry:plum', 'forestry:cherry', 0.07), fruit='apricot', temperature='warm', rarity=0.002),
    tree2('peach', 'prunus', 'persica', 'Peach', 'Персик', 'персика', 'Pink blossom, fuzzy fruit.', 'OVAL', 4, 2, 3, 0x5E4438, 0xD09C72, 0x5E9440, ('extrabees:apricot', 'forestry:plum', 0.06), fruit='peach', temperature='warm', rarity=0.002),
    tree2('quince', 'cydonia', 'oblonga', 'Quince', 'Айва', 'айвы', 'Hard, fragrant, golden. Better cooked than raw.', 'OVAL', 3, 2, 2, 0x5A4A3A, 0xC8A878, 0x58903C, ('forestry:pear', 'extrabees:medlar', 0.07), fruit='quince', rarity=0.002),
    tree2('fig', 'ficus', 'carica', 'Fig', 'Инжир', 'инжира', 'Broad leaves, sticky sweet fruit.', 'BROAD', 4, 3, 3, 0x7A6C5C, 0xD4B488, 0x3E7C30, ('forestry:olive', 'extrabees:mulberry', 0.06), fruit='fig', temperature='warm', humidity='arid', rarity=0.002),
    tree2('pecan', 'carya', 'illinoinensis', 'Pecan', 'Пекан', 'пекана', 'Tall nut tree with a buttery crop.', 'OVAL', 9, 4, 3, 0x5A4C3E, 0xC49A70, 0x4A7C30, ('extrabees:hickory', 'forestry:walnut', 0.06), fruit='pecan', temperature='warm', rarity=0.002),
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
        if T.get('fruit'):
            genome['forestry:fruits'] = {'value': f'{NS}:fruit_{T["fruit"]}'}
            genome['forestry:yield'] = {'dominant': True, 'value': 0.2}
        genome['forestry:saplings'] = {'dominant': True, 'value': 0.035}
        genome['forestry:sappiness'] = {'dominant': True, 'value': 0.2}
        sp = {'dominant': True, 'escritoire_color': T['escritoire'], 'genome': genome, 'genus': T['genus'], 'rarity': T['rarity'], 'species': T['species']}
        if T['temperature']: sp['temperature'] = T['temperature']
        if T['humidity']: sp['humidity'] = T['humidity']
        write(f'data/{NS}/tree_species/{tid}.json', sp)
        a, b, chance = T['parents']
        write(f'data/{NS}/recipe/tree_mutation/{tid}.json', {'type': 'forestry:tree_mutation', 'id': f'{NS}:tree_mutation/{tid}',
                                                              'chance': chance, 'first': a, 'second': b, 'result': f'{NS}:{tid}'})

    fj = os.environ.get('FORESTRY_TAXA', '/tmp/claude-0/-home-user-Game-/7284976b-775c-50c7-a7d5-bd10b9750ab0/scratchpad/fj/data/forestry/taxon')
    cup = json.load(open(os.path.join(fj, 'cupressaceae.json')))['parent'] if os.path.isdir(fj) else 'cupressales'
    ros = json.load(open(os.path.join(fj, 'rosaceae.json')))['parent'] if os.path.isdir(fj) else 'rosales'
    for name, parent in EXTRA_TAXA.items():
        parent = {'%CUPRESSALES%': cup, '%ROSALES%': ros}.get(parent, parent)
        write(f'data/{NS}/taxon/{name}.json', {'parent': parent, 'name': name})
    for g, parent in GENERA.items():
        write(f'data/{NS}/taxon/{g}.json', {'parent': parent, 'name': g, 'rank': 'genus'})

    item_tags = {k: v for k, v in block_tags.items() if not k.startswith('mineable/')}
    for name, ids in block_tags.items():
        ns_tag = 'minecraft' if not name.endswith('_logs') else NS
        write(f'data/{ns_tag}/tags/block/{name}.json', {'replace': False, 'values': sorted(set(ids))})
    for name, ids in item_tags.items():
        ns_tag = 'minecraft' if not name.endswith('_logs') else NS
        write(f'data/{ns_tag}/tags/item/{name}.json', {'replace': False, 'values': sorted(set(ids))})

    en_extra, ru_extra = {}, {}

    # ---- fruits: items, textures, leaf overlay sprites, lang, java ----
    for fid, fen, fru, colour, ripening, nutrition, saturation in FRUITS:
        c = rgb(colour)
        item = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
        ip = item.load()
        for x in range(16):
            for y in range(16):
                d = ((x - 7.5) ** 2 + (y - 9) ** 2) ** 0.5
                if d <= 5.2:
                    f = 0.55 if d > 4.2 else (1.25 if (x - 7.5) + (y - 9) < -2 and d < 3.4 else 1.0)
                    ip[x, y] = (min(255, int(c[0] * f)), min(255, int(c[1] * f)), min(255, int(c[2] * f)), 255)
        for (x, y) in ((8, 3), (8, 4), (9, 2), (10, 2), (7, 3)):
            ip[x, y] = (70, 110, 40, 255) if (x, y) in ((9, 2), (10, 2), (7, 3)) else (90, 60, 30, 255)
        os.makedirs(os.path.join(RES, f'assets/{NS}/textures/item'), exist_ok=True)
        item.save(os.path.join(RES, f'assets/{NS}/textures/item/{fid}.png'))
        write(f'assets/{NS}/models/item/{fid}.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'{NS}:item/{fid}'}})
        overlay = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
        op = overlay.load()
        for (x, y) in ((3, 3), (11, 4), (6, 8), (12, 11), (4, 12), (9, 13)):
            for dx in (0, 1):
                for dy in (0, 1):
                    op[x + dx, y + dy] = (235, 235, 235, 255) if (dx, dy) != (1, 1) else (190, 190, 190, 255)
        os.makedirs(os.path.join(RES, f'assets/{NS}/textures/block/fruit'), exist_ok=True)
        overlay.save(os.path.join(RES, f'assets/{NS}/textures/block/fruit/{fid}.png'))
        nut = fid in ('hazelnut', 'pecan', 'conker')
        write(f'data/{NS}/recipe/squeezer/fruit/{fid}.json', {
            'type': 'forestry:squeezer', 'id': f'{NS}:squeezer/fruit/{fid}', 'chance': 0.05,
            'output': {'stack': {'amount': 80 if nut else 50, 'id': 'forestry:seed_oil' if nut else 'forestry:fruit_juice'}},
            'remnant': {'count': 1, 'id': 'forestry:mulch'}, 'resources': [{'item': f'{NS}:{fid}'}], 'time': 20})
        en_extra[f'item.{NS}.{fid}'] = fen
        ru_extra[f'item.{NS}.{fid}'] = fru
    jf = 'package extrabees.trees;\n\n// generated by tools/gen_trees.py, do not edit\nfinal class GeneratedFruits {\n\tstatic final FruitDef[] DEFS = {\n'
    for fid, fen, fru, colour, ripening, nutrition, saturation in FRUITS:
        jf += f'\t\tnew FruitDef("{fid}", 0x{colour:06X}, {ripening}, {nutrition}, {saturation}f),\n'
    jf += '\t};\n}\n'
    open(os.path.join(JAVA, 'GeneratedFruits.java'), 'w').write(jf)
    en.update(en_extra); ru.update(ru_extra)
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
