from pathlib import Path
from rich.console import Console
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
from torchvision.datasets import CIFAR10, CIFAR100
import torchvision.transforms as transforms
from typing import Any, Optional

from mlxploit.attack.attacker import Attacker
from mlxploit.attack.utils import load_model_and_labels
from mlxploit.attack.membership.processors import AttackProcessor, ShadowProcessor


class MembershipInference(Attacker):
    """
    Membership Inference Attack base class
    References:
    - https://arxiv.black/pdf/1610.05820.pdf
    - https://jpsec.ai/miattack/
    """
    def __init__(
        self,
        console: Console,
        dataset: str = 'cifar10',
        model_file: Optional[str] = None,
        model_hf: Optional[str] = None,
        outdir: Optional[str] = None,
        device: Optional[str] = None,
        quiet: bool = False,
        verbose: bool = False
    ) -> None:
        
        super(Attacker, self).__init__(
            console=console,
            model_file=model_file,
            model_hf=model_hf,
            device=device,
            outdir=outdir,
            quiet=quiet,
            verbose=verbose)
        
        self.dataset = dataset


    def attack(self) -> None:
        """
        Main function to membership inference attack
        """
        # Load target model
        loaded_model_and_labels = load_model_and_labels(
            console=self.console,
            supported_huggingface_architectures=MembershipInference.supported_huggingface_architectures(),
            device=self.device, model_path=self.model_file, repo_id=self.model_hf)
        if loaded_model_and_labels is None:
            return

        target_model, target_model_type, target_labels = loaded_model_and_labels

        # Load sample data, make shadow data and prepare classes.
        data_loaders = self.load_data()
        if data_loaders is None:
            return

        (
            train_loader,
            test_loader,
            target_in_loader,
            target_out_loader,
            shadow_in_loader,
            shadow_out_loader,
            classes
        ) = data_loaders

        target_model = self.adjust_model_layers(model=target_model, n_classes=len(classes))
        if target_model is None:
            return
                
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(target_model.parameters(), lr=0.001)
        
        # Instantiate shadow processor
        shadow_processor = ShadowProcessor(
            console=self.console,
            shadow_in_loader=shadow_in_loader,
            shadow_out_loader=shadow_out_loader,
            criterion=criterion,
            optimizer=optimizer,
            n_classes=len(classes),
            device=self.device)
        # Train shadow model
        shadow_processor.train_shadow_models()
        # Create (probability vector, label) set for training attack model
        attack_train_set = shadow_processor.create_attack_train_set()
        if attack_train_set is None:
            return
        
        # Instantiate attack processor
        attack_processor = AttackProcessor(console=self.console, device=self.device, n_classes=len(classes))
        # Train attack model with train set
        attack_processor.train_attack_model(attack_train_set)

        # Inference membership
        scores = attack_processor.predict_membership(target_model=target_model, data_loader=target_in_loader)
        
        # Statistics
        target_model_name = self.model_file if self.model_file is not None else self.model_hf
        attack_processor.statistics(scores=scores, dataset=self.dataset, target_model_name=target_model_name)


    def load_data(self) -> Optional[tuple]:
        """
        Load dataset and return data loaders as follow:
            - train
                - target-in     (for training target model and membership inference)
                - target-out    (for testing membership inference)
                - shadow-in     (for training shadow models and creating train data for attack model)
                - shadow-out    (for creating train data for attack model)
            - test
        """
        self.console.print(f":file_cabinet: Loading dataset...")

        comp = [
            transforms.ToTensor(),
            transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225)),
        ]

        transform = transforms.Compose(comp)

        if self.dataset == 'cifar10':            
            train_dataset = CIFAR10(root=self.outdir, train=True, download=True, transform=transform)
            test_dataset = CIFAR10(root=self.outdir, train=False, download=True, transform=transform)
        elif self.dataset == 'cifar100':
            train_dataset = CIFAR100(root=self.outdir, train=True, download=True, transform=transform)
            test_dataset = CIFAR100(root=self.outdir, train=False, download=True, transform=transform)
        else:
            self.console.print(f":exclamation: {self.dataset} is unsupported dataset!", style="red")
            return None
        
        classes = train_dataset.classes
        
        batch_size = 64

        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

        # Split train dataset into (target-in, target-out, shadow-in, shadow-out)
        each_size = len(train_dataset) // 4
        target_in_dataset, target_out_dataset, shadow_in_dataset, shadow_out_dataset = random_split(
            train_dataset, [each_size, each_size, each_size, each_size])

        # Create data loader
        target_in_loader = DataLoader(target_in_dataset, batch_size=batch_size, shuffle=True)
        target_out_loader = DataLoader(target_out_dataset, batch_size=batch_size, shuffle=False)
        shadow_in_loader = DataLoader(shadow_in_dataset, batch_size=batch_size, shuffle=True)
        shadow_out_loader = DataLoader(shadow_out_dataset, batch_size=batch_size, shuffle=True)

        return train_loader, test_loader, target_in_loader, target_out_loader, shadow_in_loader, shadow_out_loader, classes
    

    def adjust_model_layers(self, model: Any, n_classes: int) -> Optional[Any]:
        """
        Adjust model output layer to have N classes for speicic dataset
        """
        if hasattr(model, 'fc'):
            model.fc = nn.Linear(in_features=model.fc.in_features, out_features=n_classes)
        elif hasattr(model, 'classifier'):
            if hasattr(model.classifier, '__getitem__'):
                model.classifier[-1] = nn.Linear(in_features=model.classifier[-1].in_features, out_features=n_classes)
            else:
                model.classifier = nn.Linear(in_features=model.classifier.in_features, out_features=n_classes)
        else:
            self.console.print(":exclamation: The output layer attribute not found on this model!", style="red")
            return None
        return model


    @staticmethod
    def supported_huggingface_architectures() -> list[tuple[str, str]]:
        """
        Supported Hugging Face model's architectures
        """
        # TODO: Support other architectures
        return [
            ("ImageClassification", "AutoModelForImageClassification"),
        ]
    

    @staticmethod
    def supporeted_datasets() -> list[tuple[str, str]]:
        """
        Supported built-in datasets
        """
        return [
            ('CIFAR-10', 'cifar10'),
            ('CIFAR-100', 'cifar100'),
        ]
