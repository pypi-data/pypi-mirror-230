from pathlib import Path
from rich.console import Console
import torch
import torch.nn.functional as F
from torchvision.utils import save_image
from typing import Any, Optional

from mlxploit.attack.attacker import Attacker
from mlxploit.attack.utils import (
    print_prob_ranking, load_model_and_labels, load_original_image, preprocess)
from mlxploit.attack.adversarial.fgsm import AdversarialFGSM
from mlxploit.attack.adversarial.lbfgs import AdversarialLBFGS


class Adversarial(Attacker):
    """
    Adversarial Attack base class
    Reference: https://arxiv.org/pdf/1810.00069.pdf#subsection.4.2
    """
    def __init__(
        self,
        console: Console,
        model_file: Optional[str] = None,
        model_hf: Optional[str] = None,
        technique: Optional[str] = None,
        img: Optional[str] = None,
        epsilons: Optional[str] = None,
        n_downloads: int = 0,
        outdir: Optional[str] = None,
        device: Optional[str] = None,
        quiet: bool = False,
        verbose: bool = False,
    ) -> None:
        super(Adversarial, self).__init__(
            console=console,
            model_file=model_file,
            model_hf=model_hf,
            outdir=outdir,
            device=device,
            quiet=quiet,
            verbose=verbose,
        )

        self.img = img
        self.epsilons = [float(eps)  for eps in epsilons.split(',')] if epsilons is not None else None
        self.n_downloads = n_downloads

        # Set adversarial technique
        if technique is None:
            self.technique = "fgsm"
        else:
            self.technique = technique


    def attack(self) -> None:
        """
        Attack ML model with adversarial attack
        """
        loaded_model_and_labels = load_model_and_labels(
            console=self.console,
            supported_huggingface_architectures=Adversarial.supported_huggingface_architectures(),
            device=self.device, model_path=self.model_file, repo_id=self.model_hf
        )
        if loaded_model_and_labels is None:
            return   

        model, model_type, labels = loaded_model_and_labels

        original_image = load_original_image(console=self.console, img=self.img)
        if original_image is None:
            return

        # Preprocess original image
        original_image_batch = preprocess(
            console=self.console,
            image=original_image,
            device=self.device)
        
        # Initial prediction
        preds = self.predict(
            model=model, inputs=original_image_batch, labels=labels, model_type=model_type)
        if preds is None:
            return
        
        top_probs, top_idxs = preds
        target_prob = top_probs[0]
        target_idx = top_idxs[0]

        if self.technique == "fgsm":
            epsilons = AdversarialFGSM.get_epsilons(self.epsilons)
            adv_examples = AdversarialFGSM.generate(
                console=self.console,
                model=model,
                original_image_batch=original_image_batch,
                target_idx=target_idx,
                model_type=model_type,
                labels=labels,
                epsilons=epsilons)

        elif self.technique == "lbfgs":
            adv_examples = AdversarialLBFGS.generate(
                console=self.console,
                model=model,
                original_image_batch=original_image_batch,
                target_idx=target_idx)
            
        if adv_examples is None:
            self.console.print(f":exclamation: Adversarial examples not generated.", style="yellow")
            return

        # Save adversarial examples
        self.save_adversarial_examples(
            epsilons=epsilons, adv_examples=adv_examples)
    

    def save_adversarial_examples(
        self,
        epsilons: list[float],
        adv_examples: list[Any],
    ) -> None:
        """
        Save generated adversarial examples.
        """
        self.console.print(":floppy_disk: Saving the adversarial examples...")

        # Create "adversarial_examples" folder under `outdir`
        adv_directory = self.outdir / "adversarial_examples"
        adv_directory.mkdir(parents=True, exist_ok=True)

        # Reverse each list
        adv_examples.reverse()
        epsilons = epsilons[:len(adv_examples)]
        epsilons.reverse()

        for i, adv_example in enumerate(adv_examples):
            if 0 < self.n_downloads <= i:
                break
            _label, _prob, ex = adv_example
            save_image(ex, f"{self.outdir}/{adv_directory.name}/example_eps{epsilons[i]}.png")

        self.console.print(f":party_popper: Saved adversarial examples under [bold bright_green]{self.outdir}/{adv_directory.name}[/bold bright_green]!")


    def predict(
        self,
        model: Any,
        inputs: Any,
        labels: list[str],
        model_type: str
    ) -> Optional[tuple[Any, Any]]:
        """
        Predict
        """
        with torch.no_grad():
            if model_type == 'pytorch':
                preds = model(inputs)
            elif model_type == 'huggingface':
                preds = model(inputs).logits

        if preds is None:
            return None
        
        probs = F.softmax(preds[0], dim=0)
        top_probs, top_idxs = torch.topk(probs, 5)
        # Display the initial prediction
        print_prob_ranking(console=self.console,
                            title=f":crown: Prediction on Original Image :crown:",
                            top_probs=top_probs,
                            top_idxs=top_idxs,
                            labels=labels)
        
        return top_probs, top_idxs
    

    @staticmethod
    def supported_techniques() -> list[tuple[str, str]]:
        """
        Supported techniques for adversarial examples.
        """
        return [
            ('FGSM (Fast Gradient Sign Method)', 'fgsm'),
            ('L-BFGS (Limited-memory BFGS)', 'lbfgs')
            # 'jsma',      # JSMA (Jacobian Saliency Map Approach)
        ]
    

    @staticmethod
    def supported_huggingface_architectures() -> list[tuple[str, str]]:
        """
        Supported Hugging Face model's architectures
        """
        # TODO: Support other architectures
        return [
            ("ImageClassification", "AutoModelForImageClassification"),
        ]