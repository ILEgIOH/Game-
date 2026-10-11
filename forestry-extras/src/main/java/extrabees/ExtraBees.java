package extrabees;

import com.mojang.logging.LogUtils;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;

@Mod(ExtraBees.MOD_ID)
public class ExtraBees {
	public static final String MOD_ID = "extrabees";
	public static final org.slf4j.Logger LOGGER = LogUtils.getLogger();

	public ExtraBees(IEventBus modBus) {
		ModItems.ITEMS.register(modBus);
		ModItems.TABS.register(modBus);
	}
}
