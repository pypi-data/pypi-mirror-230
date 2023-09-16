import logging, os
logging.disable(logging.WARNING)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import typer
from typing import Optional
from rich.console import Console
from rich.table import Table

from mlxploit.attack.adversarial.base import Adversarial
from mlxploit.attack.membership.base import MembershipInference
from mlxploit.options import (
    OptGeneralModelFile, OptGeneralModelHF, OptGeneralDevice, OptGeneralOutdir, OptGeneralQuiet, OptGeneralVerbose,
    OptAdvTechnique, OptAdvListTech, OptAdvImg, OptAdvEpsilons, OptAdvNDownloads,
    OptMiaDataset, OptMiaListDatasets,
)
from mlxploit import banner
from mlxploit.__version__ import __version__

console = Console()

app = typer.Typer()


@app.command(name="adv", help="Adversarial Attack", rich_help_panel="Attacks")
def adversarial(
    model_file: OptGeneralModelFile = None,
    model_hf: OptGeneralModelHF = None, 
    device: OptGeneralDevice = None,
    outdir: OptGeneralOutdir = None,
    quiet: OptGeneralQuiet = False,
    verbose: OptGeneralVerbose = False,
    technique: OptAdvTechnique = 'fgsm',
    list_tech: OptAdvListTech = False,
    img: OptAdvImg = None,
    epsilons: OptAdvEpsilons = '0,0.01,0.05,0.1,0.2',
    n_downloads: OptAdvNDownloads = 0,
) -> None:
    # List techniques for adversarial attack
    if list_tech is True:
        table = Table(title=":scroll: List of Techniques for Adversarial Attack :scroll:", style="bright_magenta")
        table.add_column("Techniques", style="bright_cyan")
        table.add_column("Command Examples", style="bright_green")

        for tech in Adversarial.supported_techniques():
            table.add_row(tech[0], f"mlx adv -m mymodel.pt -T {tech[1]}")
        console.print(table)
        return

    if isset_model(model_file, model_hf) is False:
        return
    
    app_dir = typer.get_app_dir("mlxploit")
    console.quiet = quiet

    banner.banner(console, "Adversarial Attack")

    adv = Adversarial(
        technique=technique,
        model_file=model_file,
        model_hf=model_hf,
        img=img,
        epsilons=epsilons,
        n_downloads=n_downloads,
        device=device,
        outdir=outdir,
        quiet=quiet,
        verbose=verbose,
        console=console)
    
    banner.options_table(
        console=adv.console,
        target_model=adv.model_file if adv.model_file is not None else adv.model_hf,
        img=adv.img,
        device=adv.device)
    
    adv.attack()


@app.command(name="mia", help="Membership Inference Attack", rich_help_panel="Attacks")
def membership(
    model_file: OptGeneralModelFile = None,
    model_hf: OptGeneralModelHF = None, 
    device: OptGeneralDevice = None,
    outdir: OptGeneralOutdir = None,
    quiet: OptGeneralQuiet = False,
    verbose: OptGeneralVerbose = False,
    dataset: OptMiaDataset = 'cifar10',
    list_datasets: OptMiaListDatasets = False,
) -> None:
    # List available datasets
    if list_datasets is True:
        table = Table(title=":scroll: List of Buil-in Datasets :scroll:", style="bright_magenta")
        table.add_column("Datasets", style="bright_cyan")
        table.add_column("Command Examples", style="bright_green")
        for sd in MembershipInference.supporeted_datasets():
            table.add_row(sd[0], f"mlx mia -m mymodel.pt -ds {sd[1]}")
        console.print(table)
        return
    
    if isset_model(model_file, model_hf) is False:
        return
    
    app_dir = typer.get_app_dir("mlx")
    console.quiet = quiet

    banner.banner(console, "Membership Inference Attack")

    mia = MembershipInference(
        dataset=dataset,
        model_file=model_file,
        model_hf=model_hf,
        outdir=outdir,
        device=device,
        quiet=quiet,
        verbose=verbose,
        console=console)
    
    banner.options_table(
        console=mia.console,
        target_model=mia.model_file if mia.model_file is not None else mia.model_hf,
        dataset=mia.dataset,
        device=mia.device)

    mia.attack()


@app.command(name="list", help="List attacks", rich_help_panel="General")
def list_attacks() -> None:
    table = Table(title=":scroll: List of Attacks :scroll:", style="bright_magenta")
    table.add_column("Attacks", style="bright_cyan")
    table.add_column("Commands", style="bright_green")
    table.add_row("Adversarial Attack", "mlx adv -m mymodel.pt")
    table.add_row("", "mlx adv -hf microsoft/resnet-50")
    table.add_section()
    table.add_row("Membership Inference Attack", "mlx mia -m mymodel.pt")
    table.add_row("", "mlx mia -hf facebook/convnext-large-224")
    console.print(table)


@app.command(name="version", help="Display the version of MLexploit", rich_help_panel="General")
def version() -> None:
    console.print(f"MLexploit version {__version__}")


@app.callback()
def main() -> None:
    """
    MLxploit - AI/ML Exploitation Framework
    """


def isset_model(model_file: Optional[str] = None, model_hf: Optional[str] = None) -> bool:
    """
    Check if model is set on command.
    """
    if model_file is None and model_hf is None:
        console.print(":exclamation: Please set target ML model with `--model-file/-m` or `--model-hf/-hf`.", style="red")
        return False
    return True
