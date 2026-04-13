import hashlib
from comfy.comfy_types import IO, ComfyNodeABC, InputTypeDict

import json
from aiohttp import web
from server import PromptServer


clipCache = {}
def make_clip_cache_key(clip, prompt):
    clip_id = id(clip)
    prompt_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    return f"{clip_id}:{prompt_hash}"


class SILVER_ClipTextEncodeWithCache(ComfyNodeABC):
    @classmethod
    def INPUT_TYPES(s) -> InputTypeDict:
        return {
            "required": {
                "clip": (IO.CLIP, {"tooltip": "The CLIP model used for encoding the text."}),
                "positive_prompt": (IO.STRING, {"multiline": True, "dynamicPrompts": True, "tooltip": "The text to be encoded."}),
                "cache_size": ("INT", {"default": 40, "min": 0, "max": 100, "tooltip": "The total amount of conditionals that can be stored in the cache. 0 = No cache"}),
                "clear_clip_cache": ("BOOLEAN", { "default": False, "tooltip": "If True - clears the clip cache on the next run." }),
            },
            "optional": {
                "negative_prompt": (IO.STRING, {"multiline": True, "dynamicPrompts": True, "tooltip": "(Optional) The text to be encoded."}),
            },
        }
    
    RETURN_TYPES = (IO.CONDITIONING, IO.CONDITIONING, "STRING", )
    RETURN_NAMES = ("positive_cond", "negative_cond", "cached_prompts" )
    OUTPUT_TOOLTIPS = ("A conditioning containing the embedded text used to guide the diffusion model.", "A conditioning containing the embedded text used to guide the diffusion model.",)
    FUNCTION = "encode"
    CATEGORY = "conditioning"
    DESCRIPTION = """
Same as the native 'CLIP Text Encode (Prompt)' node but with negative prompt widget and cache support.
Useful when shuffling between prompts often, ex: A -> B -> A -> D -> C -> B , ...
Conditionals whose prompt exists in cache will skip the encoding process of the Text Encoder entirely - making this node extremely fast in prompt shuffling scenarios.
"""

    def encode(self, clip, positive_prompt="", cache_size=40, clear_clip_cache=False, negative_prompt=""):
        global clipCache
        
        if clip is None:
            raise RuntimeError("ERROR: clip input is invalid: None\n\nIf the clip is from a checkpoint loader node your checkpoint does not contain a valid clip or text encoder model.")
        
        use_cache = cache_size > 0
        
        if not use_cache or clear_clip_cache:
            clipCache.clear()
        
        if use_cache and len(clipCache) > cache_size:
            while (len(clipCache) != cache_size):
                del clipCache[list(clipCache)[0]]
        
        positive_cond = None
        negative_cond = None
        
        if negative_prompt is not None:
            
            neg_key = make_clip_cache_key(clip, negative_prompt)
            
            if neg_key in clipCache:
                negative_cond = clipCache[neg_key][1]
            else:
                n_tokens = clip.tokenize(negative_prompt)
                negative_cond = clip.encode_from_tokens_scheduled(n_tokens)
                
                if len(clipCache) >= cache_size:
                    while (len(clipCache) >= cache_size):
                        del clipCache[list(clipCache)[0]]
                
                if use_cache:
                    clipCache[neg_key] = (negative_prompt, negative_cond)
        
        pos_key = make_clip_cache_key(clip, positive_prompt)
        if pos_key in clipCache:
            positive_cond = clipCache[pos_key][1]
        else:
            p_tokens = clip.tokenize(positive_prompt)
            positive_cond = clip.encode_from_tokens_scheduled(p_tokens)
            
            if len(clipCache) >= cache_size:
                while (len(clipCache) >= cache_size):
                    del clipCache[list(clipCache)[0]]
            
            if use_cache:
                clipCache[pos_key] = (positive_prompt, positive_cond)
            
        cached_prompts = [entry[0] for entry in clipCache.values()]
        
        return (positive_cond, negative_cond, cached_prompts, )



@PromptServer.instance.routes.post("/silver_clip_text_encode_with_cache/on_clicked")
async def on_click(request):
    global clipCache
    clipCache.clear()
    return web.json_response({})


