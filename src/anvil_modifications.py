import math
import zlib
from io import BytesIO

from anvil import Chunk, Region
from nbt import nbt


def save_region(self, file=None, region: Region = None) -> bytes:
    """
    Returns the region as bytes with
    the anvil file format structure,
    aka the final ``.mca`` file.

    Parameters
    ----------
    file
        Either a path or a file object, if given region
        will be saved there.
    """
    # Store all the chunks data as zlib compressed nbt data
    chunks_data = []
    for chunk in self.chunks:
        if chunk is None:
            chunks_data.append(None)
            continue
        chunk_data = BytesIO()
        if isinstance(chunk, Chunk):
            nbt_data = nbt.NBTFile()
            nbt_data.tags.append(nbt.TAG_Int(name="DataVersion", value=chunk.version))
            nbt_data.tags.append(chunk.data)
        else:
            data = region.get_chunk(chunk.x, chunk.z).data
            nbt_data = chunk.save(data)
        nbt_data.write_file(buffer=chunk_data)
        chunk_data.seek(0)
        chunk_data = zlib.compress(chunk_data.read())
        chunks_data.append(chunk_data)

    # This is what is added after the location and timestamp header
    chunks_bytes = bytes()
    offsets = []
    for chunk in chunks_data:
        if chunk is None:
            offsets.append(None)
            continue
        # 4 bytes are for length, b"\x02" is the compression type which is 2 since its using zlib
        to_add = (len(chunk) + 1).to_bytes(4, "big") + b"\x02" + chunk

        # offset in 4KiB sectors
        sector_offset = len(chunks_bytes) // 4096
        sector_count = math.ceil(len(to_add) / 4096)
        offsets.append((sector_offset, sector_count))

        # Padding to be a multiple of 4KiB long
        to_add += bytes(4096 - (len(to_add) % 4096))
        chunks_bytes += to_add

    locations_header = bytes()
    for offset in offsets:
        # None means the chunk is not an actual chunk in the region
        # and will be 4 null bytes, which represents non-generated chunks to minecraft
        if offset is None:
            locations_header += bytes(4)
        else:
            # offset is (sector offset, sector count)
            locations_header += (offset[0] + 2).to_bytes(3, "big") + offset[1].to_bytes(1, "big")

    # Set them all as 0
    timestamps_header = bytes(4096)

    final = locations_header + timestamps_header + chunks_bytes

    # Pad file to be a multiple of 4KiB in size
    # as Minecraft only accepts region files that are like that
    final += bytes(4096 - (len(final) % 4096))
    assert len(final) % 4096 == 0  # just in case

    # Save to a file if it was given
    if file:
        if isinstance(file, str):
            with open(file, "wb") as f:
                f.write(final)
        else:
            file.write(final)
    return final


def save_chunk(self, data) -> nbt.NBTFile:
    """
    Saves the chunk data to a :class:`NBTFile`

    Notes
    -----
    Does not contain most data a regular chunk would have,
    but minecraft stills accept it.
    """
    root = nbt.NBTFile()
    root.tags.append(nbt.TAG_Int(name="DataVersion", value=self.version))
    level = nbt.TAG_Compound()
    # Needs to be in a separate line because it just gets
    # ignored if you pass it as a kwarg in the constructor
    level.name = "Level"

    if data:
        if data.get("Biomes") is not None:
            level.tags.append(data["Biomes"])
        if data.get("Heightmaps") is not None:
            level.tags.append(data["Heightmaps"])
        # level.tags.append(data["CarvingMasks"])
        if data.get("Entities") is not None:
            level.tags.append(data["Entities"])
        if data.get("TileEntities") is not None:
            level.tags.append(data["TileEntities"])

        # if data.get("TileTicks") is not None:
        #     level.tags.append(data["TileTicks"])
        if data.get("LiquidTicks") is not None:
            level.tags.append(data["LiquidTicks"])
        ########
        if data.get("Lights") is not None:
            level.tags.append(data["Lights"])
        if data.get("LiquidsToBeTicked") is not None:
            level.tags.append(data["LiquidsToBeTicked"])
        if data.get("ToBeTicked") is not None:
            level.tags.append(data["ToBeTicked"])
        if data.get("CarvingMasks") is not None:
            level.tags.append(data["CarvingMasks"])

        ##########
        if data.get("PostProcessing") is not None:
            level.tags.append(data["PostProcessing"])
        if data.get("Structures") is not None:
            level.tags.append(data["Structures"])

        level.tags.extend(
            [
                # nbt.TAG_List(name="Entities", type=nbt.TAG_Compound),
                # nbt.TAG_List(name="TileEntities", type=nbt.TAG_Compound),
                # nbt.TAG_List(name="LiquidTicks", type=nbt.TAG_Compound),
                nbt.TAG_Int(name="xPos", value=self.x),
                nbt.TAG_Int(name="zPos", value=self.z),
                # nbt.TAG_Long(name="LastUpdate", value=data["LastUpdate"]),
                nbt.TAG_Long(name="LastUpdate", value=0),
                # nbt.TAG_Long(name="InhabitedTime", value=data["InhabitedTime"]),
                nbt.TAG_Long(name="InhabitedTime", value=0),
                nbt.TAG_Byte(name="isLightOn", value=1),
                nbt.TAG_String(name="Status", value="full"),
            ]
        )

        # entities = self.add_entities(data["Entities"])
        # level.tags.append(entities)
        # nbt.TAG_List(name="Entities", type=nbt.TAG_Compound)
    else:
        level.tags.extend(
            [
                # nbt.TAG_List(name="Entities", type=nbt.TAG_Compound),
                nbt.TAG_List(name="TileEntities", type=nbt.TAG_Compound),
                nbt.TAG_List(name="LiquidTicks", type=nbt.TAG_Compound),
                nbt.TAG_Int(name="xPos", value=self.x),
                nbt.TAG_Int(name="zPos", value=self.z),
                nbt.TAG_Long(name="LastUpdate", value=0),
                nbt.TAG_Long(name="InhabitedTime", value=0),
                nbt.TAG_Byte(name="isLightOn", value=1),
                nbt.TAG_String(name="Status", value="full"),
            ]
        )

    sections = nbt.TAG_List(name="Sections", type=nbt.TAG_Compound)
    for s in self.sections:
        if s:
            p = s.palette()
            # Minecraft does not save sections that are just air
            # So we can just skip them
            if len(p) == 1 and p[0].name() == "minecraft:air":
                continue
            sections.tags.append(s.save())
    level.tags.append(sections)
    root.tags.append(level)
    return root
