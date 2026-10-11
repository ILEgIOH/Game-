package extrabees.trees;

import java.util.function.Consumer;

import net.minecraft.resources.ResourceLocation;

import forestry.api.client.arboriculture.ILeafSprite;
import forestry.api.client.plugin.IClientRegistration;

import extrabees.ExtraBees;

final class ExtraTreesClient implements Consumer<IClientRegistration> {
	@Override
	public void accept(IClientRegistration client) {
		for (TreeWood wood : ModTrees.WOODS) {
			TreeDef def = wood.def;
			ResourceLocation leaf = ResourceLocation.fromNamespaceAndPath(ExtraBees.MOD_ID, "block/" + def.id() + "_leaves");
			client.setLeafSprite(def.speciesId(), new ILeafSprite() {
				@Override
				public ResourceLocation get(boolean pollinated, boolean fancy) {
					return leaf;
				}

				@Override
				public ResourceLocation getParticle() {
					return leaf;
				}
			});
			// the colour is baked into the texture
			client.setLeafTint(def.speciesId(), (level, pos) -> 0xFFFFFF);
			client.setSaplingModel(def.speciesId(),
				ResourceLocation.fromNamespaceAndPath(ExtraBees.MOD_ID, "block/sapling/" + def.id()),
				ResourceLocation.fromNamespaceAndPath(ExtraBees.MOD_ID, "item/sapling/" + def.id()));
		}
	}
}
