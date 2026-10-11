# Extra Bees (Forestry: CE addon, NeoForge 1.21.1)

Reimagining of Binnie's Extra Bees for modern Minecraft. Bees are plain datapack JSON
(`data/extrabees/bee_species`), crossbreeding is `forestry:bee_mutation` recipes.

## Install (fresh NeoForge 1.21.1)
Put these in `mods/`:
1. NeoForge 1.21.1 (latest 21.1.x)
2. **Forestry: Community Edition** 1.21.1 (3.0.0-alpha6 or newer) - Modrinth `forestry-community-edition`
3. **Patchouli** 1.21.1 (Forestry requires it)
4. `extrabees-1.21.1-<version>.jar` from `dist/`

## Build
`gradle build` -> `build/libs/`.  All JSON is generated: edit `tools/gen_data.py`, then `python3 tools/gen_data.py`.

## Bees (batch 1)
Cuprous, Ferrous, Auric, Carbonic, Redstone, Lapis, Adamantine (diamond), Verdant Gem (emerald),
Amethyst, Quartz, Glowing, Blazing, Ancient (netherite), Gelatinous, Prismatic Reef.
Breeding tree is in the `parents` field of each entry in `tools/gen_data.py`.
