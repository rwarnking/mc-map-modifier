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

solid_blocks = [
    'stone',
    'dirt',
    'grass',
    'cobblestone'
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

def is_log(block_id):
    return 'log' in block_id

def is_plank(block_id):
    return 'planks' in block_id

def is_solid(block_id):
    return block_id in solid_blocks or is_log(block_id) or is_plank(block_id)

###################################################################################################

# TODO have this only once
G_AIR = 1
G_WATER = 2
G_SOLID = 3
G_TRANSPARENT = 4

def get_type(block_id):
    if is_air(block_id):
        return G_AIR
    elif is_water(block_id):
        return G_WATER
    elif is_transparent(block_id):
        return G_TRANSPARENT
    else:
        return G_SOLID
