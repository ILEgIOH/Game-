package extrabees.trees;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.LevelAccessor;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.configurations.NoneFeatureConfiguration;

import forestry.api.arboriculture.ITreeGenData;
import forestry.api.arboriculture.ITreeGenerator;
import forestry.api.core.genetics.IGenome;

final class ExtraTreeGenerator implements ITreeGenerator {
	private final TreeWood wood;

	ExtraTreeGenerator(TreeWood wood) {
		this.wood = wood;
	}

	@Override
	public Feature<NoneFeatureConfiguration> getTreeFeature(ITreeGenData tree) {
		return new ExtraTreeFeature(tree, this.wood);
	}

	@Override
	public boolean setLogBlock(IGenome genome, LevelAccessor level, BlockPos pos, Direction facing) {
		return level.setBlock(pos, this.wood.log.get().defaultBlockState().setValue(RotatedPillarBlock.AXIS, facing.getAxis()), 19);
	}

	@Override
	public boolean setLeaves(IGenome genome, LevelAccessor level, BlockPos pos, RandomSource rand) {
		return level.setBlock(pos, this.wood.leaves.get().defaultBlockState(), 19);
	}
}
