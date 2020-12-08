air_blocks = [
    'air',
    'cave_air'
]

water_blocks = [
    'water',
    'flowing_water'
]

# CARE: does not contain fences!
# transparent_blocks = water_blocks + [
transparent_blocks = [
    'air',
    'cave_air',
    # all glass types
    # 'glass',
    # 'stained_glass',
    # 'glass_pane',
    # 'stained_glass_pane',
    # all slabs
    # 'stone_slab',
    # 'stone_slab2',
    # 'wooden_slab',
    # 'purpur_slab',
    'lava',
    'flowing_lava'
    # 'water',
    # 'flowing_water'
]

stone_blocks = [
    'stone',
    'andesite',
    'diorite',
    'granite',
    'bedrock',
    'smooth_stone',
    'polished_andesite',
    'polished_diorite',
    'polished_granite'
]

sandstone_blocks = [
    'chiseled_red_sandstone',
    'chiseled_sandstone',
    'cut_red_sandstone'
    'cut_sandstone',
    'red_sand',
    'red_sandstone',
    'sand',
    'sandstone',
    'smooth_red_sandstone',
    'smooth_sandstone'
]

job_site_blocks = [
    'crafting_table',
    'furnace',
    'barrel',
    'cartography_table',
    'composter',
    'fletching_table',
    'loom',
    'smithing_table',
    'smoker',
    'dispenser', # TODO
    'dropper',
    'observer',
    'lodestone',
    'respawn_anchor',
    'jukebox',
    'target'
]

nether_blocks = [
    'ancient_debris',
    'basalt',
    'polished_basalt',
    'crimson_hyphae',
    'warped_hyphae',
    'stripped_crimson_hyphae',
    'stripped_warped_hyphae',
    'chorus_flower',
    'chorus_plant',
    'crimson_nylium',
    'warped_nylium',
    'crimson_stem',
    'warped_stem',
    'stripped_crimson_stem',
    'stripped_warped_stem',
    'soul_sand',
    'soul_soil'
]

# TODO what about ice and blue ice
solid_blocks = stone_blocks + sandstone_blocks + [
    'dirt',
    'coarse_dirt',
    'grass',
    'farmland',
    'grass_path',
    'gravel',
    'clay',
    'bookshelf',
    'cobblestone',
    'mossy_cobblestone',
    'infested_stone',
    'infested_cobblestone',
    'blackstone',
    'polished_blackstone',
    'mycelium',
    'podzol',
    'bee_nest',
    'beehive',
    'mushroom_stem',
    'pumpkin',
    'carved_pumpkin',
    'jack_o_lantern',
    'melon',
    'netherrack',
    'obsidian',
    'crying_obsidian',
    'dark_prismarine',
    'prismarine'
    'end_stone',
    'gilded_blackstone',
    'sea_lantern',
    'shroomlight',
    'glowstone',
    'redstone_lamp',
    'purpur_pillar',
    'quartz_pillar',
    'smooth_quartz',
    'sponge',
    'wet_sponge',
    'tnt'
] + nether_blocks + job_site_blocks

underground_blocks = [
    'stone',
    'dirt',
    'gravel',
    'andesite',
    'diorite',
    'granite',
    'bedrock'
]

def is_air(block_id):
    return block_id in air_blocks

def is_water(block_id):
    return block_id in water_blocks

###################################################################################################

def is_glass(block_id):
    return 'glass' in block_id

def is_leave(block_id):
    return 'leaves' in block_id

def is_fence(block_id):
    return 'fence' in block_id

# TODO does also find double slabs
def is_slab(block_id):
    return 'slab' in block_id

def is_transparent(block_id):
    return block_id in transparent_blocks or is_leave(block_id) or is_glass(block_id) or is_fence(block_id) or is_slab(block_id)

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
    return 'block' in block_id

def is_wood(block_id):
    return 'wood' in block_id

def is_log(block_id):
    return 'log' in block_id

def is_plank(block_id):
    return 'planks' in block_id

def is_woody(block_id):
    return is_log(block_id) or is_plank(block_id) or is_wood(block_id)

def is_wool(block_id):
    return 'wool' in block_id

def is_ore(block_id):
    return 'ore' in block_id

def is_concrete(block_id):
    return 'concrete' in block_id

def is_bricks(block_id):
    return 'bricks' in block_id

def is_terracotta(block_id):
    return 'terracotta' in block_id

def is_solid(block_id):
    return block_id in solid_blocks or is_woody(block_id) or is_concrete(block_id) or is_terracotta(block_id) or is_wool(block_id) or is_bricks(block_id) or is_block(block_id) or is_ore(block_id)

def is_repl_block(block_id):
    return block_id in underground_blocks or is_ore(block_id)

###################################################################################################

# TODO have this only once
G_BACKGROUND = 0
G_AIR = 1
G_WATER = 2
G_SOLID = 3
G_TRANSPARENT = 4

def get_type(block_id):
    if is_air(block_id):
        return G_AIR
    elif is_water(block_id):
        # return G_WATER
        return G_AIR
    elif is_transparent(block_id):
        # return G_TRANSPARENT
        return G_AIR
    else:
        return G_SOLID

# TODO make replacement type
def get_repl_type(block_id):
    if is_repl_block(block_id):
        return G_SOLID
    else:
        return G_BACKGROUND

# TODO erkenne alle blöcke die transparent oder air sind als eine label (scipy.label)
# dann checke wie groß eine region ist
# wenn kleiner als schwellwert, dann gehe alle blocks durch - wenn keiner davon ein transparenter
# block ist, handelt es sich um ein pocket

# TODO addö water
def get_air_type(block_id):
    if is_air(block_id):
        return G_AIR
    elif is_transparent(block_id):
        return G_TRANSPARENT
    else:
        return G_BACKGROUND

# water:
# markiere alle blocks als solid
# markiere water als background
# checke alle labelregionen
# wenn kleiner schwellwert, dann muss es sich um ein pocket handeln?
def get_water_type(block_id):
    if is_water(block_id):
        return G_BACKGROUND
    else:
        return G_SOLID
