air_blocks = [
    'air',
    'cave_air'
]

water_blocks = [
    'water',
    'flowing_water'
]

# CARE: does not contain fences!
transparent_blocks = water_blocks + [
    'air',
    'cave_air',
    # all glass types
    'glass',
    'stained_glass',
    'glass_pane',
    'stained_glass_pane',
    # all leaves
    'leaves',
    'leaves2',
    # all slabs
    'stone_slab'
    'stone_slab2'
    'wooden_slab',
    'purpur_slab',
    'lava',
    'flowing_lava',
    # 'water',
    # 'flowing_water'
]

solid_blocks = [
    'stone',
    'dirt',
    'wood'
]

def is_air(block_id):
    return block_id in air_blocks

def is_water(block_id):
    return block_id in water_blocks

# def is_glass(block_id):
#     return 'glass' in block_id

def is_fence(block_id):
    return 'fence' in block_id

def is_transparent(block_id):
    return block_id in transparent_blocks or is_fence(block_id)

def is_solid(block_id):
    return block_id in solid_blocks
