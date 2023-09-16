from huggingface_hub import HfFileSystem
from importlib import import_module
import json
from pathlib import Path
from PIL import Image
import requests
from rich.console import Console
from rich.table import Table
import torch
from torchvision import transforms
from typing import Any, Optional

# Hugging Face File System to find specific file.
hffs = HfFileSystem()


def load_model_and_labels(
        console: Console,
        supported_huggingface_architectures: list[tuple[str, str]],
        device: str,
        model_path: Optional[str] = None,
        repo_id: Optional[str] = None
    ) -> Optional[tuple[Any, str, list[str]]]:
    """
    Load model and labels
    """
    console.print(":brain: Loading ML model...")
    if model_path is not None:
        model = torch.load(model_path)
        # Load labels
        labels = load_labels(console)
        # Set model type
        model_type = 'pytorch'
    elif repo_id is not None:
        loaded_hf_model = load_model_from_huggingface(
            console=console,
            repo_id=repo_id,
            supported_architectures=supported_huggingface_architectures)
        if loaded_hf_model is None:
            return None

        model, arch = loaded_hf_model

        # Load labels
        labels = list(model.config.id2label.values())
        # Set model type
        model_type = 'huggingface'

    if model is not None and model_type is not None and labels is not None:
        console.print(":thumbsup: Loaded Model and labels successfully!")
        model.eval()
        try:
            model.to(device)
        except Exception as e:
            console.print(f"{e}", style="red")
            return None
    else:
        console.print(f":exclamation: Could not load model or labels.", style="red")
        return None

    return model, model_type, labels


def load_model_from_huggingface(
        console: Console,
        repo_id: str,
        supported_architectures: list[tuple]
    ) -> Optional[tuple[Any, str]]:
    """
    Load ML model from Hugging Face
    """
    console.print(":brain: Loading ML model from Hugging Face...")

    try:
        config = json.loads(hffs.read_text(f"{repo_id}/config.json"))
        if config.get('architectures'):
            archs = config['architectures']
        else:
            console.print(f":exclamation: The architectures not found on {repo_id}.", style="red")
            return None
        
        arch = archs[0]
        for sa in supported_architectures:
            model_arch, lib_name = sa
            if model_arch in arch:
                module = import_module("transformers")
                class_obj = getattr(module, lib_name)
                model = class_obj.from_pretrained(repo_id)
                return model, model_arch
        # Unsupported model type
        console.print(f":exclamation: The architecture is not supported yet: [bright_green]{arch}[/bright_green]", style="red")
    except FileNotFoundError as e:
        console.print(f":exclamation: {e}", style="red")
    except Exception as e:
        console.print(f":exclamation: Error occured loading model from Hugging Face: {e}", style="red")

    console.print(f":exclamation: [bright_green]'{repo_id}'[/bright_green] not found in Hugging Face!", style="red")

    return None


def load_original_image(console: Console, img: Optional[str] = None) -> Optional[Image.Image]:
    """
    Load original image from file path or original dog.jpg URL
    """
    console.print(f":framed_picture: Loading original image...")

    # TODO: user can specify the url to download
    if img is None:
        # Load original image by default url
        console.print(f":eyes: The original image for adversarial examples not set.")
        url = 'https://github.com/pytorch/hub/raw/master/images/dog.jpg'
        console.print(f":dog: Downloading original image from [bright_green]`{url}`[/bright_green]...")
        original_image = Image.open(requests.get(url, stream=True).raw)
    else:
        try:
            original_image = Image.open(img)
        except FileNotFoundError:
            console.print(f":exclamation: [red]Image file not found: `{img}`. Please specify correct path.[/red]")
            return None
        
    return original_image


def load_labels(console: Console):
    """
    Load labels from URL to be used for classification
    """
    console.print(f":eyes: Loading labels...")
    url = 'https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt'

    try:
        resp = requests.get(url)
        labels = resp.text.split("\n")
    except Exception as e:
        console.print(f":exclamation: {e}", style="red")

    return labels


def print_prob_ranking(
        console: Console,
        title: str,
        title_style: str = "bold bright_yellow",
        top_probs: Any = None,
        top_idxs: Any = None,
        labels: list[str] = [],
):
    """
    Display probabilities ranking
    """
    console.print()
    table = Table(title=title, title_style=title_style)
    table.add_column("Class", style="bright_green", justify="left")
    table.add_column("Probability", style="bright_cyan", justify="right")
    
    for i in range(len(top_probs)):
        table.add_row(labels[top_idxs[i]], f"{top_probs[i]*100:.2f}%")

    console.print(table)
    console.print()


def preprocess(console: Console, image: Image.Image, device: str):
    """
    Preprocess an image
    """
    console.print(f":eyes: Preprocessing original image...")

    # Adjust number of channels
    image = image.convert('RGB') if image.mode == 'RGBA' else image

    preprocess = create_preprocessor()
    original_image_tensor = preprocess(image)

    # Prepend one dimension to the tensor for inference
    original_image_batch = original_image_tensor.unsqueeze(0)
    original_image_batch = original_image_batch.to(device)

    return original_image_batch


def create_preprocessor():
    return transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])


def denormalize(batch, mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225], device: str = None):
    """
    Denormalize inputs
    """
    if device is None:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'

    if isinstance(mean, list):
        mean = torch.tensor(mean).to(device)
    if isinstance(std, list):
        std = torch.tensor(std).to(device)
    return batch * std.view(1, -1, 1, 1) + mean.view(1, -1, 1, 1)
