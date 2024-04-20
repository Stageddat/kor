from src.global_src.global_emojis import smile_pixel_emoji
from src.global_src.global_roles import (
        pixel_art_role_id,
        farm_role_id,
        structure_role_id
)

from src.global_src.global_path import (
        pixel_art_dm_embed_path,
        pixel_art_welcome_embed_path,
        farm_dm_embed_path,
        farm_welcome_embed_path,
        strucure_dm_embed_path,
        strucure_welcome_embed_path
)

ticket_type_dict = {
    "👾Request A Pixel Art Builder👾": {
        "type": "pixel_art",
        "button_label": "Pixel Art",
        "emoji": smile_pixel_emoji,
        "role_id": pixel_art_role_id,
        "category_id": 1151613273200930948,
        "dm_embed_path": pixel_art_dm_embed_path,
        "welcome_embed_path": pixel_art_welcome_embed_path,
        "short_name": "pixel",
    },
    "🧑‍🌾Request A Farm Builder🧑‍🌾": {
        "type": "farm",
        "button_label": "Farm",
        "emoji": "🧑‍🌾",
        "role_id": farm_role_id,
        "category_id": 1151613274589253745,
        "dm_embed_path": farm_dm_embed_path,
        "welcome_embed_path": farm_welcome_embed_path,
        "short_name": "farm"
    },
    "🏠Request a Structure Builder🏠": {
        "type": "structure",
        "button_label": "Structure",
        "emoji": "🏠",
        "role_id": structure_role_id,
        "category_id": 1151613279458828439,
        "dm_embed_path": strucure_dm_embed_path,
        "welcome_embed_path": strucure_welcome_embed_path,
        "short_name": "structure"
    }
}