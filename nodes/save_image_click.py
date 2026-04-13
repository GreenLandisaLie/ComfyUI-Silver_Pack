import os
import math
import random
from typing import List, Tuple, Dict

import folder_paths

import json
from aiohttp import web
from server import PromptServer

import torch
import numpy as np

from PIL import Image, ImageOps, ImageSequence
from PIL.PngImagePlugin import PngInfo



nodeIDs_data = {} # Data: [images, isSaved, filename_prefix, prompt, extra_pnginfo, saveMetatada]
output_dir = folder_paths.get_output_directory()
temp_dir = folder_paths.get_temp_directory()


def save_images(images, filename_prefix="ComfyUI", prompt=None, extra_pnginfo=None, saveMetadata=True, prefix_append="", out_dir=output_dir, compress_level=4, type="output"): # copied from native SaveImage node
    filename_prefix += prefix_append
    full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(filename_prefix, out_dir, images[0].shape[1], images[0].shape[0])
    results = list()
    for (batch_number, image) in enumerate(images):
        i = 255. * image.cpu().numpy()
        img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
        metadata = None
        if saveMetadata:
            metadata = PngInfo()
            if prompt is not None:
                metadata.add_text("prompt", json.dumps(prompt))
            if extra_pnginfo is not None:
                for x in extra_pnginfo:
                    metadata.add_text(x, json.dumps(extra_pnginfo[x]))
    
        filename_with_batch_num = filename.replace("%batch_num%", str(batch_number))
        file = f"{filename_with_batch_num}_{counter:05}_.png"
        img.save(os.path.join(full_output_folder, file), pnginfo=metadata, compress_level=compress_level)
        results.append({
            "filename": file,
            "subfolder": subfolder,
            "type": type
        })
        counter += 1
    return results


class SILVER_SaveIMGWithClick:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The images to save."}),
                "filename_prefix": ("STRING", {"default": "ComfyUI", "tooltip": "The prefix for the file to save. This may include formatting information such as %date:yyyy-MM-dd% or %Empty Latent Image.width% to include values from nodes."}),
                "save_metadata": ("BOOLEAN", {"default": True}),
            },
            "hidden": {
                "prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO",
                "unique_id": "UNIQUE_ID",
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "store_data"
    
    OUTPUT_NODE = True
    
    CATEGORY = "image"
    ESSENTIALS_CATEGORY = "Basics"
    DESCRIPTION = "Same functionality as the native SaveImage node but this one only saves when the user clicks the save button."
    SEARCH_ALIASES = ["save", "save image", "export image", "output image", "write image", "download"]
    
    def store_data(self, images, filename_prefix="ComfyUI", save_metadata=True, prompt=None, extra_pnginfo=None, unique_id=None):
        global nodeIDs_data
        if str(unique_id) in nodeIDs_data:
            del nodeIDs_data[str(unique_id)] # just in case to avoid memory leak
        nodeIDs_data[str(unique_id)] = [images, False, filename_prefix, prompt, extra_pnginfo, save_metadata]
        results = save_images(images, filename_prefix, prompt, extra_pnginfo, save_metadata, "_temp_" + ''.join(random.choice("abcdefghijklmnopqrstupvxyz") for x in range(5)), temp_dir, 1, "temp")
        return { "ui": { "images": results, "silver_status": "new" } }



@PromptServer.instance.routes.post("/silver_save_img_with_click/update_prefix")
async def update_prefix(request):
    global nodeIDs_data
    jsdata = await request.json()
    id = jsdata.get("id", "")
    filename_prefix = jsdata.get("filename_prefix", "ComfyUI")
    if id not in nodeIDs_data:
        nodeIDs_data[id] = [None, False, filename_prefix, None, None, True]
    else:
        nodeIDs_data[id][1] = False
        nodeIDs_data[id][2] = filename_prefix
    return web.json_response({})

@PromptServer.instance.routes.post("/silver_save_img_with_click/update_save_metadata")
async def update_save_metadata(request):
    global nodeIDs_data
    jsdata = await request.json()
    id = jsdata.get("id", "")
    save_metadata = False if str(jsdata.get("save_metadata", None)).lower() == "false" else True
    if id not in nodeIDs_data:
        nodeIDs_data[id] = [None, False, "ComfyUI", None, None, save_metadata]
    else:
        nodeIDs_data[id][1] = False
        nodeIDs_data[id][5] = save_metadata
    return web.json_response({})

@PromptServer.instance.routes.post("/silver_save_img_with_click/on_clicked")
async def on_clicked(request):
    global nodeIDs_data
    jsdata = await request.json()
    id = jsdata.get("id", "")
    if id and id in nodeIDs_data:
        data = nodeIDs_data[id] # Data: [images, isSaved, filename_prefix, prompt, extra_pnginfo, saveMetatada]
        if data and data[0] is not None:
            if data[1]: 
                return web.json_response({ "status": "already_saved" })
            else:
                save_images(images=data[0], filename_prefix=data[2], prompt=data[3], extra_pnginfo=data[4], saveMetadata=data[5])
                nodeIDs_data[id][1] = True
                return web.json_response({ "status": "success" })
        else:
            pass
    else:
        print(f"[SILVER_SaveIMGWithClick] WARNING: Could not find node with id:{id}. Image was not saved!")
    return web.json_response({ "status": "failed" })




