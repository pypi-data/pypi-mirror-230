import random
import numpy as np
import torch
import shutil
import os
import pickle
import torch
from typing import List, Union
from .custom_ops import custom_scaled_dot_product_attention
from PIL import Image
import requests
from optimum.onnxruntime import ORTModel
import json
import logging
from easydict import EasyDict
from transformers import AutoConfig

logger = logging.getLogger(__name__)


def set_seed(seed: int):
    """
    Helper function for reproducible behavior to set the seed in `random`, `numpy`, `torch` and/or `tf` (if installed).

    Args:
        seed (`int`): The seed to set.
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def model_save(model_type: str, save_dir: str, ckpt_path: str, device: str = "gpu"):
    """
    Save model backbone with huggingface format if possible, and classifier to onnx.
    Exporting backbone to onnx has to be done outside the trainer class, due to the large memory usage.
    Refer to the export_onnx function in trainer_util.py

    Args:
        model_type (str): model type, e.g. 'TextClassifier', 'ImageClassifier', 'ImageTextClassifier'
        save_dir (str): Directory to save the model
        ckpt_path (str): trained model checkpoint path
        device (str): device name, e.g. 'cpu', 'gpu'
    """
    if model_type == "TextClassifier":
        from .text_classifier import TextClassifierModule

        classifier_module = TextClassifierModule
    elif model_type == "ImageClassifier":
        from .image_classifier import ImageClassifierModule

        classifier_module = ImageClassifierModule
    elif model_type == "ImageTextClassifier":
        from .image_text_classifier import ImageTextClassifierModule

        classifier_module = ImageTextClassifierModule
    else:
        raise ValueError(f"Not supported model type: {model_type}")

    if device == "gpu":
        device = torch.device("cuda")
    elif device == "cpu":
        device = torch.device("cpu")
    else:
        raise ValueError(
            f"Not supported device type: {device}, choose in ['cpu', 'gpu']."
        )

    if model_type == "ImageTextClassifier":
        os.makedirs(os.path.join(save_dir, "image"), exist_ok=True)
        os.makedirs(os.path.join(save_dir, "text"), exist_ok=True)
    else:
        os.makedirs(save_dir, exist_ok=True)

    # Load pretrained model
    logger.info(f"Loading the checkpoint from {ckpt_path}")
    print(f"Loading the checkpoint from {ckpt_path}")
    train_module = classifier_module.load_from_checkpoint(ckpt_path).to(device)
    # For torch pipeline
    shutil.copy(ckpt_path, os.path.join(save_dir, "model.ckpt"))

    if model_type == "ImageTextClassifier":
        ### Image backbone to onnx
        image_backbone_save_module = train_module.image_backbone
        # Only for huggingface transformers
        if not train_module.train_config.image_timm:
            # TransformerWrapper
            image_backbone_save_module = image_backbone_save_module.model
            # When model is trained with LORA, we have to merge the lora weight with backbone.
            if train_module.train_config.image_lora:
                image_backbone_save_module = (
                    image_backbone_save_module.merge_and_unload()
                )
            image_backbone_save_module.save_pretrained(os.path.join(save_dir, "image"))
        ### Text backbone to onnx
        text_backbone_save_module = train_module.text_backbone
        # When model is trained with LORA, we have to merge the lora weight with backbone.
        if train_module.train_config.text_lora:
            text_backbone_save_module = text_backbone_save_module.merge_and_unload()
        # ONly for huggingface transformers
        assert (
            train_module.train_config.text_timm == False
        ), "Not supported timm model for text backbone."
        text_backbone_save_module.save_pretrained(os.path.join(save_dir, "text"))
        # Save Tokenizer
        train_module.tokenizer.save_pretrained(os.path.join(save_dir, "text"))
        train_module.text_initial_config.save_pretrained(os.path.join(save_dir, "text"))

        with open(os.path.join(save_dir, "image", "config.json"), "w") as f:
            json.dump(train_module.image_initial_config, f)

        # Save validation transform with pickle
        with open(os.path.join(save_dir, "image", "val_transforms.pkl"), "wb") as f:
            pickle.dump(train_module.val_transforms, f)

    else:
        ### Backbone to onnx
        backbone_save_module = train_module.backbone
        # Only for huggingface transformers
        if not train_module.train_config.timm:
            # TransformerWrapper
            if model_type == "ImageClassifier":
                backbone_save_module = backbone_save_module.model
            # When model is trained with LORA, we have to merge the lora weight with backbone.
            if train_module.train_config.lora:
                backbone_save_module = backbone_save_module.merge_and_unload()
            backbone_save_module.save_pretrained(save_dir)

        if model_type == "TextClassifier":
            # Save Tokenizer
            train_module.tokenizer.save_pretrained(save_dir)
            train_module.initial_config.save_pretrained(save_dir)
        # ImageClassifier
        else:
            with open(os.path.join(save_dir, "config.json"), "w") as f:
                json.dump(train_module.initial_config, f)
            # Save validation transform with pickle
            with open(os.path.join(save_dir, "val_transforms.pkl"), "wb") as f:
                pickle.dump(train_module.val_transforms, f)

    # Save train config
    with open(os.path.join(save_dir, "train_config.json"), "w") as f:
        json.dump(train_module.train_config.to_dict(), f)

    ### Classifier save to onnx
    classifier_head_save_module = train_module.classifier_head
    dummy_input = torch.randn(
        [1, train_module.embedding_size], device=device
    )  # .to(device)
    torch.onnx.export(
        classifier_head_save_module,
        dummy_input,
        os.path.join(save_dir, "classifier_head.onnx"),
        input_names=["embeddings"],
        output_names=["logits"],
        dynamic_axes={"embeddings": {0: "batch_size"}, "logits": {0: "batch_size"}},
    )


def export_onnx(model_type: str, save_dir: str, device: str = "gpu"):
    """
    Export Huggingface backbone model to onnx format.
    Args:
        model_type (`str`): Model type string, e.g. "TextClassifier", "ImageClassifier", "ImageTextClassifier"
        save_dir (`str`): Saved model directory, containing pytorch_model.bin or model.ckpt
        device (`str`): Device type for exporting onnx, no related with pipeline device  "cpu" or "gpu"
    """
    if device == "gpu":
        device = torch.device("cuda")
    elif device == "cpu":
        device = torch.device("cpu")
    else:
        raise ValueError(
            f"Not supported device type: {device}, choose in ['cpu', 'gpu']."
        )

    with open(os.path.join(save_dir, "train_config.json"), "r") as f:
        train_config = EasyDict(json.load(f))

    if model_type == "TextClassifier":
        assert train_config.timm == False, "timm is not supported for TextClassifier"
        logger.info("Exporting torch pt model to onnx...")
        model = ORTModel.from_pretrained(save_dir, export=True)
        # Saved with model.onnx
        logger.info("Saving onnx file...")
        model.save_pretrained(save_dir)
    elif model_type == "ImageClassifier":
        from .image_classifier import ImageClassifierModule

        if train_config.timm:
            train_module = ImageClassifierModule.load_from_checkpoint(
                os.path.join(save_dir, "model.ckpt"), map_location=device
            )

            backbone_save_module = train_module.backbone
            from transformers import CLIPModel

            if isinstance(train_module.backbone, CLIPModel):
                backbone_save_module = backbone_save_module.vision_model

            if train_module.train_config.lora:
                backbone_save_module = backbone_save_module.merge_and_unload()

            torch.onnx.register_custom_op_symbolic(
                symbolic_name="aten::scaled_dot_product_attention",
                symbolic_fn=custom_scaled_dot_product_attention,
                opset_version=17,
            )

            # Custom operation registered, we can produce our onnx model

            dummy_input = torch.randn(
                train_module.initial_config["input_size"], device=device
            ).unsqueeze(0)
            torch.onnx.export(
                backbone_save_module,
                dummy_input,
                os.path.join(save_dir, "model.onnx"),
                custom_opsets={"onnx-script": 17},
                opset_version=17,
                input_names=["inputs"],
                output_names=["embeddings"],
                dynamic_axes={
                    "inputs": {0: "batch_size"},
                    "embeddings": {0: "batch_size"},
                },
            )
        # Case for using huggingface transformers
        else:
            logger.info("Exporting torch pt model to onnx...")
            model = ORTModel.from_pretrained(save_dir, export=True)
            # Saved with model.onnx
            logger.info("Saving onnx file...")
            model.save_pretrained(save_dir)

    elif model_type == "ImageTextClassifier":
        from .image_text_classifier import ImageTextClassifierModule

        assert (
            train_config.text_timm == False
        ), "timm is not supported for TextClassifier"
        logger.info("Exporting torch pt text model to onnx...")
        text_model = ORTModel.from_pretrained(
            os.path.join(save_dir, "text"), export=True
        )
        # Saved with model.onnx
        logger.info("Saving onnx file...")
        text_model.save_pretrained(os.path.join(save_dir, "text"))

        logger.info("Exporting torch pt image model to onnx...")
        # huggingface transformers
        if not train_config.image_timm:
            image_model = ORTModel.from_pretrained(
                os.path.join(save_dir, "image"), export=True
            )
            # Saved with model.onnx
            logger.info("Saving onnx file...")
            image_model.save_pretrained(os.path.join(save_dir, "image"))
        # timm
        else:
            train_module = ImageTextClassifierModule.load_from_checkpoint(
                os.path.join(save_dir, "model.ckpt"), map_location=device
            )
            from transformers import CLIPModel

            if isinstance(train_module.image_backbone, CLIPModel):
                image_backbone_save_module = (
                    train_module.image_backbone.model.vision_model
                )
            else:
                image_backbone_save_module = train_module.image_backbone

            # image_backbone_save_module = train_module.image_backbone.model
            if train_module.train_config.image_lora:
                image_backbone_save_module = (
                    image_backbone_save_module.merge_and_unload()
                )

            torch.onnx.register_custom_op_symbolic(
                symbolic_name="aten::scaled_dot_product_attention",
                symbolic_fn=custom_scaled_dot_product_attention,
                opset_version=17,
            )
            # Custom operation registered, we can produce our onnx model

            dummy_image_input = torch.randn(
                train_module.image_initial_config["input_size"], device=device
            ).unsqueeze(0)
            torch.onnx.export(
                image_backbone_save_module,
                dummy_image_input,
                os.path.join(save_dir, "image/model.onnx"),
                custom_opsets={"onnx-script": 17},
                opset_version=17,
                input_names=["inputs"],
                output_names=["embeddings"],
                dynamic_axes={
                    "inputs": {0: "batch_size"},
                    "embeddings": {0: "batch_size"},
                },
            )

    else:
        raise ValueError(f"Model type {model_type} not supported.")


def export_onnx_optimization(save_dir: str, optimization_level: int = 2):
    """
    export optimized onnx model using onnxruntime

    Args:
        save_dir (str): directory to save the optimized onnx model
        optimization_level (int, optional): optimization level. Defaults to 2. Can be 1, 2, 3, 4
    """
    from optimum.onnxruntime import ORTOptimizer, AutoOptimizationConfig

    optimization_config_dict = {
        1: AutoOptimizationConfig.O1(),
        2: AutoOptimizationConfig.O2(),
        3: AutoOptimizationConfig.O3(),
        4: AutoOptimizationConfig.O4(),
    }

    if optimization_level not in optimization_config_dict.keys():
        raise ValueError(f"Not supported optimization level {optimization_level}")
    optimization_config = optimization_config_dict[optimization_level]
    # Need to export onnx model first using export_onnx
    optimizer = ORTOptimizer.from_pretrained(save_dir, file_names="model.onnx")
    # saved with model_optimized.onnx
    optimizer.optimize(save_dir=save_dir, optimization_config=optimization_config)


def export_onnx_quantization(save_dir: str, cpu_architecture: str = "avx512"):
    """
    export quantized onnx model using onnxruntime

    Args:
        save_dir (str): directory to save the quantized onnx model
        cpu_architecture (str, optional): cpu architecture. Defaults to "avx512". Can be "arm64", "avx2", "avx512", "avx512_vnni", "tensorrt"
    """
    from optimum.onnxruntime import ORTQuantizer
    from optimum.onnxruntime.configuration import AutoQuantizationConfig

    supported_architectures = ["arm64", "avx2", "avx512", "avx512_vnni", "tensorrt"]
    if cpu_architecture not in supported_architectures:
        raise ValueError(
            f"Not supported quantization cpu architecture {cpu_architecture}"
        )
    # Need to export onnx model first using export_onnx
    quantizer = ORTQuantizer.from_pretrained(save_dir, file_name="model.onnx")
    # Use dynamic quantization, not using calibration dataset.
    dqconfig = getattr(AutoQuantizationConfig, cpu_architecture)(
        is_static=False, per_channel=False
    )
    # saved with model_quantized.onnx
    model_quantized_path = quantizer.quantize(
        save_dir=save_dir, quantization_config=dqconfig
    )


def ImageClassifierInputPreprocess(
    input_img_paths: List[str], device: torch.device, transforms
):
    """
    Preprocess input images for image classifier.

    Args:
        input_img_paths (List[str]): list of image paths
        device (torch.device): device to use
        transforms (torchvision.transforms): torchvision transforms
    """
    inputs = []
    # PIL open image then preprocess with augmentation.
    for img_path in input_img_paths:
        if img_path.startswith("https:"):
            input_img = Image.open(requests.get(img_path, stream=True).raw).convert(
                "RGB"
            )
        else:
            input_img = Image.open(img_path).convert("RGB")
        input_tensor = transforms(input_img).to(device)
        inputs.append(input_tensor)

    return torch.stack(inputs)


def TextClassifierInputPreprocess(
    input_texts: List[str], text_prompt: str, device: torch.device, tokenizer
):
    """
    Preprocess input texts for text classifier, including prompt and tokenizer.

    Args:
        input_texts (List[str]): list of input texts
        text_prompt (str): text prompt
        device (torch.device): device to use
        tokenizer (transformers.tokenizer): tokenizer
    """
    # Prompting and apply tokenizer.
    prompted_input_texts = list(map(lambda x: text_prompt.format(x), input_texts))

    inputs = tokenizer(prompted_input_texts, padding=True, return_tensors="pt").to(
        device
    )

    return inputs


def TextClassifierSelectToken(
    backbone_outputs: torch.Tensor, inputs: dict, configs: AutoConfig
):
    """
    Selecting the proper token for text classifier.
    Can be different for each model_type, so we need to handle it separately.
    Currently only implemented for gpt_neox.

    Args:
        backbone_outputs (torch.tensor): backbone outputs
        inputs (dict): model inputs
        configs (AutoConfig): model configs
    """
    # For classificaiton, model use the last token as other causal models (e.g. GPT-1) do. We utilize attention mask to know the position of the last token.
    if configs.model_type == "gpt_neox":
        last_hidden_state = backbone_outputs[0]
        if type(last_hidden_state) == np.ndarray:
            selected_tokens = last_hidden_state[
                np.arange(last_hidden_state.shape[0]),
                inputs["attention_mask"].sum(axis=-1) - 1,
            ]
            selected_tokens = torch.from_numpy(selected_tokens)
        else:
            selected_tokens = last_hidden_state[
                torch.arange(last_hidden_state.shape[0]),
                inputs["attention_mask"].sum(axis=-1) - 1,
            ]

        return selected_tokens

    else:
        raise NotImplementedError(
            f"{configs.model_type} selecting token method is not implemented."
        )
