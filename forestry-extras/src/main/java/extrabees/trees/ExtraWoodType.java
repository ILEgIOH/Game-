package extrabees.trees;

import javax.annotation.Nullable;

import com.mojang.authlib.GameProfile;

import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.LevelAccessor;

import forestry.api.arboriculture.IWoodType;
import forestry.api.core.genetics.IGenome;

final class ExtraWoodType implements IWoodType {
	private final TreeWood wood;

	ExtraWoodType(TreeWood wood) {
		this.wood = wood;
	}

	@Override
	public float getHardness() {
		return 2.0f;
	}

	@Override
	public boolean setDefaultLeaves(LevelAccessor level, BlockPos pos, IGenome genome, RandomSource rand, @Nullable GameProfile owner) {
		return level.setBlock(pos, this.wood.leaves.get().defaultBlockState(), 19);
	}

	@Override
	public String getSerializedName() {
		return this.wood.def.id();
	}

	@Override
	public String toString() {
		return getSerializedName();
	}
}
