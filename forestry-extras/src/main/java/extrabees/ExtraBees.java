package extrabees;

import com.mojang.logging.LogUtils;
import net.neoforged.bus.api.IEventBus;
import java.util.List;

import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.common.NeoForge;
import net.neoforged.neoforge.event.server.ServerStartedEvent;

@Mod(ExtraBees.MOD_ID)
public class ExtraBees {
	public static final String MOD_ID = "extrabees";
	public static final org.slf4j.Logger LOGGER = LogUtils.getLogger();

	public ExtraBees(IEventBus modBus) {
		ModItems.ITEMS.register(modBus);
		ModItems.TABS.register(modBus);
		NeoForge.EVENT_BUS.addListener((ServerStartedEvent event) -> {
			List<String> ids = ForestryBridge.listOwnSpecies();
			LOGGER.info("Extra Bees: {} bee species loaded in Forestry: {}", ids.size(), ids);
		});
	}
}
