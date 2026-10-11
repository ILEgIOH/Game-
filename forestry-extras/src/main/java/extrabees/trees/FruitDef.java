package extrabees.trees;

import net.minecraft.resources.ResourceLocation;

import extrabees.ExtraBees;

record FruitDef(String id, int colour, int ripening, int nutrition, float saturation) {
	ResourceLocation fruitId() {
		return ResourceLocation.fromNamespaceAndPath(ExtraBees.MOD_ID, "fruit_" + id);
	}

	ResourceLocation sprite() {
		return ResourceLocation.fromNamespaceAndPath(ExtraBees.MOD_ID, "block/fruit/" + id);
	}
}
