import os
import sys
import json
import gradio as gr
from modules import shared, script_callbacks
import torch
import glob
import gc
import cv2
from toolkit import *

data_folder = "/data/stable-diffusion-webui/extensions/stable-diffusion-webui-image-label/data" #/data文件夹
data_sets={} # 数据集实体{tigo:[],img:[]}
label_set={} #{tigo:{1.jpg:tigo on the hill}}
label_folders=[] #数据集名称 [tigo,img]
label_changed=False #标注内容是否变化

def save_label():
    pass

def do_save(file_name,prompt,dataset_name,user_name):
    #保存
    # print(label_set[dataset_name])
    label_set[dataset_name].append("{0}:{1}".format(file_name,prompt))
    label_changed=True
    with open("/data/stable-diffusion-webui/extensions/stable-diffusion-webui-image-label/data/finished.txt",'a') as writer:
        writer.write(file_name+'\r\n')
    with open("/data/stable-diffusion-webui/extensions/stable-diffusion-webui-image-label/data/label.json",'r+') as reader:
        result=json.load(reader)
        result[file_name]=prompt
        json.dump(result,reader)

    #取下一张
    img_file = data_sets[dataset_name].pop()
    return img_file,os.path.basename(img_file) 

def do_load(dataset_name):
    if not dataset_name in data_sets.keys():
        img_folder=os.path.join(data_folder,dataset_name)
        files = os.listdir(img_folder) #枚举单个数据集中的所有图片
        label_images = [os.path.join(img_folder, f) for f in files]
        data_sets[dataset_name]=label_images
    img_file = data_sets[dataset_name].pop()

    return img_file,os.path.basename(img_file) 


def on_ui_tabs():
    global label_folders
    css = """
        .float-text { float: left; } .float-text-p { float: left; line-height: 2.5rem; } #mediumbutton { max-width: 32rem; } #smalldropdown { max-width: 2rem; } #smallbutton { max-width: 2rem; }
        #toolbutton { max-width: 8em; } #toolsettings > div > div { padding: 0; } #toolsettings { gap: 0.4em; } #toolsettings > div { border: none; background: none; gap: 0.5em; }
        #reportmd { padding: 1rem; } .dark #reportmd thead { color: #daddd8 } .gr-prose hr { margin-bottom: 0.5rem } #reportmd ul { margin-top: 0rem; margin-bottom: 0rem; } #reportmd li { margin-top: 0rem; margin-bottom: 0rem; }
        .dark .gr-compact { margin-left: unset } #image {height:30em;} #next_button,#previous_button,#pass_button {height:6.5em;} #load_button{height:3.7em;}
        #errormd { min-height: 0rem; text-align: center; } #errormd h3 { color: #ba0000; }
    """
    for root, dirs, files in os.walk(data_folder):
        if len(dirs)>0:
            label_folders=dirs
            for dir in dirs:
                label_set[dir]=[] #{tigo:[],img:[]}  标记集初始化

    with gr.Blocks(css=css, analytics_enabled=False, variant="compact") as image_label:
        gr.HTML(value=f"<style>{css}</style>")
        with gr.Row():
            with gr.Column(scale=4):
                with gr.Row():
                    dataset_dropdown = gr.Dropdown(label="Dataset", choices=label_folders, interactive=True)
                    user_dropdown = gr.Dropdown(label="User Name", choices=['001', '002', '003', '004', '005', '006', '007', '008', '009', '010'], interactive=True)
            with gr.Column(scale=1):
                load_button = gr.Button(value="Load", variant="primary", elem_id="load_button")
        with gr.Row():
            label=gr.Label(visible=False)
        with gr.Row() as load_row:
            image = gr.Image(elem_id="image")
        with gr.Row():
            with gr.Column(scale=7,min_width=750):
                prompt = gr.Textbox(label="Prompt", elem_id="txt_prompt", show_label=False, lines=3, placeholder="Prompt (press Enter to save and jump to next)")
            with gr.Column(scale=1,min_width=60):
                next_button = gr.Button(value='Save', variant="primary", elem_id="next_button")
            with gr.Column(scale=1,min_width=60):
                previous_button = gr.Button(value='Previous', variant="primary", elem_id="previous_button")
            with gr.Column(scale=1,min_width=60):
                pass_button = gr.Button(value='Pass', variant="primary", elem_id="pass_button")
        next_button.click(fn=do_save, inputs=[label,prompt,dataset_dropdown,user_dropdown], outputs=[image,label])
        load_button.click(fn=do_load, inputs=dataset_dropdown, outputs=[image,label])
        # comp_dropdown.change(fn=do_select,inputs=None,outputs=None)

    return (image_label, "Label", "image_label"),


def on_ui_settings():
    section = ('image-label', "Image Label")
    shared.opts.add_option("model_toolkit_fix_clip", shared.OptionInfo(False, "Fix broken CLIP position IDs", section=section))


script_callbacks.on_ui_settings(on_ui_settings)
script_callbacks.on_ui_tabs(on_ui_tabs)
