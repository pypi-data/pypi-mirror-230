import numpy as np
from rich.console import Console
from rich.progress import Progress
from rich.table import Table
import torch
from torch.utils.data import DataLoader, random_split
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms
from typing import Any, Optional, Sized
import inspect

import mlxploit.attack.membership.models as mia_models


class ShadowProcessor:
    def __init__(
        self,
        console: Console,
        criterion: Any,
        optimizer: Any,
        n_classes: int,
        device: str,
        shadow_in_loader: DataLoader,
        shadow_out_loader: DataLoader,
    ):
        """
        Shadow processor for training shadow models and generating predictions with shadow dataset.
        """
        self.console = console
        self.device = device

        self.criterion = criterion
        self.optimizer = optimizer

        self.n_classes = n_classes

        self.shadow_models = self._create_shadow_models()
        self.shadow_in_loader = shadow_in_loader
        self.shadow_out_loader = shadow_out_loader


    def _create_shadow_models(self) -> list[Any]:
        """
        Create various shadow models with similar architectures to target model.

        Arguments:
            n (int): Number of shadow models to create
        """
        shadow_models = []
        for name, obj in inspect.getmembers(mia_models, inspect.isclass):
            if "ShadowNet" in name:
                shadow_models.append(obj(output_size=self.n_classes).to(self.device))
        return shadow_models
    

    def train_shadow_models(self) -> None:
        """
        Train shadow models on shadow-in data
        """
        self.console.print(":brain: Training shadow models on shadow training data...")

        effective_shadow_models = []

        for i, shadow_model in enumerate(self.shadow_models):

            shadow_model_name = shadow_model.__class__.__name__

            try:
                criterion = nn.CrossEntropyLoss()
                optimizer = torch.optim.SGD(shadow_model.parameters(), lr=0.001, momentum=0.9)

                n_epochs = 10

                with Progress() as progress:
                    task = progress.add_task(f":muscle: Training {shadow_model_name} model...", total=n_epochs)

                    for epoch in range(n_epochs):
                        shadow_model.train(True)

                        total_loss = 0.0

                        for inputs, labels in self.shadow_in_loader:
                            optimizer.zero_grad()
                            outputs = shadow_model(inputs)
                            loss = criterion(outputs, labels)
                            loss.backward()
                            optimizer.step()

                            total_loss += loss.item()
                        progress.console.print(f":alarm_clock: Epoch {epoch+1} - Loss: {total_loss / len(self.shadow_in_loader):.3f}")
                        progress.advance(task)
                    progress.console.print(f":thumbsup: {shadow_model_name} model trained successfully!")
                    effective_shadow_models.append(shadow_model)
            except:
                self.console.print(f":sweat_drops: {shadow_model_name} model is not suitable for this dataset!", style="yellow")
    
        self.console.print(":thumbsup: Finish training all shadow models!")

        # Update shadow models
        self.shadow_models = effective_shadow_models


    def create_attack_train_set(self) -> Optional[list[tuple[Any, Any]]]:
        """
        Generate predictions/labels for each shadow model on the shadow dataset. These are used for trainnig attack model.
        """

        if len(self.shadow_models) == 0:
            self.console.print(":exclamation: There are no suitable shadow models for this dataset.", style="red")
            return None

        self.console.print(":eyes: Generating predictions for each shadow model on the shadow data...")

        # Get splitted indices for splitting shadow-in loader and shadow-out loader
        n_samples = len(self.shadow_in_loader.dataset)
        n_shadow_models = len(self.shadow_models)
        
        split_sizes = [n_samples // n_shadow_models] * n_shadow_models
        split_sizes[-1] += n_samples % n_shadow_models

        split_shadow_in_datasets = random_split(self.shadow_in_loader.dataset, split_sizes)
        split_shadow_out_datasets = random_split(self.shadow_out_loader.dataset, split_sizes)

        split_shadow_in_loaders = [DataLoader(dataset=split, batch_size=64, shuffle=True) for split in split_shadow_in_datasets]
        split_shadow_out_loaders = [DataLoader(dataset=split, batch_size=64, shuffle=True) for split in split_shadow_out_datasets]

        # Split original dataset into shadow-in and shadow-out
        shadow_in_probs = []
        shadow_in_labels = []
        shadow_out_probs = []
        shadow_out_labels = []

        for i, shadow_model in enumerate(self.shadow_models):
            # Shadow in training
            in_probs, in_labels = self._create_attack_train_set(
                shadow_model, split_shadow_in_loaders[i], flag=1)
            shadow_in_probs.append(in_probs)
            shadow_in_labels.append(in_labels)

            # Shadow out of training
            out_probs, out_labels = self._create_attack_train_set(
                shadow_model, split_shadow_out_loaders[i], flag=0)
            shadow_out_probs.append(out_probs)
            shadow_out_labels.append(out_labels)

        shadow_in_probs = np.concatenate(shadow_in_probs)
        shadow_in_labels = np.concatenate(shadow_in_labels)
        shadow_out_probs = np.concatenate(shadow_out_probs)
        shadow_out_labels = np.concatenate(shadow_out_labels)

        # Concatenate
        shadow_probs = np.concatenate([shadow_in_probs, shadow_out_probs])
        shadow_labels = np.concatenate([shadow_in_labels, shadow_out_labels])

        attack_set = []
        for i in range(len(shadow_probs)):
            attack_set.append((shadow_probs[i], shadow_labels[i]))

        return attack_set


    def _create_attack_train_set(
        self,
        shadow_model: Any,
        shadow_loader: DataLoader,
        flag: int
    ) -> tuple[list[Any], list[Any]]:
        """
        Create (probability vector, label) set for training attack model by evaluating shadow data loader on shadow model.

        Arguments:
            shadow_model: A shadow model
            shadow_loader: Shadow data loader (in or out)
            flag (int): 1 => In training set, 0 => Out of training set
        """
        probs_list = []
        labels_list = []

        with torch.no_grad():
            shadow_model.eval()
            for inputs, _ in shadow_loader:
                inputs = inputs.to(self.device)
                outputs = shadow_model(inputs)

                # Get probability vector
                prob_vectors = torch.softmax(outputs, dim=1).squeeze()
                prob_vectors = prob_vectors.cpu().numpy()

                for i in range(len(inputs)):
                    probs_list.append(prob_vectors[i])
                    labels_list.append(np.array([flag]))
        return probs_list, labels_list


class AttackProcessor:
    """
    Attack processor for training attack model and inferencing membership for specific dataset.
    """
    def __init__(self, console: Console, device: str, n_classes: int) -> None:
        self.console = console
        self.attack_model = mia_models.AttackNet(input_size=n_classes)
        self.criterion = nn.BCELoss()
        self.optimizer = optim.Adam(self.attack_model.parameters(), lr=0.001)
        self.device = device


    def train_attack_model(self, attack_train_set: list) -> None:
        """
        Train attack model with train set (probability vector, label).
        """
        n_epochs = 5

        self.attack_model.train(True)

        with Progress() as progress:
            task = progress.add_task(":muscle: Training attack model...", total=n_epochs)

            for epoch in range(n_epochs):
                total_loss = 0.0
                
                for prob_vector, label in attack_train_set:
                    self.optimizer.zero_grad()
                    inputs = torch.from_numpy(prob_vector)
                    outputs = self.attack_model(inputs)
                    loss = self.criterion(outputs, torch.from_numpy(label).to(torch.float32))
                    loss.backward()
                    self.optimizer.step()

                    total_loss += loss.item()
                progress.console.print(f":alarm_clock: Epoch {epoch+1} - Loss: {total_loss / len(attack_train_set):.3f}")
                progress.advance(task)


    def predict_membership(self, target_model: Any, data_loader: DataLoader) -> list[float]:
        target_model.eval()

        # Create a transform (preprocess) to resize inputs if target model needs to do that.
        resize_transform = None
        if hasattr(target_model, 'config') and hasattr(target_model.config, 'image_size'):
            img_size = target_model.config.image_size
            resize_transform = transforms.Resize(img_size)

        with Progress() as progress:
            task = progress.add_task(":thinking_face: Inferencing membership for target dataset...", total=len(data_loader))

            all_scores: list[float] = []
            for i, data in enumerate(data_loader):
                inputs, _ = data
                scores = self.predict_membership_score(inputs=inputs, target_model=target_model, transform=resize_transform)
                all_scores.extend(scores)
                progress.advance(task)
            return all_scores
    

    def predict_membership_score(
        self,
        inputs: torch.Tensor,
        target_model: Any,
        transform: Optional[Any] = None
    ) -> list[float]:
        target_model.eval()

        scores = []
        with torch.no_grad():
            # Resize inputs
            if transform is not None:
                inputs = torch.stack([transform(img) for img in inputs])

            target_outputs = target_model(inputs)
            if hasattr(target_outputs, 'logits'): # For Hugging Face models
                target_outputs = target_outputs.logits
            target_prob_vector = torch.softmax(target_outputs, dim=1).squeeze()

            # score = self.attack_model(target_prob_vector).item()
            attack_outputs = self.attack_model(target_prob_vector)
            scores.extend(attack_outputs)
            return scores
        

    def statistics(
        self,
        scores: list[float],
        target_model_name: Any,
        dataset: str
    ) -> None:
        cnt_membership = 0
        cnt_uncertain = 0
        cnt_non_membership = 0

        for score in scores:
            if score > 0.5:
                cnt_membership += 1
            elif score == 0.5:
                cnt_uncertain += 1
            elif score < 0.5:
                cnt_non_membership += 1
            else:
                cnt_uncertain += 1

        console = Console()
        console.print()
        table = Table(
            title=f":bar_chart: Statistics of Membership Inference for [bold cyan]{dataset}[/bold cyan] against [bold bright_green]{target_model_name}[/bold bright_green] :bar_chart:",
            style="bold bright_magenta")
        table.add_column("Total", justify="right", style="bold bright_green")
        table.add_column("Membership", justify="right", style="bold bright_blue")
        table.add_column("Uncertain", justify="right", style="bold bright_yellow")
        table.add_column("Non-Membership", justify="right", style="bold bright_red")
        table.add_row(f"{len(scores)}", f"{cnt_membership}", f"{cnt_uncertain}", f"{cnt_non_membership}")
        console.print(table)
