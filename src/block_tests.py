# For globals
import config as cfg

###################################################################################################
# Arrays of transparent block_ids
###################################################################################################

air_blocks = ["air", "cave_air"]

water_blocks = ["water", "flowing_water"]

lava_blocks = ["lava", "flowing_lava"]

# TODO check for missing plants like wheat
plants = [
    "grass",
    "fern",
    "tall_grass",
    "large_fern",
    "kelp",
    "kelp_plant",
    "seagrass",
    "tall_seagrass",
    "allium",
    "azure_bluet",
    "bamboo",
    "blue_orchid",
    "brown_mushroom",
    "cornflower",
    "crimson_fungus",
    "dandelion",
    "dead_bush",
    "lilac",
    "lily_of_the_valley",
    "orange_tulip",
    "oxeye_daisy",
    "peony",
    "pink_tulip",
    "poppy",
    "red_mushroom",
    "red_tulip",
    "rose_bush",
    "warped_fungus",
    "white_tulip",
    "wither_rose",
]

glass = [
    "glass",
    "glass_pane",
    "black_stained_glass",
    "black_stained_glass_pane",
    "blue_stained_glass",
    "blue_stained_glass_pane",
    "brown_stained_glass",
    "brown_stained_glass_pane",
    "cyan_stained_glass",
    "cyan_stained_glass_pane",
    "gray_stained_glass",
    "gray_stained_glass_pane",
    "green_stained_glass",
    "green_stained_glass_pane",
    "light_blue_stained_glass",
    "light_blue_stained_glass_pane",
    "light_gray_stained_glass",
    "light_gray_stained_glass_pane",
    "lime_stained_glass",
    "lime_stained_glass_pane",
    "magenta_stained_glass",
    "magenta_stained_glass_pane",
    "orange_stained_glass",
    "orange_stained_glass_pane",
    "pink_stained_glass",
    "pink_stained_glass_pane",
    "purple_stained_glass",
    "purple_stained_glass_pane",
    "red_stained_glass",
    "red_stained_glass_pane",
    "white_stained_glass",
    "white_stained_glass_pane",
    "yellow_stained_glass",
    "yellow_stained_glass_pane",
]

slabs = [
    "acacia_slab",
    "andesite_slab",
    "birch_slab",
    "blackstone_slab",
    "brick_slab",
    "cobblestone_slab",
    "crimson_slab",
    "cut_red_sandstone_slab",
    "cut_sandstone_slab",
    "dark_oak_slab",
    "dark_prismarine_slab",
    "diorite_slab",
    "end_stone_brick_slab",
    "granite_slab",
    "jungle_slab",
    "mossy_cobblestone_slab",
    "mossy_stone_brick_slab",
    "nether_brick_slab",
    "oak_slab",
    "petrified_oak_slab",
    "polished_andesite_slab",
    "polished_blackstone_brick_slab",
    "polished_blackstone_slab",
    "polished_diorite_slab",
    "polished_granite_slab",
    "prismarine_brick_slab",
    "prismarine_slab",
    "purpur_slab",
    "quartz_slab",
    "red_nether_brick_slab",
    "red_sandstone_slab",
    "sandstone_slab",
    "smooth_quartz_slab",
    "smooth_red_sandstone_slab",
    "smooth_sandstone_slab",
    "smooth_stone_slab",
    "spruce_slab",
    "stone_brick_slab",
    "stone_slab",
    "warped_slab",
]

fences = [
    "acacia_fence",
    "acacia_fence_gate",
    "birch_fence",
    "birch_fence_gate",
    "crimson_fence",
    "crimson_fence_gate",
    "dark_oak_fence",
    "dark_oak_fence_gate",
    "jungle_fence",
    "jungle_fence_gate",
    "nether_brick_fence",
    "oak_fence",
    "oak_fence_gate",
    "spruce_fence",
    "spruce_fence_gate",
    "warped_fence",
    "warped_fence_gate",
]

leaves = [
    "acacia_leaves",
    "birch_leaves",
    "dark_oak_leaves",
    "jungle_leaves",
    "oak_leaves",
    "spruce_leaves",
]


fluid_blocks = water_blocks + lava_blocks

transparent_blocks = fluid_blocks + glass + slabs + fences + leaves


###################################################################################################
# Arrays of solid block_ids
###################################################################################################


stone_blocks = [
    "stone",
    "andesite",
    "diorite",
    "granite",
    "bedrock",
    "smooth_stone",
    "polished_andesite",
    "polished_diorite",
    "polished_granite",
]

sandstone_blocks = [
    "chiseled_red_sandstone",
    "chiseled_sandstone",
    "cut_red_sandstone",
    "cut_sandstone",
    "red_sand",
    "red_sandstone",
    "sand",
    "sandstone",
    "smooth_red_sandstone",
    "smooth_sandstone",
]

job_site_blocks = [
    "crafting_table",
    "furnace",
    "barrel",
    "cartography_table",
    "composter",
    "fletching_table",
    "loom",
    "smithing_table",
    "smoker",
    "dispenser",
    "dropper",
    "observer",
    "lodestone",
    "respawn_anchor",
    "jukebox",
    "target",
]

nether_blocks = [
    "ancient_debris",
    "basalt",
    "polished_basalt",
    "crimson_hyphae",
    "warped_hyphae",
    "stripped_crimson_hyphae",
    "stripped_warped_hyphae",
    "chorus_flower",
    "chorus_plant",
    "crimson_nylium",
    "warped_nylium",
    "crimson_stem",
    "warped_stem",
    "stripped_crimson_stem",
    "stripped_warped_stem",
    "soul_sand",
    "soul_soil",
]

