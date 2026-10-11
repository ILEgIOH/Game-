package extrabees.trees;

import java.util.ArrayDeque;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import javax.annotation.Nullable;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.tags.BlockTags;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.LeavesBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;

import forestry.api.arboriculture.ITreeGenData;
import forestry.api.core.genetics.IGenome;

// a plain Feature on purpose: Forestry only special-cases its own base class, and this runs on the public API alone
final class ExtraTreeFeature extends Feature<NoneFeatureConfiguration> {
	private final ITreeGenData tree;
	private final TreeDef def;

	ExtraTreeFeature(ITreeGenData tree, TreeWood wood) {
		super(NoneFeatureConfiguration.CODEC);
		this.tree = tree;
		this.def = wood.def;
	}

	@Override
	public boolean place(FeaturePlaceContext<NoneFeatureConfiguration> context) {
		WorldGenLevel level = context.level();
		RandomSource rand = context.random();
		IGenome genome = this.tree.getDefaultGenome();
		int girth = Math.max(1, this.tree.getGirth(genome));
		int height = Math.max(4, Math.round((this.def.baseHeight() + rand.nextInt(this.def.heightVar())) * this.tree.getHeightModifier(genome)));

		BlockPos base = findBase(level, context.origin(), genome, girth, height);
		if (base == null) {
			return false;
		}

		for (int y = 0; y < height; y++) {
			for (int x = 0; x < girth; x++) {
				for (int z = 0; z < girth; z++) {
					this.tree.setLogBlock(genome, level, base.offset(x, y, z), Direction.UP);
				}
			}
		}

		Set<BlockPos> leaves = new HashSet<>();
		double cx = base.getX() + (girth - 1) / 2.0;
		double cz = base.getZ() + (girth - 1) / 2.0;
		int radius = this.def.radius() + (girth - 1);
		for (int y = 1; y <= height + 2; y++) {
			double r = layerRadius(y, height, radius);
			if (r <= 0) {
				continue;
			}
			int ir = (int) Math.ceil(r);
			for (int dx = -ir; dx <= ir; dx++) {
				for (int dz = -ir; dz <= ir; dz++) {
					double px = base.getX() + dx + (girth - 1) / 2.0;
					double pz = base.getZ() + dz + (girth - 1) / 2.0;
					double dist = Math.sqrt((px - cx) * (px - cx) + (pz - cz) * (pz - cz));
					// ragged edge
					if (dist > r + (rand.nextFloat() < 0.15f ? 0.4 : -0.1)) {
						continue;
					}
					BlockPos pos = new BlockPos(base.getX() + dx + (girth - 1) / 2, base.getY() + y, base.getZ() + dz + (girth - 1) / 2);
					BlockState existing = level.getBlockState(pos);
					if (existing.isAir() || existing.canBeReplaced() && !existing.is(BlockTags.LOGS)) {
						if (this.tree.setLeaves(genome, level, pos, rand, false)) {
							leaves.add(pos);
						}
					}
				}
			}
		}
		fixDistances(level, leaves);
		return true;
	}

	// radius of the leaf canopy at height y above the trunk base (0 = no leaves at this layer)
	private double layerRadius(int y, int height, int radius) {
		int top = height + 2;
		switch (this.def.shape()) {
			case CONE -> {
				int bottom = Math.max(2, height / 3);
				if (y < bottom) {
					return 0;
				}
				double t = (double) (top - y) / (top - bottom);
				return Math.max(0.4, radius * t);
			}
			case COLUMN -> {
				int bottom = Math.max(2, height / 3);
				if (y < bottom) {
					return 0;
				}
				double mid = (bottom + top) / 2.0;
				double half = (top - bottom) / 2.0;
				double t = 1 - Math.pow((y - mid) / half, 2);
				return Math.max(0.4, radius * Math.sqrt(Math.max(t, 0)));
			}
			case BROAD -> {
				int vr = Math.max(2, radius / 2 + 1);
				int centre = height - vr + 2;
				double dy = (double) (y - centre) / vr;
				if (Math.abs(dy) > 1) {
					return 0;
				}
				return Math.max(0.4, radius * Math.sqrt(1 - dy * dy));
			}
			default -> {
				int vr = radius + 1;
				int centre = height - radius + 1;
				double dy = (double) (y - centre) / vr;
				if (Math.abs(dy) > 1) {
					return 0;
				}
				return Math.max(0.4, radius * Math.sqrt(1 - dy * dy));
			}
		}
	}

	@Nullable
	private BlockPos findBase(WorldGenLevel level, BlockPos origin, IGenome genome, int girth, int height) {
		BlockState state = level.getBlockState(origin);
		boolean sapling = !state.isAir() && !state.canBeReplaced() && level.getBlockEntity(origin) != null;
		if (sapling) {
			return this.tree.getGrowthPos(genome, level, origin, girth, height);
		}
		// no sapling (world generation, commands): check ground and room ourselves
		for (int x = 0; x < girth; x++) {
			for (int z = 0; z < girth; z++) {
				if (!level.getBlockState(origin.offset(x, -1, z)).is(BlockTags.DIRT)) {
					return null;
				}
				for (int y = 0; y <= height + 2; y++) {
					BlockState s = level.getBlockState(origin.offset(x, y, z));
					if (!s.canBeReplaced() && !s.is(BlockTags.LEAVES) && !s.isAir()) {
						return null;
					}
				}
			}
		}
		return origin;
	}

	// same idea as vanilla TreeFeature: leaf distance is how many leaf steps away the nearest log is
	private static void fixDistances(LevelAccessor level, Set<BlockPos> leaves) {
		Map<BlockPos, Integer> dist = new HashMap<>();
		ArrayDeque<BlockPos> queue = new ArrayDeque<>();
		for (BlockPos pos : leaves) {
			for (Direction dir : Direction.values()) {
				if (level.getBlockState(pos.relative(dir)).is(BlockTags.LOGS)) {
					dist.put(pos, 1);
					queue.add(pos);
					break;
				}
			}
		}
		while (!queue.isEmpty()) {
			BlockPos pos = queue.poll();
			int next = dist.get(pos) + 1;
			if (next > 7) {
				continue;
			}
			for (Direction dir : Direction.values()) {
				BlockPos n = pos.relative(dir);
				if (leaves.contains(n) && !dist.containsKey(n)) {
					dist.put(n, next);
					queue.add(n);
				}
			}
		}
		for (BlockPos pos : leaves) {
			BlockState state = level.getBlockState(pos);
			if (state.hasProperty(LeavesBlock.DISTANCE)) {
				level.setBlock(pos, state.setValue(LeavesBlock.DISTANCE, dist.getOrDefault(pos, 7)), 19);
			}
		}
	}
}
