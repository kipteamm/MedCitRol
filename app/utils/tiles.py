tile_index_map = {
    "windmill" : 66,
    "windmill-0" : 67,
    "windmill-7" : 68,
    "farm_land" : 91,
    "well" : 92,
    "hut" : 118,
    "rye_seeds" : 126,
    "rye_growing" : 127,
    "rye_harvestable" : 128,
}

def get_tile_index(tile_type: str) -> int:
    return tile_index_map.get(tile_type, 0)