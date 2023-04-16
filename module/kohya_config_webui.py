# -*- coding: utf-8 -*-
"""kohya_config_webui.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/WSH032/kohya-config-webui/blob/main/kohya_config_webui.ipynb

| ![visitors](https://visitor-badge.glitch.me/badge?page_id=wsh.kohya_config_webui) | [![GitHub Repo stars](https://img.shields.io/github/stars/WSH032/kohya-config-webui?style=social)](https://github.com/WSH032/kohya-config-webui)</a> |

#A WebUI for making config files used by kohya_sd_script

Created by [WSH](https://space.bilibili.com/8417436)
"""


#@title 函数部分


import os
import toml
import warnings
import gradio as gr

common_parameter_dict_key_list=[]
sample_parameter_dict_key_list=[]
plus_parameter_dict_key_list=[]
all_parameter_dict_key_list=[]  #后面会有一次all_parameter_dict_key_list = common_parameter_dict_key_list + sample_parameter_dict_key_list + plus_parameter_dict_key_list
    

common_parameter_dict=({})
sample_parameter_dict=({})
plus_parameter_dict=({})

common_confirm_flag = False   #必须要确认常规参数一次才允许写入toml

parameter_len_dict={"common":0, "sample":0, "plus":0}

random_symbol = '\U0001f3b2\ufe0f'  # 🎲️
reuse_symbol = '\u267b\ufe0f'  # ♻️
paste_symbol = '\u2199\ufe0f'  # ↙
refresh_symbol = '\U0001f504'  # 🔄
save_style_symbol = '\U0001f4be'  # 💾
apply_style_symbol = '\U0001f4cb'  # 📋
clear_prompt_symbol = '\U0001f5d1\ufe0f'  # 🗑️
extra_networks_symbol = '\U0001F3B4'  # 🎴
switch_values_symbol = '\U000021C5' # ⇅
folder_symbol = '\U0001f4c2'  # 📂


def check_len_and_2dict(args, parameter_len_dict_value, parameter_dict_key_list, func_name=""):
    if len(args) != parameter_len_dict_value:
        warnings.warn(f"传入{func_name}的参数长度不匹配", UserWarning)
    if len(parameter_dict_key_list) != parameter_len_dict_value:
        warnings.warn(f" {func_name}内部字典赋值关键字列表的长度不匹配", UserWarning)
    parameter_dict = dict(zip(parameter_dict_key_list, args))
    return parameter_dict

def common_parameter_get(*args):
    global common_parameter_dict, common_confirm_flag
    common_confirm_flag = True    #必须要确认常规参数一次才允许写入toml
    common_parameter_dict = check_len_and_2dict(args, parameter_len_dict["common"], common_parameter_dict_key_list, func_name="common_parameter_get")
    common_parameter_toml = toml.dumps(common_parameter_dict)
    common_parameter_title = "基础参数配置确认"
    return common_parameter_toml,  common_parameter_title

def sample_parameter_get(*args):
    global sample_parameter_dict
    sample_parameter_dict = check_len_and_2dict(args, parameter_len_dict["sample"], sample_parameter_dict_key_list, func_name="sample_parameter_get")
    sample_parameter_toml = toml.dumps(sample_parameter_dict)
    sample_parameter_title = "采样配置确认"
    return sample_parameter_toml,  sample_parameter_title


def plus_parameter_get(*args):
    global plus_parameter_dict
    plus_parameter_dict = check_len_and_2dict(args, parameter_len_dict["plus"], plus_parameter_dict_key_list, func_name="plus_parameter_get")
    plus_parameter_toml = toml.dumps(plus_parameter_dict)
    plus_parameter_title = "进阶参数配置确认"
    return plus_parameter_toml,  plus_parameter_title


def all_parameter_get(*args):
    if len(args) != sum( parameter_len_dict.values() ):
         warnings.warn(f"传入all_parameter_get的参数长度不匹配", UserWarning)
    common_parameter_toml,  common_parameter_title = common_parameter_get( *args[ : parameter_len_dict["common"] ] )
    sample_parameter_toml,  sample_parameter_title = sample_parameter_get( *args[ parameter_len_dict["common"] : parameter_len_dict["common"] + parameter_len_dict["sample"] ] )
    plus_parameter_toml,  plus_parameter_title = plus_parameter_get( *args[ -parameter_len_dict["plus"] : ] )
    return common_parameter_toml, sample_parameter_toml, plus_parameter_toml,  "全部参数确认"

                      
