import os
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from PIL.PngImagePlugin import PngInfo
import folder_paths
import platform
import subprocess

class rk_save_image_v01:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "filename_prefix": ("STRING", {"default": "ComfyUI"}),

                "save_metadata": ("BOOLEAN", {"default": True}),
                "image_format": (["png","jpeg","webp"],),
                "open_explorer_after_saving": ("BOOLEAN", {"default": False}),

                # Watermark controls
                "enable_watermark": ("BOOLEAN", {"default": False}),
                "watermark_text": ("STRING", {"default": "Test"}),

                # Custom path toggles
                "enable_custom_path": ("BOOLEAN", {"default": False}),
                "custom_path": ("STRING", {"default": "E:/Image_output/CB"}),
            },
            "hidden": {
                "prompt": "PROMPT",
                "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "RK_tools_v02"

    def save_images(self,
                    images,
                    filename_prefix="ComfyUI",
                    save_metadata=True,
                    image_format="png",
                    open_explorer_after_saving=False,

                    enable_watermark=False,
                    watermark_text="Test",

                    enable_custom_path=False,
                    custom_path="E:/Image_output/CB",

                    prompt=None,
                    extra_pnginfo=None):
        """
        Always saves to ComfyUI's default output folder so previews work.
        If enable_custom_path is True, also saves a second copy to custom_path.
        Watermark is optional, appended as a black bar at the bottom using a larger font.
        Resolution info is displayed automatically by ComfyUI (width/height).
        """

        # --- 1) ComfyUI default output folder ---
        comfyui_output_dir = folder_paths.get_output_directory()
        os.makedirs(comfyui_output_dir, exist_ok=True)

        # --- 2) Optional custom folder (second copy) ---
        custom_dir = None
        if enable_custom_path and custom_path.strip():
            # Strip any accidental surrounding quotes or whitespace
            sanitized_path = custom_path.strip().strip('"').strip("'")
            custom_dir = sanitized_path
            # Attempt to create the folder
            os.makedirs(custom_dir, exist_ok=True)

        # Find highest existing number in ComfyUI's folder
        existing_files = [
            f for f in os.listdir(comfyui_output_dir)
            if f.startswith(filename_prefix) and f.lower().endswith(f'.{image_format.lower()}')
        ]
        highest_num = 0
        for file in existing_files:
            try:
                num = int(file.split('_')[-1].split('.')[0])
                highest_num = max(highest_num, num)
            except:
                pass

        counter = highest_num + 1
        results = []

        for image in images:
            # Convert tensor to PIL
            arr = 255.0 * image.cpu().numpy()
            img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

            # --- Watermark ---
            if enable_watermark:
                banner_height = 50
                new_img = Image.new('RGB', (img.width, img.height + banner_height), color='black')
                new_img.paste(img, (0, 0))

                # Larger font attempt:
                try:
                    # If you have 'arial.ttf' installed, you can specify its path/name here
                    font = ImageFont.truetype("arial.ttf", 28)
                except:
                    # Fallback to default font if TTF not found
                    font = ImageFont.load_default()

                draw = ImageDraw.Draw(new_img)
                # textbbox returns (left, top, right, bottom)
                bbox = draw.textbbox((0, 0), watermark_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

                x = (new_img.width - text_width) // 2
                y = img.height + (banner_height - text_height) // 2
                draw.text((x, y), watermark_text, fill="white", font=font)
                img = new_img

            # --- Metadata (PNG only) ---
            pnginfo = None
            if image_format.lower() == "png" and save_metadata:
                pnginfo = PngInfo()
                if prompt is not None:
                    pnginfo.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for k, v in extra_pnginfo.items():
                        pnginfo.add_text(k, json.dumps(v))

            # --- Save to ComfyUI folder (for preview) ---
            file_name = f"{filename_prefix}_{counter:05}.{image_format.lower()}"
            comfyui_full_path = os.path.join(comfyui_output_dir, file_name)

            if image_format.lower() == "png":
                img.save(comfyui_full_path, pnginfo=pnginfo, optimize=True)
            else:
                img.save(comfyui_full_path, optimize=True)

            # --- If custom path is enabled, save second copy ---
            if custom_dir:
                custom_full_path = os.path.join(custom_dir, file_name)
                if image_format.lower() == "png":
                    img.save(custom_full_path, pnginfo=pnginfo, optimize=True)
                else:
                    img.save(custom_full_path, optimize=True)

            # Gather resolution
            width, height = img.size

            # Add to results so ComfyUI displays them
            results.append({
                "filename": file_name,
                "subfolder": "",
                "type": "output",
                "width": width,
                "height": height
            })

            counter += 1

        # --- Optionally open explorer (ComfyUI folder) ---
        if open_explorer_after_saving:
            if platform.system() == "Windows":
                os.startfile(comfyui_output_dir)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", comfyui_output_dir])
            else:  # Linux / other
                subprocess.call(["xdg-open", comfyui_output_dir])

        # Return UI info only; no pipeline outputs
        return {
            "ui": {
                "images": results
            }
        }


# Register the node
NODE_CLASS_MAPPINGS = {
    "rk_save_image_v01": rk_save_image_v01
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "rk_save_image_v01": "RK Save Image v01"
}
