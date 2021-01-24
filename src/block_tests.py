# For globals
import config as cfg
from block_lists import (
    air_blocks,
    fluid_blocks,
    plants,
    solid_blocks,
    underground_blocks,
    water_blocks,
)

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
