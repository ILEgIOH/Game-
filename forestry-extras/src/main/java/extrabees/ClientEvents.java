package extrabees;

import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.RegisterColorHandlersEvent;

@EventBusSubscriber(modid = ExtraBees.MOD_ID, value = Dist.CLIENT)
public final class ClientEvents {
	@SubscribeEvent
	public static void onItemColors(RegisterColorHandlersEvent.Item event) {
		for (int i = 0; i < ModItems.COMBS.size(); i++) {
			int tint = 0xFF000000 | GeneratedCombs.TINTS[i];
			event.register((stack, layer) -> tint, ModItems.COMBS.get(i).get());
		}
	}

	private ClientEvents() {
	}
}
