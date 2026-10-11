package extrabees;

import java.nio.file.Path;
import java.util.Optional;

import net.minecraft.network.chat.Component;
import net.minecraft.server.packs.PackLocationInfo;
import net.minecraft.server.packs.PackSelectionConfig;
import net.minecraft.server.packs.PackType;
import net.minecraft.server.packs.PathPackResources;
import net.minecraft.server.packs.repository.Pack;
import net.minecraft.server.packs.repository.PackSource;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.ModList;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.AddPackFindersEvent;

// bee data that references another mod's items only loads when that mod is present
@EventBusSubscriber(modid = ExtraBees.MOD_ID)
public final class CompatPacks {
	@SubscribeEvent
	public static void addPacks(AddPackFindersEvent event) {
		if (event.getPackType() != PackType.SERVER_DATA) {
			return;
		}
		Path root = ModList.get().getModFileById(ExtraBees.MOD_ID).getFile().findResource("compat");
		for (String[] entry : GeneratedCombs.PACKS) {
			String modId = entry[0];
			if (!ModList.get().isLoaded(modId)) {
				continue;
			}
			PackLocationInfo info = new PackLocationInfo(ExtraBees.MOD_ID + "_" + modId, Component.literal("Extra Bees: " + entry[1]),
				PackSource.BUILT_IN, Optional.empty());
			Pack pack = Pack.readMetaAndCreate(info, new PathPackResources.PathResourcesSupplier(root.resolve(modId)),
				PackType.SERVER_DATA, new PackSelectionConfig(true, Pack.Position.TOP, false));
			if (pack != null) {
				event.addRepositorySource(consumer -> consumer.accept(pack));
			}
		}
	}

	private CompatPacks() {
	}
}
