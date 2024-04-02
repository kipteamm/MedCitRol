tile_index_map = {
    "well" : 92,
    "hut" : 118
}

def get_tile_index(tile_type: str) -> int:
    return tile_index_map.get(tile_type, 0)