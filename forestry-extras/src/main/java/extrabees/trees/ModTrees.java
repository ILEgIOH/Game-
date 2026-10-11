package extrabees.trees;

import java.util.ArrayList;
import java.util.List;

import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.FireBlock;
import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;
import net.neoforged.neoforge.registries.DeferredRegister;

import extrabees.ExtraBees;

public final class ModTrees {
	public static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(ExtraBees.MOD_ID);
	public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(ExtraBees.MOD_ID);

	static final List<TreeWood> WOODS = new ArrayList<>();

	static {
		for (TreeDef def : GeneratedTrees.DEFS) {
			WOODS.add(new TreeWood(def));
		}
	}

	public static void register(IEventBus modBus) {
		BLOCKS.register(modBus);
		ITEMS.register(modBus);
		modBus.addListener(ModTrees::onCommonSetup);
	}

	private static void onCommonSetup(FMLCommonSetupEvent event) {
		event.enqueueWork(() -> {
			FireBlock fire = (FireBlock) Blocks.FIRE;
			for (TreeWood w : WOODS) {
				for (var log : List.of(w.log, w.strippedLog, w.wood, w.strippedWood)) {
					fire.setFlammable(log.get(), 5, 5);
				}
				for (var plank : List.of(w.planks, w.stairs, w.slab, w.fence, w.fenceGate)) {
					fire.setFlammable(plank.get(), 5, 20);
				}
				fire.setFlammable(w.leaves.get(), 30, 60);
			}
		});
	}

	public static List<net.minecraft.world.item.Item> allItems() {
		return ITEMS.getEntries().stream().<net.minecraft.world.item.Item>map(h -> h.get()).toList();
	}

	private ModTrees() {
	}
}