def save_webui_config(save_webui_config_dir, save_webui_config_name, write_files_dir):
    os.makedirs(save_webui_config_dir, exist_ok=True)
    
    other = {"write_files_dir":write_files_dir}
    param = {**common_parameter_dict, **sample_parameter_dict, **plus_parameter_dict}
    dict = { "other":other, "param":param }

    save_webui_config_path = os.path.join(save_webui_config_dir, save_webui_config_name)
    with open(save_webui_config_path, "w", encoding="utf-8") as f:
        webui_config_str = toml.dumps( dict )
        f.write(webui_config_str)
    return f"保存webui配置成功，文件在{save_webui_config_path}"

def read_webui_config_get(read_webui_config_dir):
    try:
        files = [f for f in os.listdir(read_webui_config_dir) if f.endswith(".toml") ]
        if files:
            return gr.update( choices=files,value=files[0] )
        else:
            return gr.update( choices=[],value="没有找到webui配置文件" )
    except Exception as e:
        return gr.update( choices=[], value=f"错误的文件夹路径:{e}" )

def read_webui_config(read_webui_config_dir, read_webui_config_name, write_files_dir, *args):
    dir_change_flag = False
    param_len = sum( parameter_len_dict.values() )
    if len(args) != param_len:
        warnings.warn(f"传入read_webui_config的*args长度不匹配", UserWarning)
    
    read_webui_config_path = os.path.join(read_webui_config_dir, read_webui_config_name)
    #能打开就正常操作
    try:
        with open(read_webui_config_path, "r", encoding="utf-8") as f:
            config_dict = toml.loads( f.read() )
        
        #能读到["other"].["write_files_dir"]就改，读不到就用原写入地址
        try:
            if config_dict["other"]["write_files_dir"] != write_files_dir:
                write_files_dir = config_dict["other"]["write_files_dir"]
                dir_change_flag = True
        except KeyError:
            pass
        
        param_dict_key_list = list( config_dict.get("param",{}).keys() )
        #找出共有的key进行赋值，非共有的报错
        both_key = set(all_parameter_dict_key_list) & set(param_dict_key_list)
        parameter_unique_key = set(all_parameter_dict_key_list) - set(both_key)
        config_unique_key = set(param_dict_key_list) - set(both_key)
        #赋值
        count = 0
        if both_key:
            args = list(args)
            for key in both_key:
                index = all_parameter_dict_key_list.index(key)
                args[ index ] = config_dict["param"][key]
                count += 1
            args = tuple(args)
        read_done = f"\n读取完成,WebUI中共有{param_len}项参数,更新了其中{count}项\n" + f"写入文件夹发生改变:{write_files_dir}" if dir_change_flag else ""
        config_warning = f"\nwebui-config文件中以下参数可能已经失效或错误：\n{config_unique_key}\n" if config_unique_key else ""
        parameter_warning = f"\nWebUI中以下参数在webui-config文件中未找到，不发生修改：\n{parameter_unique_key}\n" if parameter_unique_key else ""
        str = read_done + config_warning + parameter_warning
        return  str, write_files_dir, *args

    #打不开就返回原值
    except FileNotFoundError:
        return "文件或目录不存在", write_files_dir, *args
    except PermissionError:
        return "没有权限访问文件或目录", write_files_dir, *args
    except OSError as e:
        return f"something wrong：{e}", write_files_dir, *args
    
    

def model_get(model_dir):
    try:
        files = [f for f in os.listdir(model_dir) if os.path.isfile(os.path.join(model_dir, f))]
        if files:
            return gr.update( choices=files,value=files[0] )
        else:
            return gr.update( choices=[],value="没有找到模型" )
    except Exception as e:
        return gr.update( choices=[], value=f"错误的文件夹路径:{e}" )


