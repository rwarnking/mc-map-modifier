import config as cfg

###################################################################################################
# Lists of transparent block_ids
###################################################################################################

air_blocks = ["air"]

water_blocks = ["water"]  # , "flowing_water"]

lava_blocks = ["lava"]  # , "flowing_lava"]

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

stairs = []

slabs = [
    "stone_slab",
    "acacia_slab",
    "birch_slab",
    "brick_slab",
    "cobblestone_slab",
    "dark_oak_slab",
    "jungle_slab",
    "nether_brick_slab",
    "oak_slab",
    "petrified_oak_slab",
    "purpur_slab",
    "quartz_slab",
    "red_sandstone_slab",
    "sandstone_slab",
    "spruce_slab",
    "stone_brick_slab",
]

fences = [
    "acacia_fence",
    "acacia_fence_gate",
    "birch_fence",
    "birch_fence_gate",
    "dark_oak_fence",
    "dark_oak_fence_gate",
    "jungle_fence",
    "jungle_fence_gate",
    "nether_brick_fence",
    "oak_fence",
    "oak_fence_gate",
    "spruce_fence",
    "spruce_fence_gate",
]

walls = []

signs = [
    "oak_sign",
    "oak_wall_sign",
]

leaves = [
    "acacia_leaves",
    "birch_leaves",
    "dark_oak_leaves",
    "jungle_leaves",
    "oak_leaves",
    "spruce_leaves",
]

# TODO check for missing plants like wheat
plants = [
    "grass",
    "fern",
    "tall_grass",
    "large_fern",
    "allium",
    "azure_bluet",
    "blue_orchid",
    "brown_mushroom",
    "dandelion",
    "dead_bush",
    "lilac",
    "orange_tulip",
    "oxeye_daisy",
    "peony",
    "pink_tulip",
    "poppy",
    "red_mushroom",
    "red_tulip",
    "rose_bush",
    "white_tulip",
]


fluid_blocks = water_blocks + lava_blocks

transparent_blocks = []


###################################################################################################
# Listss of solid block_ids
###################################################################################################


# TODO what about ice and blue ice are they transparent?
solid_blocks = [
    "dirt",
    "coarse_dirt",
    "grass_block",
    "farmland",
    "grass_path",
    "gravel",
    "clay",
    "bookshelf",
    "cobblestone",
    "mossy_cobblestone",
    "infested_stone",
    "infested_cobblestone",
    "mycelium",
    "podzol",
    "mushroom_stem",
    "pumpkin",
    "jack_o_lantern",
    "melon",
    "netherrack",
    "obsidian",
    "dark_prismarine",
    "prismarine",
    "end_stone",
    "sea_lantern",
    "glowstone",
    "redstone_lamp",
    "purpur_pillar",
    "quartz_pillar",
    "smooth_quartz",
    "sponge",
    "wet_sponge",
    "tnt",
]

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

