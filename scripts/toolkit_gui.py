import os
import sys
import gradio as gr
from modules import shared, script_callbacks
import torch
import glob
import gc
import cv2
from toolkit import *

data_folder = "/data/stable-diffusion-webui/extensions/stable-diffusion-webui-image-label/data"
label_folders=[]
# label_folder = "/data/stable-diffusion-webui/extensions/stable-diffusion-webui-image-label/data/img"
label_images = {}


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
    img_file = label_images.pop()
    img_file = None if img_file == "" else img_file
    return img_file


def do_load(prompt):
    # if len(label_images.items())==0:
    #     files = os.listdir(label_folder)
    img_file = label_images.pop()
    img_file = None if img_file == "" else img_file
    return img_file


def on_ui_tabs():
    global label_images
    global label_folders
    css = """
        .float-text { float: left; } .float-text-p { float: left; line-height: 2.5rem; } #mediumbutton { max-width: 32rem; } #smalldropdown { max-width: 2rem; } #smallbutton { max-width: 2rem; }
        #toolbutton { max-width: 8em; } #toolsettings > div > div { padding: 0; } #toolsettings { gap: 0.4em; } #toolsettings > div { border: none; background: none; gap: 0.5em; }
        #reportmd { padding: 1rem; } .dark #reportmd thead { color: #daddd8 } .gr-prose hr { margin-bottom: 0.5rem } #reportmd ul { margin-top: 0rem; margin-bottom: 0rem; } #reportmd li { margin-top: 0rem; margin-bottom: 0rem; }
        .dark .gr-compact { margin-left: unset } #image {height:30em;} #save_button {height:6.5em;} #load_button{height:3.7em;}
        #errormd { min-height: 0rem; text-align: center; } #errormd h3 { color: #ba0000; }
    """
    for root, dirs, files in os.walk(data_folder):
        if len(dirs)>0:
            label_folders=dirs
    # files = os.listdir(label_folder)
    # label_images = [os.path.join(label_folder, f) for f in files]

    with gr.Blocks(css=css, analytics_enabled=False, variant="compact") as image_label:
        gr.HTML(value=f"<style>{css}</style>")
        with gr.Row():
            with gr.Column(scale=4):
                with gr.Row():
                    comp_dropdown = gr.Dropdown(label="Dataset", choices=label_folders, interactive=True)
                    user_dropdown = gr.Dropdown(label="User Name", choices=['001', '002', '003', '004', '005', '006', '007', '008', '009', '010'], interactive=True)
            with gr.Column(scale=1):
                load_button = gr.Button(value="Load", variant="primary", elem_id="load_button")

        with gr.Row() as load_row:
            img = gr.Image(elem_id="image")
        with gr.Row():
            with gr.Column(scale=4):
                prompt = gr.Textbox(label="Prompt", elem_id="txt_prompt", show_label=False, lines=3, placeholder="Prompt (press Ctrl+Enter or Alt+Enter to save and jump to next)")
            with gr.Column(scale=1):
                save_button = gr.Button(value='Next', variant="primary", elem_id="save_button")
        save_button.click(fn=do_save, inputs=prompt, outputs=img)
        load_button.click(fn=do_load, inputs=None, outputs=img)

    return (image_label, "Label", "image_label"),


def on_ui_settings():
    section = ('image-label', "Image Label")
    shared.opts.add_option("model_toolkit_fix_clip", shared.OptionInfo(False, "Fix broken CLIP position IDs", section=section))


script_callbacks.on_ui_settings(on_ui_settings)
script_callbacks.on_ui_tabs(on_ui_tabs)
