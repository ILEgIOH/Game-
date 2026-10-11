package extrabees.trees;

import java.util.function.BiFunction;
import java.util.function.Function;

import net.minecraft.world.item.DoubleHighBlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.ButtonBlock;
import net.minecraft.world.level.block.DoorBlock;
import net.minecraft.world.level.block.FenceBlock;
import net.minecraft.world.level.block.FenceGateBlock;
import net.minecraft.world.level.block.LeavesBlock;
import net.minecraft.world.level.block.PressurePlateBlock;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.TrapDoorBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.properties.BlockSetType;
import net.minecraft.world.level.block.state.properties.WoodType;
import net.neoforged.neoforge.registries.DeferredBlock;

// vanilla oak sound/behavior types are reused on purpose: custom WoodTypes also need sign textures
final class TreeWood {
	final TreeDef def;
	final DeferredBlock<Block> log;
	final DeferredBlock<Block> strippedLog;
	final DeferredBlock<Block> wood;
	final DeferredBlock<Block> strippedWood;
	final DeferredBlock<Block> planks;
	final DeferredBlock<Block> stairs;
	final DeferredBlock<Block> slab;
	final DeferredBlock<Block> fence;
	final DeferredBlock<Block> fenceGate;
	final DeferredBlock<Block> door;
	final DeferredBlock<Block> trapdoor;
	final DeferredBlock<Block> button;
	final DeferredBlock<Block> pressurePlate;
	final DeferredBlock<Block> leaves;

	TreeWood(TreeDef def) {
		this.def = def;
		String id = def.id();
		this.strippedLog = block("stripped_" + id + "_log", p -> new ExtraLogBlock(p, null), Blocks.STRIPPED_OAK_LOG);
		this.strippedWood = block("stripped_" + id + "_wood", p -> new ExtraLogBlock(p, null), Blocks.STRIPPED_OAK_WOOD);
		this.log = block(id + "_log", p -> new ExtraLogBlock(p, () -> this.strippedLog.get()), Blocks.OAK_LOG);
		this.wood = block(id + "_wood", p -> new ExtraLogBlock(p, () -> this.strippedWood.get()), Blocks.OAK_WOOD);
		this.planks = block(id + "_planks", Block::new, Blocks.OAK_PLANKS);
		this.stairs = block(id + "_stairs", p -> new StairBlock(this.planks.get().defaultBlockState(), p), Blocks.OAK_STAIRS);
		this.slab = block(id + "_slab", SlabBlock::new, Blocks.OAK_SLAB);
		this.fence = block(id + "_fence", FenceBlock::new, Blocks.OAK_FENCE);
		this.fenceGate = block(id + "_fence_gate", p -> new FenceGateBlock(WoodType.OAK, p), Blocks.OAK_FENCE_GATE);
		this.door = block(id + "_door", p -> new DoorBlock(BlockSetType.OAK, p), Blocks.OAK_DOOR,
			DoubleHighBlockItem::new);
		this.trapdoor = block(id + "_trapdoor", p -> new TrapDoorBlock(BlockSetType.OAK, p), Blocks.OAK_TRAPDOOR);
		this.button = block(id + "_button", p -> new ButtonBlock(BlockSetType.OAK, 30, p), Blocks.OAK_BUTTON);
		this.pressurePlate = block(id + "_pressure_plate", p -> new PressurePlateBlock(BlockSetType.OAK, p), Blocks.OAK_PRESSURE_PLATE);
		this.leaves = block(id + "_leaves", LeavesBlock::new, Blocks.OAK_LEAVES);
	}

	private static DeferredBlock<Block> block(String name, Function<BlockBehaviour.Properties, Block> factory, Block copyFrom) {
		DeferredBlock<Block> block = ModTrees.BLOCKS.registerBlock(name, factory, BlockBehaviour.Properties.ofFullCopy(copyFrom));
		ModTrees.ITEMS.registerSimpleBlockItem(block);
		return block;
	}

	private static DeferredBlock<Block> block(String name, Function<BlockBehaviour.Properties, Block> factory, Block copyFrom,
											BiFunction<Block, Item.Properties, Item> itemFactory) {
		DeferredBlock<Block> block = ModTrees.BLOCKS.registerBlock(name, factory, BlockBehaviour.Properties.ofFullCopy(copyFrom));
		ModTrees.ITEMS.registerItem(name, props -> itemFactory.apply(block.get(), props));
		return block;
	}
}
