package extrabees;

import java.util.ArrayList;
import java.util.List;

import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;

public final class ModItems {
	public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(ExtraBees.MOD_ID);
	public static final DeferredRegister<CreativeModeTab> TABS = DeferredRegister.create(Registries.CREATIVE_MODE_TAB, ExtraBees.MOD_ID);

	public static final List<DeferredHolder<Item, Item>> COMBS = new ArrayList<>();

	static {
		for (String id : GeneratedCombs.IDS) {
			COMBS.add(ITEMS.registerSimpleItem(id));
		}
	}

	public static final DeferredHolder<CreativeModeTab, CreativeModeTab> MAIN_TAB = TABS.register("main", () -> CreativeModeTab.builder()
		.title(Component.translatable("itemGroup." + ExtraBees.MOD_ID + ".main"))
		.icon(() -> new ItemStack(COMBS.get(0).get()))
		.displayItems((params, output) -> COMBS.forEach(comb -> output.accept(comb.get())))
		.build());

	private ModItems() {
	}
}