# TODO what about ice and blue ice are they transparent?
solid_blocks = (
    stone_blocks
    + sandstone_blocks
    + [
        "dirt",
        "coarse_dirt",
        "grass_block",  # TODO is already cotained in blocks only needed for test map
        "farmland",
        "grass_path",
        "gravel",
        "clay",
        "bookshelf",
        "cobblestone",
        "mossy_cobblestone",
        "infested_stone",
        "infested_cobblestone",
        "blackstone",
        "polished_blackstone",
        "mycelium",
        "podzol",
        "bee_nest",
        "beehive",
        "mushroom_stem",
        "pumpkin",
        "carved_pumpkin",
        "jack_o_lantern",
        "melon",
        "netherrack",
        "obsidian",
        "crying_obsidian",
        "dark_prismarine",
        "prismarine",
        "end_stone",
        "gilded_blackstone",
        "sea_lantern",
        "shroomlight",
        "glowstone",
        "redstone_lamp",
        "purpur_pillar",
        "quartz_pillar",
        "smooth_quartz",
        "sponge",
        "wet_sponge",
        "tnt",
    ]
    + nether_blocks
    + job_site_blocks
)

underground_blocks = [
    "stone",
    "dirt",
    "gravel",
    "andesite",
    "diorite",
    "granite",
    "bedrock",
]


###################################################################################################
# Transparent functions
###################################################################################################


def is_air(block_id):
    return block_id in air_blocks


def is_water(block_id):
    return block_id in water_blocks


def is_glass(block_id):
    return "glass" in block_id


def is_leave(block_id):
    return "leaves" in block_id


def is_fence(block_id):
    return "fence" in block_id


# TODO does also find double slabs
def is_slab(block_id):
    return "slab" in block_id


def is_plant(block_id):
    return block_id in plants or "sapling" in block_id


def is_transparent(block_id):
    return (
        block_id in fluid_blocks
        or is_leave(block_id)
        or is_glass(block_id)
        or is_fence(block_id)
        or is_slab(block_id)
        or is_plant(block_id)
    )


###################################################################################################
# Solid functions
###################################################################################################


# bone_block
# coral_block
# red + brown_mushroom_block
# command_block
# quartz_block
# coal_block, diamond_block, emerald_block, gold_block, iron_block, lapis_block, redstone_block
# kelp_block
# grass_block
# hay_block
# honey_block
# magma_block
# nether_wart_block, warped_wart_block
# netherite_block
# note_block
# purpur_block, quartz_block
# slime_block, snow_block
# structure_block


def is_block(block_id):
    return "block" in block_id


def is_wood(block_id):
    return "wood" in block_id


def is_log(block_id):
    return "log" in block_id


def is_plank(block_id):
    return "planks" in block_id


def is_woody(block_id):
    return is_log(block_id) or is_plank(block_id) or is_wood(block_id)


def is_wool(block_id):
    return "wool" in block_id


def is_ore(block_id):
    return "ore" in block_id


def is_concrete(block_id):
    return "concrete" in block_id


def is_bricks(block_id):
    return "bricks" in block_id


def is_terracotta(block_id):
    return "terracotta" in block_id


def is_solid(block_id):
    return (
        block_id in solid_blocks
        or is_woody(block_id)
        or is_concrete(block_id)
        or is_terracotta(block_id)
        or is_wool(block_id)
        or is_bricks(block_id)
        or is_block(block_id)
        or is_ore(block_id)
    )


def is_repl_block(block_id):
    return block_id in underground_blocks or is_ore(block_id)


###################################################################################################

# def get_type(block_id):
#     if is_air(block_id):
#         return cfg.G_AIR
#     elif is_water(block_id):
#         return cfg.G_WATER
#     elif is_transparent(block_id):
#         return cfg.G_TRANSPARENT
#     else:
#         return cfg.G_SOLID


def get_repl_type(block_id):
    if is_repl_block(block_id):
        return cfg.G_SOLID
    else:
        return cfg.G_BACKGROUND


# TODO remove this and write a real comment at the right place (same below)
# TODO erkenne alle blöcke die transparent oder air sind als eine label (scipy.label)
# dann checke wie groß eine region ist
# wenn kleiner als schwellwert, dann gehe alle blocks durch - wenn keiner davon ein transparenter
# block ist, handelt es sich um ein pocket

# make two arrays one only for air and one for both, dialate the first
# and check all blocks if they are transparent -> needs more ram but
# it should reduce the amount of labels found


def get_air_type(block_id):
    if is_air(block_id):
        return cfg.G_AIR
    elif is_transparent(block_id) or is_water(block_id):
        return cfg.G_TRANSPARENT
    else:
        return cfg.G_BACKGROUND


# water:
# markiere alle blocks als solid
# markiere water als background
# checke alle labelregionen
# wenn kleiner schwellwert, dann muss es sich um ein pocket handeln?


def get_water_type(block_id):
    if is_water(block_id):
        return cfg.G_BACKGROUND
    else:
        return cfg.G_SOLID


###################################################################################################

# Used for the tunnel functionality


def is_hot(block_id):
    if is_air(block_id) or is_transparent(block_id) or is_water(block_id):
        return True
    else:
        return False