underground_blocks = [
    "stone",
    "dirt",
    "gravel",
    "andesite",
    "diorite",
    "granite",
    "bedrock",
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

nether_blocks = [
    "soul_sand",
]

job_site_blocks = [
    "crafting_table",
    "furnace",
    "dispenser",
    "dropper",
    "observer",
    "jukebox",
]


# def add0():
#     "nether_bricks",

# https://minecraft.gamepedia.com/Java_Edition_1.9

# def add9():
# "chorus_flower",
# "chorus_plant",
# "dragon_head",
# "end_gateway",
# "end_rod"
# "end_stone_bricks",
# "frosted_ice",
# "grass_path",
# "purpur_block",
# "purpur_pillar",
# "purpur_stairs",
# "purpur_slab",
# "structure_block",

# def add10():
# "nether_wart_block",
# "red_nether_bricks",
# "magma_block",
# "bone_block",


def add11():
    global job_site_blocks

    job_site_blocks += [
        "observer",
    ]

    # "shulker_box",
    # "white_shulker_box",
    # "orange_shulker_box",
    # "magenta_shulker_box",
    # "light_blue_shulker_box",
    # "yellow_shulker_box",
    # "lime_shulker_box",
    # "pink_shulker_box",
    # "gray_shulker_box",
    # "light_gray_shulker_box",
    # "cyan_shulker_box",
    # "purple_shulker_box",
    # "blue_shulker_box",
    # "brown_shulker_box",
    # "green_shulker_box",
    # "red_shulker_box",
    # "black_shulker_box",


# def add12():
# "white_bed",
# "orange_bed",
# "magenta_bed",
# "light_blue_bed",
# "yellow_bed",
# "lime_bed",
# "pink_bed",
# "gray_bed",
# "light_gray_bed",
# "cyan_bed",
# "purple_bed",
# "blue_bed",
# "brown_bed",
# "green_bed",
# "black_bed",

# "white_concrete",
# "orange_concrete",
# "magenta_concrete",
# "light_blue_concrete",
# "yellow_concrete",
# "lime_concrete",
# "pink_concrete",
# "gray_concrete",
# "light_gray_concrete",
# "cyan_concrete",
# "purple_concrete",
# "blue_concrete",
# "brown_concrete",
# "green_concrete",
# "red_concrete",
# "black_concrete",

# "white_concrete_powder",
# "orange_concrete_powder",
# "magenta_concrete_powder",
# "light_blue_concrete_powder",
# "yellow_concrete_powder",
# "lime_concrete_powder",
# "pink_concrete_powder",
# "gray_concrete_powder",
# "light_gray_concrete_powder",
# "cyan_concrete_powder",
# "purple_concrete_powder",
# "blue_concrete_powder",
# "brown_concrete_powder",
# "green_concrete_powder",
# "red_concrete_powder",
# "black_concrete_powder",

# "white_glazed_terracotta",
# "orange_glazed_terracotta",
# "magenta_glazed_terracotta",
# "light_blue_glazed_terracotta",
# "yellow_glazed_terracotta",
# "lime_glazed_terracotta",
# "pink_glazed_terracotta",
# "gray_glazed_terracotta",
# "light_gray_glazed_terracotta",
# "cyan_glazed_terracotta",
# "purple_glazed_terracotta",
# "blue_glazed_terracotta",
# "brown_glazed_terracotta",
# "green_glazed_terracotta",
# "red_glazed_terracotta",
# "black_glazed_terracotta",


def add13():
    # "blue_ice",
    # "bubble_column",
    # "carved_pumpkin",
    # "conduit",
    # "dried_kelp_block",
    # "turtle_egg",

    # "tube_coral",
    # "brain_coral",
    # "bubble_coral",
    # "fire_coral",
    # "horn_coral",
    # "dead_tube_coral",
    # "dead_brain_coral",
    # "dead_bubble_coral",
    # "dead_fire_coral",
    # "dead_horn_coral",

    # "tube_coral_fan",
    # "brain_coral_fan",
    # "bubble_coral_fan",
    # "fire_coral_fan",
    # "horn_coral_fan",
    # "dead_tube_coral_fan",
    # "dead_brain_coral_fan",
    # "dead_bubble_coral_fan",
    # "dead_fire_coral_fan",
    # "dead_horn_coral_fan",
    # "tube_coral_wall_fan",
    # "brain_coral_wall_fan",
    # "bubble_coral_wall_fan",
    # "fire_coral_wall_fan",
    # "horn_coral_wall_fan",
    # "dead_tube_coral_wall_fan",
    # "dead_brain_coral_wall_fan",
    # "dead_bubble_coral_wall_fan",
    # "dead_fire_coral_wall_fan",
    # "dead_horn_coral_wall_fan",

    # "stripped_oak_log",
    # "stripped_spruce_log",
    # "stripped_birch_log",
    # "stripped_jungle_log",
    # "stripped_acacia_log",
    # "stripped_dark_oak_log",
    global air_blocks
    global stairs
    global slabs
    global plants

    air_blocks += [
        "cave_air",
        "void_air",
    ]

    stairs += [
        "prismarine_stairs",
        "prismarine_brick_stairs",
        "dark_prismarine_stairs",
    ]

    slabs += [
        "dark_prismarine_slab",
        "prismarine_brick_slab",
        "prismarine_slab",
    ]

    plants += [
        "kelp",
        "kelp_plant",
        "seagrass",
        "tall_seagrass",
        "sea_pickle",
    ]


def add14():
    # "campfire",
    # "lantern",
    # "grindstone",
    # "bell",
    # "jigsaw",
    # "lectern",
    # "scaffolding",
    # "stonecutter",
    # TODO are sapling needed?
    # "bamboo_sapling",

    global job_site_blocks
    global stairs
    global slabs
    global walls
    global signs
    global plants

    # solid_blocks += [
    # ]

    job_site_blocks += [
        "barrel",
        "blast_furnace",
        "cartography_table",
        "composter",
        "fletching_table",
        "loom",
        "smithing_table",
        "smoker",
    ]

    stairs += [
        "andesite_stairs",
        "polished_andesite_stairs",
        "diorite_stairs",
        "polished_diorite_stairs",
        "granite_stairs",
        "polished_granite_stairs",
        "mossy_stone_brick_stairs",
        "mossy_cobblestone_stairs",
        "smooth_sandstone_stairs",
        "smooth_red_sandstone_stairs",
        "smooth_quartz_stairs",
        "red_nether_brick_stairs",
        "end_stone_brick_stairs",
    ]

    slabs += [
        "smooth_stone_slab",
        "andesite_slab",
        "polished_andesite_slab",
        "diorite_slab",
        "polished_diorite_slab",
        "granite_slab",
        "polished_granite_slab",
        "mossy_stone_brick_slab",
        "mossy_cobblestone_slab",
        "smooth_sandstone_slab",
        "cut_sandstone_slab",
        "smooth_red_sandstone_slab",
        "cut_red_sandstone_slab",
        "smooth_quartz_slab",
        "red_nether_brick_slab",
        "end_stone_brick_slab",
    ]

    walls += [
        "brick_wall",
        "andesite_wall",
        "diorite_wall",
        "granite_wall",
        "prismarine_wall",
        "stone_brick_wall",
        "mossy_stone_brick_wall",
        "sandstone_wall",
        "red_sandstone_wall",
        "nether_brick_wall",
        "red_nether_brick_wall",
        "end_stone_brick_wall",
    ]

    signs += [
        "spruce_sign",
        "birch_sign",
        "acacia_sign",
        "jungle_sign",
        "dark_oak_sign",
        "spruce_wall_sign",
        "birch_wall_sign",
        "jungle_wall_sign",
        "acacia_wall_sign",
        "dark_oak_wall_sign",
    ]

    plants += [
        "bamboo",
        "cornflower",
        "lily_of_the_valley",
        "wither_rose",
        "sweet_berry_bush",
    ]


def add15():
    global solid_blocks
    # TODO blocks to add
    # "honey_block",
    # "honeycomb_block",

    solid_blocks += [
        "bee_nest",
        "beehive",
    ]


def add16():
    # TODO blocks to add
    # "netherite_block",
    # "chain",
    # "cracked_nether_bricks",
    # "chiseled_nether_bricks",
    # "crimson_planks",
    # "warped_planks",
    # "nether_gold_ore",
    # "quartz_bricks",
    # "soul_campfire",
    # "soul_fire",
    # "soul_lantern",
    # "soul_torch",
    # "soul_wall_torch",
    # "warped_wart_block",

    global solid_blocks
    global nether_blocks
    global job_site_blocks
    global stairs
    global slabs
    global fences
    global walls
    global signs
    global plants

    solid_blocks += [
        "crying_obsidian",
        "blackstone",
        "polished_blackstone",
        "gilded_blackstone",
        "shroomlight",
    ]

    # TODO is the nether array adjusted before the solid blocks is constructed?
    nether_blocks += [
        "ancient_debris",
        "crimson_nylium",
        "warped_nylium",
        "crimson_stem",
        "warped_stem",
        "stripped_crimson_stem",
        "stripped_warped_stem",
        "soul_soil",
        "basalt",
        "polished_basalt",
        "crimson_hyphae",
        "warped_hyphae",
        "stripped_crimson_hyphae",
        "stripped_warped_hyphae",
    ]

    job_site_blocks += [
        "lodestone",
        "target",
        "respawn_anchor",
    ]

    stairs += [
        "crimson_stairs",
        "warped_stairs",
        "blackstone_stairs",
        "polished_blackstone_stairs",
        "polished_blackstone_brick_stairs",
    ]

    slabs += [
        "blackstone_slab",
        "polished_blackstone_brick_slab",
        "polished_blackstone_slab",
        "crimson_slab",
        "warped_slab",
    ]

    fences += [
        "crimson_fence",
        "crimson_fence_gate",
        "warped_fence",
        "warped_fence_gate",
    ]

    walls += [
        "blackstone_wall",
        "polished_blackstone_wall",
        "polished_blackstone_brick_wall",
    ]

    signs += [
        "crimson_sign",
        "warped_sign",
        "crimson_wall_sign",
        "warped_wall_sign",
    ]

    plants += [
        "crimson_fungus",
        "warped_fungus",
        "crimson_roots",
        "warped_roots",
        "nether_sprouts",
        "twisting_vines",
        "twisting_vines_plant",
        "weeping_vines",
        "weeping_vines_plant",
    ]


def add17():
    global stairs

    stairs += [
        "cut_copper_stairs",
        "lightly_weathered_cut_copper_stairs",
        "semi_weathered_cut_copper_stairs",
        "weathered_cut_copper_stairs",
        "waxed_cut_copper_stairs",
        "waxed_lightly_weathered_cut_copper_stairs",
        "waxed_semi_weathered_cut_copper_stairs",
    ]


def init_lists():
    if cfg.VERSION >= 11:
        add11()
    # if cfg.VERSION >= 12:
    # add12()
    if cfg.VERSION >= 13:
        add13()
    if cfg.VERSION >= 14:
        add14()
    if cfg.VERSION >= 15:
        add15()
    if cfg.VERSION >= 16:
        add16()
    if cfg.VERSION >= 17:
        add17()

    global transparent_blocks
    global solid_blocks
    transparent_blocks += fluid_blocks + glass + slabs + fences + leaves
    solid_blocks += stone_blocks + sandstone_blocks + nether_blocks + job_site_blocks


init_lists()