def write_files(write_files_dir):

    if not common_confirm_flag:
        return "必须要确认常规参数一次才允许写入toml"

    write_files_dir = write_files_dir if write_files_dir else os.getcwd()
    os.makedirs(write_files_dir, exist_ok=True)
    config_file_toml_path = os.path.join(write_files_dir, "config_file.toml")
    sample_prompts_txt_path = os.path.join(write_files_dir, "sample_prompts.txt")

    all = {**common_parameter_dict, **sample_parameter_dict, **plus_parameter_dict}

    def parameter2toml():

        #生成config_file.toml的字典

        #model_arguments部分
        model_arguments = { key: all.get(key) for key in ["v2", "v_parameterization"] }
        """ 生成底模路径 """
        base_model_path = os.path.join( all.get("base_model_dir"), all.get("base_model_name") )
        model_arguments.update( {"pretrained_model_name_or_path": base_model_path} )
        """ 生成vae路径 """
        if all.get("use_vae"):
            vae_model_path = os.path.join( all.get("vae_model_dir"), all.get("vae_model_name") )
            model_arguments.update( {"vae": vae_model_path} )

        #additional_network_arguments部分
        additional_network_arguments = { key: all.get(key) for key in ["unet_lr", "text_encoder_lr", "network_dim",\
                                            "network_alpha", "network_train_unet_only",\
                                            "network_train_text_encoder_only"] }
        """ 生成如network_module = "locon.locon_kohya" """
        #["LoRA-LierLa", "LoRA-C3Lier", "LoCon_Lycoris", "LoHa_Lycoris", "DyLoRa-LierLa", "DyLoRa-C3Lier"]
        #主要负责network_module的参数生成
        def network_module_param(train_method):
            conv_dim = all.get("conv_dim") if train_method != "DyLoRa-C3Lier" else all.get("network_dim")
            conv_alpha = all.get("conv_alpha")
            algo = "lora" if train_method == "LoCon_Lycoris" else "loha"
            unit = all.get("unit")
            if train_method in ["LoRA-LierLa", "LoRA-C3Lier"]:
                network_module = "networks.lora"
                if train_method == "LoRA-C3Lier":
                    network_module_args = [f"conv_dim={conv_dim}", f"conv_alpha={conv_alpha}"]
                else:
                    network_module_args = []
            elif train_method in ["LoCon_Lycoris", "LoHa_Lycoris"]:
                network_module = "lycoris.kohya"
                network_module_args = [f"conv_dim={conv_dim}", f"conv_alpha={conv_alpha}", f"algo={algo}"]
            elif train_method in ["DyLoRa-LierLa", "DyLoRa-C3Lier"]:
                network_module = "networks.dylora"
                if train_method == "DyLoRa-C3Lier":
                    network_module_args = [f"conv_dim={conv_dim}", f"conv_alpha={conv_alpha}", f"unit={unit}"]
                else:
                    network_module_args = [f"unit={unit}"]
            else: 
                warnings.warn(f"训练方法参数生成出错", UserWarning)
            return network_module, network_module_args
        network_module, network_module_args = network_module_param( all.get("train_method") )
        #更多network_args部分（主要为分层训练）
        network_lr_weight_args = [ f"{name}={all.get(name)}" for name in ["up_lr_weight", "mid_lr_weight", "down_lr_weight"] if all.get(name) ]

        def network_block_param(train_method):
            lst = ["block_dims", "block_alphas", "conv_block_dims", "conv_block_alphas"]
            if train_method == "LoRA-LierLa":
                return [ f"{name}={all.get(name)}" for name in lst[0:1] if all.get(name) ]
            if train_method in ["LoRA-C3Lier", "LoCon_Lycoris", "LoHa_Lycoris"]:
                return [ f"{name}={all.get(name)}" for name in lst if all.get(name) ]
            else:
                return []
        network_block_args = network_block_param( all.get("train_method") )
        

        network_args = []
        network_args.extend(network_module_args)
        network_args.extend(network_lr_weight_args)
        network_args.extend(network_block_args)

        additional_network_arguments.update( { "network_module":network_module } )
        additional_network_arguments.update( {"network_args":network_args} )          

        #optimizer_arguments部分
        optimizer_arguments = { key: all.get(key) for key in ["optimizer_type", "lr_scheduler", "lr_warmup_steps"] }
        """只有余弦重启调度器指定重启次数"""
        if all.get("lr_scheduler") == "cosine_with_restarts":
            optimizer_arguments.update( {"lr_restart_cycles":all.get("lr_restart_cycles")} )
        """学习率lr指定=unet_lr"""
        optimizer_arguments.update( {"learning_rate":all.get("unet_lr")} )
            #optimizer_args（待添加）

        #dataset_arguments部分
        dataset_arguments = { key: all.get(key) for key in ["cache_latents", "shuffle_caption", "enable_bucket"] }
        
        #training_arguments部分
        training_arguments = { key: all.get(key) for key in ["batch_size", "noise_offset", "keep_tokens",\
                                      "min_bucket_reso", "max_bucket_reso",\
                                      "caption_extension", "max_token_length", "seed",\
                                      "xformers", "lowram"]
        }
        """min_snr_gamma大于零才生效"""
        if all.get("min_snr_gamma") > 0:
            training_arguments.update( { "min_snr_gamma":all.get("min_snr_gamma") } )
        """ 最大训练时间 """
        training_arguments.update( { all.get("max_train_method"):all.get("max_train_value") } )
        """ 训练分辨率 """
        training_arguments.update( { "resolution":f"{all.get('width')},{all.get('height')}" } )
        """ 如果v2开启，则不指定clip_skip """
        if not all.get("v2"):
            training_arguments.update( { "clip_skip":all.get("clip_skip") } )
        """ 重训练模块 """
        if all.get("use_retrain") == "model":
            training_arguments.update( { "network_weights":all.get("retrain_dir") } )
        elif all.get("use_retrain") == "state":
            training_arguments.update( { "resume":all.get("retrain_dir") } )
        """  训练精度、保存精度 """
        training_arguments.update( { "mixed_precision":"fp16" } )
        training_arguments.update( { "save_precision":"fp16" } )
        


        #sample_prompt_arguments部分（采样间隔，采样文件地址待添加）
        sample_prompt_arguments = { key: all.get(key) for key in ["sample_sampler"] }
        if all.get("sample_every_n_type"):    #如果采样部分没确认过一次，会出现all.get("sample_every_n_type")=None:None的字典造成报错
            sample_prompt_arguments.update( {all.get("sample_every_n_type"):all.get("sample_every_n_type_value")} )

        #dreambooth_arguments部分
        dreambooth_arguments = { key: all.get(key) for key in ["train_data_dir", "reg_data_dir", "prior_loss_weight"] }

        #saving_arguments部分
        saving_arguments = { key: all.get(key) for key in ["output_dir",\
                                      "output_name", "save_every_n_epochs", "save_n_epoch_ratio",\
                                      "save_last_n_epochs", "save_state", "save_model_as" ]
        }
        """ 指定log输出目录与output相同 """
        saving_arguments.update( { "logging_dir":os.path.join( all.get("output_dir"), "logs" ) } )
        """ 指定log前缀和输出名字相同 """
        saving_arguments.update( { "log_prefix":all.get("output_name") } )
        

        toml_dict = {"model_arguments":model_arguments,
               "additional_network_arguments":additional_network_arguments,
               "optimizer_arguments":optimizer_arguments,
               "dataset_arguments":dataset_arguments,
               "training_arguments":training_arguments,
               "sample_prompt_arguments":sample_prompt_arguments,
               "dreambooth_arguments":dreambooth_arguments,
               "saving_arguments":saving_arguments,
        }
        toml_str = toml.dumps(toml_dict)
        return toml_str
    def sample_parameter2txt():
        #key_list = ["prompt", "negative", "sample_width", "sample_height", "sample_scale", "sample_steps", "sample_seed"]

        if not all.get('sample_seed'):    #如果采样部分没确认过，会出现all.get('sample_seed')=None > 0造成报错
            return ""
        sample_str = f"""{all.get("prompt")}  \
--n {all.get("negative")}  \
--w {all.get("sample_width")}  \
--h {all.get("sample_height")}  \
--l {all.get("sample_scale")}  \
--s {all.get("sample_steps")}  \
{f"--d {all.get('sample_seed')}" if all.get('sample_seed') > 0 else ""}"""
        return sample_str

    def write(content, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    write(parameter2toml(), config_file_toml_path)
    write(sample_parameter2txt(), sample_prompts_txt_path)
    write_files_title = f"写入成功, 训练配置文件在{config_file_toml_path}, 采样参数文件在{sample_prompts_txt_path}"
    return write_files_title

#@title WebUI部分


with gr.Blocks() as demo:
    with gr.Accordion("保存、读取\nwebui配置", open=False):
        save_read_webui_config_title = gr.Markdown("保存或读取")
        with gr.Row():
            save_webui_config_button = gr.Button("保存")
        with gr.Row():
            save_webui_config_dir = gr.Textbox(lines=1, label="保存目录", value=os.path.join(os.getcwd(),"kohya_config_webui_save") )
            save_webui_config_name = gr.Textbox(lines=1, label="保存名字（以toml为扩展名，否则不会被读取）", value="kohya_config_webui_save.toml" )
        with gr.Row():
            read_webui_config_get_button = gr.Button(refresh_symbol)
            read_webui_config_button = gr.Button("读取")
        with gr.Row():
            read_webui_config_dir = gr.Textbox(lines=1, label="读取目录", value=os.path.join(os.getcwd(),"kohya_config_webui_save") )  
            read_webui_config_name = gr.Dropdown(choices=[], label="读取文件", value="" )          
    with gr.Row():
        write_files_button = gr.Button("生成toml参数与采样配置文件")
        all_parameter_get_button = gr.Button("全部参数确认")
        write_files_dir = gr.Textbox( lines=1, label="写入文件夹", placeholder="一般填kohya_script目录，留空就默认根目录", value="" )
    write_files_title = gr.Markdown("生成适用于kohya/train_network.py的配置文件")
    with gr.Tabs():
        with gr.TabItem("基础参数"):
            common_parameter_get_button = gr.Button("确定")
            common_parameter_title = gr.Markdown("")
            with gr.Accordion("当前基础参数配置", open=False):
                common_parameter_toml = gr.Textbox(label="toml形式", placeholder="基础参数", value="")
            with gr.Row():
                train_data_dir = gr.Textbox(lines=1, label="train_data_dir", placeholder="训练集路径", value="")
            with gr.Accordion("使用正则化(可选)", open=False):
                with gr.Row():
                    reg_data_dir = gr.Textbox(lines=1, label="reg_data_dir", placeholder="正则化集路径（填入意味着启用正则化）", value="")
                    prior_loss_weight = gr.Slider(0, 1, step=0.01, value=0.3, label="正则化权重")
            with gr.Row():
                base_model_dir = gr.Textbox(label="底模文件夹地址", placeholder="文件夹路径", value="")
                base_model_name = gr.Dropdown(choices=[],label="底模",value="")
                base_model_get_button = gr.Button(refresh_symbol)
            with gr.Accordion("使用vae(可选)", open=False):
                with gr.Row():
                    use_vae = gr.Checkbox(label="是否使用vae",value=False)
                with gr.Row():
                    vae_model_dir = gr.Textbox(label="vae文件夹地址", placeholder="文件夹路径", value="")
                    vae_model_name = gr.Dropdown(choices=[],label="vae", value="")
                    vae_model_get_button = gr.Button(refresh_symbol)
            with gr.Row():
                width = gr.Slider(64, 1920, step=64, value=512, label="训练分辨率（宽）width")
                height = gr.Slider(64, 1920, step=64, value=512, label="训练分辨率（高）height")
                batch_size = gr.Slider(1, 24, step=1, value=1, label="batch大小")
            with gr.Row():
                noise_offset = gr.Slider(0, 1, step=0.01, value=0.05, label="noise_offset")
                keep_tokens = gr.Slider(0, 225, step=1, value=0, label="keep_tokens")
                min_snr_gamma = gr.Slider(0, 100, step=0.1, value=5, label="min_snr_gamma(设置为0则不生效)")
            """
            with gr.Row():
                gr.Markdown("repeat * 图片数 = 每个epoch的steps数")
            """
            with gr.Row():
                max_train_method = gr.Dropdown(["max_train_epochs","max_train_steps"], label="以epochs或steps来指定最大训练时间", value="max_train_epochs")
                max_train_value = gr.Number(label="最大训练epochs\steps数", value=10, precision=0)
            with gr.Accordion("输出设置", open=True):
                with gr.Row():
                    output_dir = gr.Textbox( label="模型、log日志输出地址（自行修改）", placeholder="文件夹路径",value=os.path.join(os.getcwd(),"output") )
                    output_name = gr.Textbox(label="输出模型名称（自行修改）", placeholder="名称",value="output_name")
                    save_model_as = gr.Dropdown(["safetensors","ckpt","pt"], label="保存模型格式", value="safetensors")
                with gr.Row():
                    save_every_n_epochs = gr.Slider(1, 499, step=1, value=1, label="每n个epoch保存一次")
                    save_n_epoch_ratio = gr.Slider(1, 499, step=1, value=0, label="等间隔保存n个(如不为0，会覆盖每n个epoch保存一次)")
                    save_last_n_epochs = gr.Slider(1, 499, step=1, value=499, label="最多保存n个（后面的出来就会把前面删了,优先级最高）")
                with gr.Row():   
                    save_state = gr.Checkbox(label="保存学习状态",value=False)
            with gr.Row():
                optimizer_type = gr.Dropdown(["AdamW8bit", "Lion", "DAdaptation", "AdamW", "SGDNesterov", "SGDNesterov8bit", "AdaFactor"],\
                                label="optimizer_type优化器类型", value="AdamW8bit")
                unet_lr = gr.Number(label="unet学习率", value=1e-4)
                text_encoder_lr = gr.Number(label="text_encoder学习率", value=1e-5)
            with gr.Row():
                lr_scheduler = gr.Dropdown(["cosine_with_restarts","cosine","polynomial","linear","constant_with_warmup","constant"],\
                               label="lr_scheduler学习率调度器", value="cosine_with_restarts")
                lr_warmup_steps = gr.Number(label="升温步数", value=0, precision=0)
                lr_restart_cycles = gr.Number(label="退火重启次数", value=1, precision=0)
            with gr.Row():
                train_method = gr.Dropdown(["LoRA-LierLa", "LoRA-C3Lier",\
                                "LoCon_Lycoris","LoHa_Lycoris",\
                                "DyLoRa-LierLa", "DyLoRa-C3Lier"],\
                                label="train_method训练方法", value="LoRA-LierLa")
                network_dim = gr.Number(label="线性dim", value=32, precision=0)
                network_alpha = gr.Number(label="线性alpha（可以为小数）", value=16)
            with gr.Accordion("额外网络参数(LoRA-C3Lier、LoCon、LoHa、DyLoRa-C3Lier都属于卷积,unit为DyLoRa专用)", open=True):
                with gr.Row():
                    with gr.Column():
                        conv_dim = gr.Number(label="卷积dim", info="使用DyLoRa-C3Lier时会被设置为等于基础dim", value=8, precision=0)
                    with gr.Column():
                        conv_alpha = gr.Number(label="卷积alpha", info="可以为小数", value=1)
                    with gr.Column():
                        unit = gr.Number(label="分割单位unit(整数)", info="使用DyLoRa时，请让dim为unit的倍数", value=1, precision=0)
            with gr.Row():          
                v2 = gr.Checkbox(label="v2")
                v_parameterization = gr.Checkbox(label="v_parameterization")
                lowram = gr.Checkbox(label="lowram")
                xformers = gr.Checkbox(label="xformers",value=True)
                cache_latents = gr.Checkbox(label="cache_latents",value=True)
                shuffle_caption = gr.Checkbox(label="shuffle_caption",value=True)
                enable_bucket = gr.Checkbox(label="enable_bucket",value=True)
        with gr.TabItem("采样参数"):
            sample_parameter_get_button = gr.Button("确定")
            sample_parameter_title = gr.Markdown("")
            with gr.Accordion("当前采样配置", open=False):
                sample_parameter_toml = gr.Textbox(label="toml形式", placeholder="采样配置", value="")
            with gr.Row():
                #enable_sample = gr.Checkbox(label="是否启用采样功能")
                sample_every_n_type = gr.Dropdown(["sample_every_n_epochs", "sample_every_n_steps"], label="sample_every_n_type", value="sample_every_n_epochs")
                sample_every_n_type_value = gr.Number(label="sample_every_n_type_value", value=1, precision=0)
            with gr.Row():
                sample_sampler = gr.Dropdown(["ddim", "pndm", "lms", "euler", "euler_a", "heun",\
                            "dpm_2", "dpm_2_a", "dpmsolver","dpmsolver++", "dpmsingle",\
                            "k_lms", "k_euler", "k_euler_a", "k_dpm_2", "k_dpm_2_a"],\
                            label="采样器", value="euler_a")
                sample_seed = gr.Number(label="采样种子(-1不是随机，大于0才生效)", value=-1, precision=0)
            with gr.Row():
                sample_width = gr.Slider(64, 1920, step=64, value=512, label="采样图片宽")
                sample_height = gr.Slider(64, 1920, step=64, value=768, label="采样图片高")
                sample_scale = gr.Slider(1, 30, step=0.5, value=7, label="提示词相关性")
                sample_steps = gr.Slider(1, 150, step=1, value=24, label="采样迭代步数")
            with gr.Row():
                prompt = gr.Textbox(lines=10, label="prompt", placeholder="正面提示词", value="(masterpiece, best quality, hires:1.2), 1girl, solo,")
                default_negative = ("(worst quality, bad quality:1.4), "
                          "lowres, bad anatomy, bad hands, text, error, "
                          "missing fingers, extra digit, fewer digits, "
                          "cropped, worst quality, low quality, normal quality, "
                          "jpeg artifacts,signature, watermark, username, blurry,")
                negative = gr.Textbox(lines=10, label="negative", placeholder="负面提示词", value=default_negative)
        with gr.TabItem("进阶参数"):
            plus_parameter_get_button = gr.Button("确定")
            plus_parameter_title = gr.Markdown("")
            with gr.Accordion("当前进阶参数配置", open=False):
                plus_parameter_toml = gr.Textbox(label="toml形式", placeholder="进阶参数", value="")
            with gr.Row():
                use_retrain = gr.Dropdown(["no","model","state"], label="是否使用重训练", value="no")
                retrain_dir = gr.Textbox(lines=1, label="重训练路径", placeholder="模型或者状态路径", value="")
            with gr.Row():
                min_bucket_reso = gr.Slider(64, 1920, step=64, value=256, label="最低桶分辨率")
                max_bucket_reso = gr.Slider(64, 1920, step=64, value=1024, label="最高桶分辨率")
                clip_skip = gr.Slider(0, 25, step=1, value=2, label="跳过层数")
                max_token_length = gr.Slider(75, 225, step=75, value=225, label="训练最大token数")
                caption_extension = gr.Textbox(lines=1, label="标签文件扩展名", placeholder="一般填.txt或.cap", value=".txt")
                seed = gr.Number(label="种子", value=1337, precision=0)
            with gr.Row():
                network_train_unet_only= gr.Checkbox(label="仅训练unet网络",value=False)
                network_train_text_encoder_only = gr.Checkbox(label="仅训练text_encoder网络",value=False)
            with gr.Accordion("分层学习模块", open=True):
                gr.Markdown("学习率分层，为不同层的结构指定不同学习率倍数； 如果某一层权重为0，那该层不会被创建")
                with gr.Row():
                    with gr.Column(scale=15):
                        up_lr_weight = gr.Textbox(lines=1, label="上层学习率权重", placeholder="留空则不启用",\
                                      info="15层，例如1.5,1.5,1.5,1.5,1.0,1.0,1.0,1.0,0.5,0.5,0.5,0.5", value="")
                    with gr.Column(scale=1):
                        mid_lr_weight = gr.Textbox(lines=1, label="中层学习率权重", placeholder="留空则不启用",\
                                      info="1层，例如2.0", value="")
                    with gr.Column(scale=15):
                        down_lr_weight = gr.Textbox(lines=1, label="下层学习率权重", placeholder="留空则不启用",\
                                      info="15层，例如0.5,0.5,0.5,0.5,1.0,1.0,1.0,1.0,1.5,1.5,1.5,1.5", value="")
                gr.Markdown("dim和alpha分层，为不同层的结构指定不同的dim和alpha（`DyLoRa`无法使用，卷积分层只有`LoRa-C3Lier、LoCon、LoHa`可以使用）")
                with gr.Row():
                        block_dims = gr.Textbox(lines=1, label="线性dim分层", placeholder="留空则不启用",\
                                      info="25层（上中下），例如2,4,4,4,8,8,8,8,12,12,12,12,16,12,12,12,12,8,8,8,8,4,4,4,2", value="")
                        block_alphas = gr.Textbox(lines=1, label="线性alpha分层", placeholder="留空则不启用",\
                                      info="25层（上中下），例如2,2,2,2,4,4,4,4,6,6,6,6,8,6,6,6,6,4,4,4,4,2,2,2,2", value="")
                with gr.Row():
                        conv_block_dims = gr.Textbox(lines=1, label="卷积dim分层", placeholder="留空则不启用",\
                                        info="25层（上中下），例如2,2,2,2,4,4,4,4,6,6,6,6,8,6,6,6,6,4,4,4,4,2,2,2,2", value="")
                        conv_block_alphas = gr.Textbox(lines=1, label="卷积alpha分层", placeholder="留空则不启用",\
                                        info="25层（上中下），例如2,2,2,2,4,4,4,4,6,6,6,6,8,6,6,6,6,4,4,4,4,2,2,2,2", value="")


    def dict_key_list_2_list(dict_key_list):
        list = []
        for key in dict_key_list:
            try:
                list.append(globals()[key])
            except KeyError:
                print(f"Error: parameter_dict_key_list中{key}不存在")
        list_len = len(list)
        return list, list_len

    common_parameter_dict_key_list = ["train_data_dir",
                      "reg_data_dir",
                      "prior_loss_weight",
                      "base_model_dir",
                      "base_model_name",
                      "use_vae",
                      "vae_model_dir",
                      "vae_model_name",
                      "width",
                      "height",
                      "batch_size",
                      "noise_offset",
                      "keep_tokens",
                      "min_snr_gamma",
                      "max_train_method",
                      "max_train_value",
                      "output_dir",
                      "output_name",
                      "save_model_as",
                      "save_every_n_epochs",
                      "save_n_epoch_ratio",
                      "save_last_n_epochs",
                      "save_state",
                      "optimizer_type",
                      "unet_lr",
                      "text_encoder_lr",
                      "lr_scheduler",
                      "lr_warmup_steps",
                      "lr_restart_cycles",
                      "train_method",
                      "network_dim",
                      "network_alpha",
                      "conv_dim",
                      "conv_alpha",
                      "unit",
                      "v2",
                      "v_parameterization",
                      "lowram",
                      "xformers",
                      "cache_latents",
                      "shuffle_caption",
                      "enable_bucket"]
    common_parameter_list, parameter_len_dict["common"] = dict_key_list_2_list(common_parameter_dict_key_list)
    sample_parameter_dict_key_list = ["sample_every_n_type",
                      "sample_every_n_type_value",
                      "sample_sampler",
                      "sample_seed",
                      "sample_width",
                      "sample_height",
                      "sample_scale",
                      "sample_steps",
                      "prompt",
                      "negative"]
    sample_parameter_list, parameter_len_dict["sample"] = dict_key_list_2_list(sample_parameter_dict_key_list)
    plus_parameter_dict_key_list = ["use_retrain",
                    "retrain_dir",
                    "min_bucket_reso",
                    "max_bucket_reso",
                    "clip_skip",
                    "max_token_length",
                    "caption_extension",
                    "seed",
                    "network_train_unet_only",
                    "network_train_text_encoder_only",
                    "up_lr_weight",
                    "mid_lr_weight",
                    "down_lr_weight",
                    "block_dims",
                    "block_alphas",
                    "conv_block_dims",
                    "conv_block_alphas"]
    plus_parameter_list, parameter_len_dict["plus"] = dict_key_list_2_list(plus_parameter_dict_key_list)

    #注意，这几个list相加的顺序不能错
    all_parameter_list = common_parameter_list + sample_parameter_list + plus_parameter_list
    all_parameter_dict_key_list = common_parameter_dict_key_list + sample_parameter_dict_key_list + plus_parameter_dict_key_list

    save_webui_config_button.click(fn=save_webui_config,
                    inputs=[save_webui_config_dir, save_webui_config_name, write_files_dir],
                    outputs=save_read_webui_config_title      
    )
    read_webui_config_get_button.click(fn=read_webui_config_get,
                      inputs=[read_webui_config_dir],
                      outputs=[read_webui_config_name]       
    )
    read_webui_config_button.click(fn=read_webui_config,
                    inputs=[read_webui_config_dir, read_webui_config_name, write_files_dir] + all_parameter_list,
                    outputs=[save_read_webui_config_title, write_files_dir] + all_parameter_list
    )
    common_parameter_get_button.click(fn=common_parameter_get,
                    inputs=common_parameter_list,
                    outputs=[common_parameter_toml,  common_parameter_title]
    )
    sample_parameter_get_button.click(fn=sample_parameter_get,
                    inputs=sample_parameter_list,
                    outputs=[sample_parameter_toml,  sample_parameter_title]
    )
    plus_parameter_get_button.click(fn=plus_parameter_get,
                    inputs=plus_parameter_list,
                    outputs=[plus_parameter_toml,  plus_parameter_title]
    )
    all_parameter_get_button.click(fn=all_parameter_get,
                    inputs=all_parameter_list,
                    outputs=[common_parameter_toml, sample_parameter_toml, plus_parameter_toml,  write_files_title]
    )
    base_model_get_button.click(fn=model_get,
                  inputs=[base_model_dir],
                  outputs=[base_model_name]
    )
    vae_model_get_button.click(fn=model_get,
                  inputs=[vae_model_dir],
                  outputs=[vae_model_name]
    )
    write_files_button.click(fn=write_files,
                inputs=[write_files_dir],
                outputs=[write_files_title]
    )


if __name__ == "__main__":
    demo.launch(share=False,inbrowser=False,inline=True,debug=True)