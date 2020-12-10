# Blocks per chunk
CHUNK_B_X = 16
CHUNK_B_Y = 256
CHUNK_B_Z = 16

# Chunks per region
REGION_C_X = 32
REGION_C_Z = 32

# Blocks per region
REGION_B_X = REGION_C_X * CHUNK_B_X
REGION_B_Y = CHUNK_B_Y
REGION_B_Z = REGION_C_Z * CHUNK_B_Z
REGION_B_TOTAL = REGION_B_X * REGION_B_Y * REGION_B_Z

# For estimated time
# TODO these times may be dependend on the settings
T_CLASSIFY = 80
T_IDENTIFY = 70
T_MODIFY = 500
T_SAVE = 180

# Algorithm steps
A_CLASSIFY = 0
A_IDENTIFY = 1
A_MODIFY = 2
A_SAVE = 3
A_FINISHED = 4

# TODO use C for classify globals and I for identify?
# Classifier types
G_BACKGROUND = 0
G_AIR = 1
G_WATER = 2
G_SOLID = 3
G_TRANSPARENT = 4

# Identifier types
UNCHANGED = 0
WATERBLOCK = 1
AIRPOCKET = 2
SOLIDAREA = 3

