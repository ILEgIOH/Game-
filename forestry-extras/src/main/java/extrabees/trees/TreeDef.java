package extrabees.trees;

import net.minecraft.resources.ResourceLocation;

import extrabees.ExtraBees;

record TreeDef(String id, String genus, String species, Shape shape, int baseHeight, int heightVar, int radius, int escritoire, int leafColor) {
	enum Shape {
		OVAL, CONE, COLUMN, BROAD
	}

	ResourceLocation speciesId() {
		return ResourceLocation.fromNamespaceAndPath(ExtraBees.MOD_ID, id);
	}
}
