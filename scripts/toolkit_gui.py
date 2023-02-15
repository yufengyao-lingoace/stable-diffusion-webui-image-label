import os
import sys
import gradio as gr
from modules import shared, script_callbacks
import torch
import glob
import gc
import cv2
from toolkit import *

label_folder="/data/stable-diffusion-webui/extensions/stable-diffusion-webui-image-label/data/img"
label_images=[]


def do_clear():
    global loaded
    loaded = None
    gc.collect()
    
    reports = [gr.update(value=""), gr.update(value="")]
    sources = [gr.update(), gr.update()]
    drops = [gr.update(choices=[], value="") for _ in range(3)]
    rows = [gr.update(visible=True), gr.update(visible=False)]
    names = [gr.update(value=""), gr.update()]
    error = [gr.update(value=""), gr.update(visible=False)]

    updates = reports + sources + drops + rows + names + error
    return updates

def do_save(prompt):
    return f"/data/stable-diffusion-webui/extensions/stable-diffusion-webui-image-label/data/img/f677826d-6d9d-4fe9-975e-840251946410.jpg"

def on_ui_tabs():
    css = """
        .float-text { float: left; } .float-text-p { float: left; line-height: 2.5rem; } #mediumbutton { max-width: 32rem; } #smalldropdown { max-width: 2rem; } #smallbutton { max-width: 2rem; }
        #toolbutton { max-width: 8em; } #toolsettings > div > div { padding: 0; } #toolsettings { gap: 0.4em; } #toolsettings > div { border: none; background: none; gap: 0.5em; }
        #reportmd { padding: 1rem; } .dark #reportmd thead { color: #daddd8 } .gr-prose hr { margin-bottom: 0.5rem } #reportmd ul { margin-top: 0rem; margin-bottom: 0rem; } #reportmd li { margin-top: 0rem; margin-bottom: 0rem; }
        .dark .gr-compact { margin-left: unset } #image {height:30em;} #save_button {height:6.5em;}
        #errormd { min-height: 0rem; text-align: center; } #errormd h3 { color: #ba0000; }
    """

    files=os.listdir(label_folder)
    files=[os.path.join(label_folder,f) for f in files]
    file_value=files[0]
    with gr.Blocks(css=css, analytics_enabled=False, variant="compact") as image_label:
        gr.HTML(value=f"<style>{css}</style>")
        with gr.Row():
            comp_dropdown = gr.Dropdown(label="Dataset", choices=['tigo','img'], interactive=True)
            user_dropdown = gr.Dropdown(label="User Name", choices=['001','002','003','004','005','006','007','008','009','010'], interactive=True)
            # txt_user=gr.Textbox(placeholder="What is your name?")
            load_button = gr.Button(value="Load", variant="primary",elem_id="load_button")
        with gr.Row() as load_row:
            img = gr.Image(value=file_value,elem_id="image")
        with gr.Row():
            with gr.Column(scale=4):
                prompt = gr.Textbox(label="Prompt", elem_id="txt_prompt", show_label=False, lines=3, placeholder="Prompt (press Ctrl+Enter or Alt+Enter to generate)")
            with gr.Column(scale=1):
                save_button = gr.Button(value='Save', variant="primary",elem_id="save_button")
                save_button.click(fn=do_save, inputs=prompt, outputs=img)

    return (image_label, "Label", "image_label"),

def on_ui_settings():
    section = ('image-label', "Image Label")
    shared.opts.add_option("model_toolkit_fix_clip", shared.OptionInfo(False, "Fix broken CLIP position IDs", section=section))

script_callbacks.on_ui_settings(on_ui_settings)
script_callbacks.on_ui_tabs(on_ui_tabs)