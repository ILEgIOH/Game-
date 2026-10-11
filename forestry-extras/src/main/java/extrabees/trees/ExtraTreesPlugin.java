package extrabees.trees;

import java.util.function.Consumer;

import net.minecraft.network.chat.TextColor;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.ItemStack;

import forestry.api.client.plugin.IClientRegistration;
import forestry.api.plugin.IArboricultureRegistration;
import forestry.api.plugin.IForestryPlugin;

import extrabees.ExtraBees;

// discovered by Forestry through META-INF/services/forestry.api.plugin.IForestryPlugin
public final class ExtraTreesPlugin implements IForestryPlugin {
	@Override
	public ResourceLocation id() {
		return ResourceLocation.fromNamespaceAndPath(ExtraBees.MOD_ID, "trees");
	}

	@Override
	public void registerArboriculture(IArboricultureRegistration arboriculture) {
		for (FruitDef fruit : GeneratedFruits.DEFS) {
			arboriculture.registerFruit(fruit.fruitId(), new ExtraFruit(fruit, ModTrees.FRUIT_ITEMS.get(fruit.id()).get()));
		}
		for (TreeWood wood : ModTrees.WOODS) {
			TreeDef def = wood.def;
			arboriculture.registerSpecies(def.speciesId(), def.genus(), def.species(), true, TextColor.fromRgb(def.escritoire()), new ExtraWoodType(wood))
				.setGenerator(new ExtraTreeGenerator(wood))
				.setDecorativeLeaves(new ItemStack(wood.leaves.get()))
				.addVanillaStates(wood.leaves.get().getStateDefinition().getPossibleStates());
		}
	}

	@Override
	public void registerClient(Consumer<Consumer<IClientRegistration>> registrar) {
		registrar.accept(new ExtraTreesClient());
	}
}
