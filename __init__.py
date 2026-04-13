from .nodes.save_image_click import SILVER_SaveIMGWithClick
from .nodes.clip_text_encode_with_cache import SILVER_ClipTextEncodeWithCache

NODE_CLASS_MAPPINGS = {
    "SILVER_SaveIMGWithClick": SILVER_SaveIMGWithClick,
    "SILVER_ClipTextEncodeWithCache": SILVER_ClipTextEncodeWithCache,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SILVER_SaveIMGWithClick": "[Silver] Save Image with Click",
    "SILVER_ClipTextEncodeWithCache": "[Silver] CLIP Text Encode (Prompt) With Cache",
}


WEB_DIRECTORY = "./web"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

