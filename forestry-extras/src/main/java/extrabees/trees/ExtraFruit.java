package extrabees.trees;

import java.util.ArrayList;
import java.util.List;

import javax.annotation.Nullable;

import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.util.RandomSource;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.LevelAccessor;

import forestry.api.arboriculture.genetics.IFruit;
import forestry.api.core.IProduct;
import forestry.api.core.Product;
import forestry.api.core.genetics.IGenome;
import forestry.api.core.genetics.alleles.TreeChromosomes;

// a ripening leaf fruit: the fruit shows as an overlay on genetic leaves and drops once ripe
final class ExtraFruit implements IFruit {
	private final FruitDef def;
	private final List<IProduct> products;

	ExtraFruit(FruitDef def, Item item) {
		this.def = def;
		this.products = List.of(Product.of(item));
	}

	@Override
	public boolean isDominant() {
		return true;
	}

	@Override
	public int getColour(IGenome genome, BlockGetter world, BlockPos pos, int ripeningTime) {
		return this.def.colour();
	}

	@Override
	public int getDecorativeColor() {
		return this.def.colour();
	}

	@Override
	public boolean isFruitLeaf() {
		return true;
	}

	@Override
	public float getFruitChance(IGenome genome, LevelAccessor level) {
		return genome.getActiveValue(TreeChromosomes.YIELD) * 2.5F;
	}

	@Override
	public int getRipeningPeriod() {
		return this.def.ripening();
	}

	@Override
	public List<IProduct> getSpecialty() {
		return List.of();
	}

	@Override
	public List<ItemStack> getFruits(@Nullable IGenome genome, Level level, int ripeningTime) {
		if (ripeningTime < this.def.ripening()) {
			return List.of();
		}
		RandomSource rand = level.random;
		List<ItemStack> stacks = new ArrayList<>();
		for (IProduct product : this.products) {
			stacks.add(product.createRandomStack(rand));
		}
		return stacks;
	}

	@Nullable
	@Override
	public ResourceLocation getSprite(IGenome genome, BlockGetter world, BlockPos pos, int ripeningTime) {
		return this.def.sprite();
	}

	@Nullable
	@Override
	public ResourceLocation getDecorativeSprite() {
		return this.def.sprite();
	}

	@Override
	public boolean requiresFruitBlocks() {
		return false;
	}

	@Override
	public boolean trySpawnFruitBlock(IGenome genome, LevelAccessor world, RandomSource rand, BlockPos pos) {
		return false;
	}

	@Override
	public List<IProduct> getProducts() {
		return this.products;
	}
}
