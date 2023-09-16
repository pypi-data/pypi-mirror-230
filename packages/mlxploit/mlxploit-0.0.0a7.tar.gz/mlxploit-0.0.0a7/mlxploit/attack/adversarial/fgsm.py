from pathlib import Path
from rich.console import Console
import torch
from torch import Tensor
import torch.nn.functional as F
from torchvision import transforms
import typer
from typing import Any, Optional

from mlxploit.attack.utils import denormalize, print_prob_ranking


class AdversarialFGSM:
    """
    Adversarial attack with FGSM (Fast Gradient Sign Method)
    References:
        - https://arxiv.org/pdf/1810.00069.pdf#subsection.4.2
    """

    @staticmethod
    def generate(
        console: Console,
        model: Any,
        original_image_batch: Any,
        target_idx: int,
        model_type: str,
        labels: list[str],
        epsilons: list[float],
    ) -> Optional[list[tuple[Any, Any, Tensor]]]:
        """
        A main function to generate adversarial examples with FGSM.
        """
        console.print(":brain: Start generating adversarial examples with FGSM...")
        console.print(":mobile_phone: Calculating perturbations...")
        perturbations = AdversarialFGSM.calc_perturbations(
            model, original_image_batch, torch.tensor([target_idx]), model_type=model_type)

        # Generate adversarial examples
        console.print(":factory: Generating adversarial examples...")

        adv_examples: list[tuple[Any, Any, Tensor]] = []

        # Keep generating adversarial examples after fooling target model.
        is_continue = False

        for eps in epsilons:
            original_image_batch_denorm = denormalize(original_image_batch)
            adv_img = original_image_batch_denorm + eps * perturbations
            adv_img = torch.clamp(adv_img, 0, 1)
            # Normalize the adversarial image
            adv_img_norm = transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))(adv_img)

            # Predict adversarial example
            preds = AdversarialFGSM.predict(
                console=console, model=model, inputs=adv_img_norm, labels=labels, model_type=model_type
            )
            if preds is None:
                return None
            adv_top_probs, adv_top_idxs = preds

            # Add list
            adv_examples.append((labels[adv_top_idxs[0]], adv_top_idxs[0], adv_img))

            # If the adversial example could fool target model, check if stop to generate adversarial examples.
            if adv_top_idxs[0] != target_idx and is_continue is False:
                is_continue = AdversarialFGSM._is_continue(console=console, eps=eps)
                if not is_continue:
                    console.print(":stop_sign: Stop generating adversarial examples.")
                    break

        return adv_examples


    @staticmethod
    def predict(
        console,
        model: Any,
        inputs: Any,
        labels: list[str],
        model_type: str
    ) -> Optional[tuple[Any, Any]]:
        with torch.no_grad():
            if model_type == 'pytorch':
                preds = model(inputs)
            elif model_type == 'huggingface':
                preds = model(inputs).logits

        if preds is None:
            console.print(f":exclamation: Could not predict.", style="red")
            return None
        
        probs = F.softmax(preds[0], dim=0)
        top_probs, top_idxs = torch.topk(probs, 5)
        # Display the initial prediction
        print_prob_ranking(console=console,
                            title=f":crown: Prediction on Original Image :crown:",
                            top_probs=top_probs,
                            top_idxs=top_idxs,
                            labels=labels)
        
        return top_probs, top_idxs


    @staticmethod
    def calc_perturbations(
        model: Any,
        inputs: Any,
        target: Any,
        model_type: str
    ) -> Any:
        """
        Calculate perturbations for PyTorch models.
        """
        inputs.requires_grad = True

        if model_type == "pytorch":
            pred = model(inputs)
            loss = F.nll_loss(pred, target)
            model.zero_grad()
            loss.backward()
            gradient = inputs.grad.data
            return gradient.sign()
        elif model_type == 'huggingface':
            logits = model(inputs).logits
            loss = F.nll_loss(logits, target)
            gradient = torch.autograd.grad(loss, inputs)[0]
            return gradient.sign()
    
        return None
    

    @staticmethod
    def get_epsilons(epsilons: Optional[list[float]] = None) -> list[float]:
        """
        Get epsilons list to geenrate perturbated images.
        """
        if epsilons is None:
            return [0, .01, .05, .1, .2]
        else:
            return epsilons


    @staticmethod
    def _is_continue(console: Console, eps: float) -> bool:
        """
        Confirm to continue attacking after fooling ML model.
        """
        console.print(f":thumbsup: Fooled target model successfully at Eps {eps}!")
        is_continue = typer.confirm(f"Continue to generate?")
        return is_continue