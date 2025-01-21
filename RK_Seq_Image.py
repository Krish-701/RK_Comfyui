# -*- coding: utf-8 -*-
import os
import glob
import random
import logging
from PIL import Image
import numpy as np
import torch

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File to store the current index
STATE_FILE = os.path.join(os.path.dirname(__file__), "rk_image_viewer_state.txt")

# ===========================================
# RK Image Viewer Node (Position Input + File-Based Persistent State)
# ===========================================
class RK_ImageViewer:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory": ("STRING", {
                    "default": "C:/Users/TS6000-1/Downloads/Art02/Art02/Art02",
                    "multiline": False
                }),
                "mode": (["increment", "decrement", "random", "disabled", "position"], {
                    "default": "increment"
                }),
                "show_text": (["enabled", "disabled"], {
                    "default": "enabled"
                }),
                "position": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 1000,
                    "step": 1,
                    "display": "number"
                }),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("IMAGE", "PROMPT_TEXT", "FILE_NAME", "IMAGE_COUNT")
    FUNCTION = "load_image_text"
    CATEGORY = "RK_tools_v02"
    OUTPUT_NODE = True

    def load_image_text(self, directory, mode, show_text, position):
        try:
            # Validate directory
            if not os.path.isdir(directory):
                error_msg = f"Directory not found: {directory}"
                logger.error(error_msg)
                return (torch.zeros(1, 64, 64, 3), error_msg, "", "0/0")

            # Get all supported image formats
            image_formats = ["*.png", "*.jpg", "*.jpeg", "*.webp"]
            image_files = []
            for fmt in image_formats:
                image_files.extend(glob.glob(os.path.join(directory, fmt)))
            
            # Sort files alphabetically
            image_files = sorted(image_files)
            
            if not image_files:
                return (torch.zeros(1, 64, 64, 3), "No images found", "", "0/0")

            # Load or initialize the current index
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, "r") as f:
                    current_index = int(f.read().strip())
            else:
                current_index = 0

            # Handle mode selection
            if mode == "increment":
                current_index = (current_index + 1) % len(image_files)
            elif mode == "decrement":
                current_index = (current_index - 1) % len(image_files)
            elif mode == "random":
                current_index = random.randint(0, len(image_files) - 1)
            elif mode == "position":
                # Use the provided position (1-based index)
                current_index = (position - 1) % len(image_files)
            elif mode == "disabled":
                pass  # Keep current index unchanged

            # Save the current index to the state file
            with open(STATE_FILE, "w") as f:
                f.write(str(current_index))

            # Get the current image path
            image_path = image_files[current_index]
            
            # Extract file name without extension
            file_name = os.path.splitext(os.path.basename(image_path))[0]
            logger.info(f"Loading image {current_index + 1}/{len(image_files)}: {file_name}")

            # Load image
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            image_array = np.array(image).astype(np.float32) / 255.0
            image_tensor = torch.from_numpy(image_array)[None,]

            # Load text file if enabled
            prompt_text = ""
            if show_text == "enabled":
                text_path = os.path.join(directory, f"{file_name}.txt")
                if os.path.exists(text_path):
                    with open(text_path, "r", encoding="utf-8", errors='replace') as f:
                        prompt_text = f.read().strip()
                else:
                    prompt_text = "No text file found"

            # Prepare image count string
            image_count = f"{current_index + 1}/{len(image_files)}"

            return (image_tensor, prompt_text, file_name, image_count)
            
        except Exception as e:
            logger.error(f"Error in RK_ImageViewer: {str(e)}")
            return (torch.zeros(1, 64, 64, 3), f"Error: {str(e)}", "", "0/0")

# ===========================================
# Node Registration
# ===========================================
NODE_CLASS_MAPPINGS = {
    "RK_ImageViewer": RK_ImageViewer
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RK_ImageViewer": "🖼️ RK Sequential Image Viewer"
}