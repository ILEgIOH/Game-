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

## Bees
Cuprous, Ferrous, Auric, Carbonic, Redstone, Lapis, Adamantine (diamond), Verdant Gem (emerald),
Amethyst, Quartz, Glowing, Blazing, Ancient (netherite), Gelatinous, Prismatic Reef.
Breeding tree is in the `parents` field of each entry in `tools/gen_data.py`.

### Mod-specific bees (batch 2)
Loaded only when the other mod is present (built-in datapacks in `compat/`, see `CompatPacks.java`):
- **Create:** Zincic, Brassy, Andesite
- **The Aether:** Ambrosial, Zanitic
- **Mystical Agriculture:** Inferium, Prosperous
- **DivineRPG:** Arlemite, Realmite, Rupee, Bloodgem, Torrid

Item ids are checked against the real mod jars. Not done yet: Twilight Forest, AE2, Thermal, Draconic Evolution.
Bees themselves are listed in the Extra Bees creative tab (via reflection, see `ForestryBridge.java`) and in Forestry's own Apiculture tab.

## Testing without the game
`gradle runServer` starts a headless NeoForge server. Put Forestry CE alpha8, Patchouli (and any compat mods) into
`run/server/mods/` first. The server logs `Extra Bees: N bee species loaded in Forestry` once everything is parsed.
This catches datapack/recipe/registry errors; it cannot check visuals.

## Extra Trees (stage 1)
Written only against Forestry's public API (`forestry-api/`, MIT licensed, copied from the alpha8 tag), so it does not touch Forestry internals.
- Trees: **Ash**, **Cedar**, **Aspen** - each with log, stripped log, wood, stripped wood, planks, stairs, slab, fence, fence gate, door, trapdoor, button, pressure plate, leaves.
- Generator: `python3 tools/gen_data.py && python3 tools/gen_trees.py` (run in this order, the second merges lang files).
  Textures are luminance recolours of the vanilla oak textures; for private/hobby use.
- Code: `src/main/java/extrabees/trees/` (`ExtraTreesPlugin` is found by Forestry through `META-INF/services`).
- `/extrabees tree <ash|cedar|aspen>` (op) grows a tree at the command position.
- Not done yet: signs, boats, fruits, fireproof wood, own leaf block entity (pollination/leaf genetics use Forestry's generic leaves).
- To add a tree: add an entry to `TREES` in `tools/gen_trees.py`, regenerate, rebuild. The genus must exist in Forestry's taxonomy or be added to `GENERA`.

Headless self-test: `gradle runServer -Pselftest=true` grows every tree after startup, logs `SELFTEST ...` lines and stops.
