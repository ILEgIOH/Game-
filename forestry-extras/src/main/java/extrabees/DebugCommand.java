package extrabees;

import java.util.Optional;

import com.mojang.brigadier.arguments.StringArgumentType;

import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.tags.BlockTags;
import net.minecraft.world.level.block.LeavesBlock;
import net.minecraft.world.level.levelgen.Heightmap;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.RegisterCommandsEvent;
import net.neoforged.neoforge.event.server.ServerStartedEvent;

import extrabees.trees.ModTrees;
import forestry.api.IForestryApi;
import forestry.api.arboriculture.ITreeSpecies;
import forestry.api.core.genetics.ForestrySpeciesTypes;

// op-only helper: /extrabees tree <name> grows one of our trees at the command position
@EventBusSubscriber(modid = ExtraBees.MOD_ID)
public final class DebugCommand {
	@SubscribeEvent
	public static void register(RegisterCommandsEvent event) {
		event.getDispatcher().register(Commands.literal(ExtraBees.MOD_ID)
			.requires(source -> source.hasPermission(2))
			.then(Commands.literal("tree")
				.then(Commands.argument("name", StringArgumentType.word())
					.executes(ctx -> growTree(ctx.getSource(), StringArgumentType.getString(ctx, "name"))))));
	}

	private static int growTree(CommandSourceStack source, String name) {
		ResourceLocation id = ResourceLocation.fromNamespaceAndPath(ExtraBees.MOD_ID, name);
		String message = grow(source.getLevel(), BlockPos.containing(source.getPosition()), id);
		source.sendSuccess(() -> Component.literal(message), true);
		return message.contains("placed=true") ? 1 : 0;
	}

	private static String grow(ServerLevel level, BlockPos pos, ResourceLocation id) {
		try {
			var type = IForestryApi.INSTANCE.getGeneticManager().getSpeciesType(ForestrySpeciesTypes.TREE);
			if (!(type.getSpecies(id) instanceof ITreeSpecies species)) {
				return "Unknown tree: " + id;
			}
			Feature<NoneFeatureConfiguration> feature = species.getGenerator().getTreeFeature(species);
			boolean placed = feature.place(new FeaturePlaceContext<>(Optional.empty(), level, level.getChunkSource().getGenerator(),
				level.getRandom(), pos, NoneFeatureConfiguration.INSTANCE));
			int logs = 0;
			int leaves = 0;
			int decaying = 0;
			int top = pos.getY();
			for (BlockPos p : BlockPos.betweenClosed(pos.offset(-10, 0, -10), pos.offset(10, 40, 10))) {
				var state = level.getBlockState(p);
				if (state.is(BlockTags.LOGS)) {
					logs++;
					top = Math.max(top, p.getY());
				} else if (state.is(BlockTags.LEAVES)) {
					leaves++;
					if (state.hasProperty(LeavesBlock.DISTANCE) && state.getValue(LeavesBlock.DISTANCE) == 7) {
						decaying++;
					}
				}
			}
			String message = "Tree " + id + ": placed=" + placed + " logs=" + logs + " leaves=" + leaves + " leavesWithoutSupport=" + decaying
				+ " trunkHeight=" + (top - pos.getY() + 1);
			ExtraBees.LOGGER.info(message);
			return message;
		} catch (Throwable t) {
			ExtraBees.LOGGER.error("Could not grow tree {}", id, t);
			return "Failed: " + t;
		}
	}

	// -Dextrabees.selftest=true grows every tree once after startup and stops the server (used for headless testing)
	@SubscribeEvent
	public static void onServerStarted(ServerStartedEvent event) {
		if (!Boolean.getBoolean("extrabees.selftest")) {
			return;
		}
		ServerLevel level = event.getServer().overworld();
		int x = 0;
		java.util.List<String> names = new java.util.ArrayList<>(ModTrees.ids());
		names.add("nosuchtree");
		for (String name : names) {
			BlockPos column = new BlockPos(x, 0, 0);
			level.getChunk(column);
			BlockPos ground = level.getHeightmapPos(Heightmap.Types.MOTION_BLOCKING_NO_LEAVES, column);
			ExtraBees.LOGGER.info("SELFTEST {}", grow(level, ground, ResourceLocation.fromNamespaceAndPath(ExtraBees.MOD_ID, name)));
			x += 40;
		}
		ExtraBees.LOGGER.info("SELFTEST done");
		event.getServer().halt(false);
	}

	private DebugCommand() {
	}
}
