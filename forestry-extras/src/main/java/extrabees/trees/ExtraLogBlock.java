package extrabees.trees;

import java.util.function.Supplier;

import javax.annotation.Nullable;

import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.neoforge.common.ItemAbilities;
import net.neoforged.neoforge.common.ItemAbility;

class ExtraLogBlock extends RotatedPillarBlock {
	@Nullable
	private final Supplier<Block> stripped;

	ExtraLogBlock(Properties properties, @Nullable Supplier<Block> stripped) {
		super(properties);
		this.stripped = stripped;
	}

	@Nullable
	@Override
	public BlockState getToolModifiedState(BlockState state, UseOnContext context, ItemAbility ability, boolean simulate) {
		if (ability == ItemAbilities.AXE_STRIP && this.stripped != null) {
			return this.stripped.get().defaultBlockState().setValue(AXIS, state.getValue(AXIS));
		}
		return super.getToolModifiedState(state, context, ability, simulate);
	}
}
