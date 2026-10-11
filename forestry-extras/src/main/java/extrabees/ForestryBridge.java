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

	static List<String> listOwnSpecies() {
		List<String> ids = new java.util.ArrayList<>();
		try {
			Class<?> apiClass = Class.forName("forestry.api.IForestryApi");
			Object api = apiClass.getField("INSTANCE").get(null);
			Object genetics = apiClass.getMethod("getGeneticManager").invoke(api);
			Object beeType = Class.forName("forestry.api.core.genetics.IGeneticManager").getMethod("getSpeciesType", ResourceLocation.class)
				.invoke(genetics, ResourceLocation.fromNamespaceAndPath("forestry", "bee_species"));
			List<?> species = (List<?>) Class.forName("forestry.api.core.genetics.ISpeciesType").getMethod("getAllSpecies").invoke(beeType);
			Method id = Class.forName("forestry.api.core.genetics.ISpecies").getMethod("id");
			for (Object bee : species) {
				ResourceLocation key = (ResourceLocation) id.invoke(bee);
				if (ExtraBees.MOD_ID.equals(key.getNamespace())) {
					ids.add(key.getPath());
				}
			}
		} catch (Throwable t) {
			ExtraBees.LOGGER.warn("Could not query Forestry species", t);
		}
		return ids;
	}

	private ForestryBridge() {
	}
}
