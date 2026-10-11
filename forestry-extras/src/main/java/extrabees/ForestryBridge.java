package extrabees;

import java.lang.reflect.Method;
import java.util.Collection;
import java.util.List;

import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.ItemStack;

// reflection on purpose: a changed Forestry API only empties the tab, it must never crash the game
final class ForestryBridge {
	static void addBees(CreativeModeTab.Output output) {
		try {
			Class<?> apiClass = Class.forName("forestry.api.IForestryApi");
			Object api = apiClass.getField("INSTANCE").get(null);
			Object genetics = apiClass.getMethod("getGeneticManager").invoke(api);
			Class<?> geneticsClass = Class.forName("forestry.api.core.genetics.IGeneticManager");
			Object beeType = geneticsClass.getMethod("getSpeciesType", ResourceLocation.class)
				.invoke(genetics, ResourceLocation.fromNamespaceAndPath("forestry", "bee_species"));

			Class<?> typeClass = Class.forName("forestry.api.core.genetics.ISpeciesType");
			Class<?> speciesClass = Class.forName("forestry.api.core.genetics.ISpecies");
			Class<?> stageClass = Class.forName("forestry.api.core.genetics.ILifeStage");
			Collection<?> stages = (Collection<?>) typeClass.getMethod("getLifeStages").invoke(beeType);
			List<?> species = (List<?>) typeClass.getMethod("getAllSpecies").invoke(beeType);
			Method id = speciesClass.getMethod("id");
			Method createStack = speciesClass.getMethod("createStack", stageClass);

			for (Object bee : species) {
				if (ExtraBees.MOD_ID.equals(((ResourceLocation) id.invoke(bee)).getNamespace())) {
					for (Object stage : stages) {
						output.accept((ItemStack) createStack.invoke(bee, stage));
					}
				}
			}
		} catch (Throwable t) {
			ExtraBees.LOGGER.warn("Could not list Extra Bees species in the creative tab", t);
		}
	}

	private ForestryBridge() {
	}
}
