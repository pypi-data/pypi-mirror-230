from dataclasses import dataclass
import typer
from typing import Optional
from typing_extensions import Annotated, TypeAlias

HELP_PANEL_GENERAL = 'General Options'
HELP_PANEL_ATTACK = 'Attack Options'

# General Options

OptGeneralModelFile: TypeAlias = Annotated[
    Optional[str],
    typer.Option(
        "--model-file", "-m",
        help="A file path for ML model.",
        rich_help_panel=HELP_PANEL_GENERAL)]


OptGeneralModelHF: TypeAlias = Annotated[
    Optional[str],
    typer.Option(
        "--model-hf", "-hf",
        help="Hugging Face model e.g. 'owner/model-name'.",
        rich_help_panel=HELP_PANEL_GENERAL)]

OptGeneralDevice: TypeAlias = Annotated[
    Optional[str],
    typer.Option(
        "--device", "-d",
        help="Device e.g. 'cuda' or 'cpu'.",
        rich_help_panel=HELP_PANEL_GENERAL)]

OptGeneralOutdir: TypeAlias = Annotated[
    Optional[str],
    typer.Option(
        "--outdir", "-o",
        help="Output directory. Default is current working directory.",
        rich_help_panel=HELP_PANEL_GENERAL)]

OptGeneralQuiet: TypeAlias = Annotated[
    bool,
    typer.Option(
        "--quiet", "-q",
        help="Queit mode displays few outputs.",
        rich_help_panel=HELP_PANEL_GENERAL)]

OptGeneralVerbose: TypeAlias = Annotated[
    bool,
    typer.Option(
        "--verbose", "-v",
        help="Verbose mode displays louder.",
        rich_help_panel=HELP_PANEL_GENERAL)]


# Options for Adversarial Attacks

OptAdvTechnique: TypeAlias = Annotated[
    str,
    typer.Option(
        "--technique", "-T",
        help="Technique for using to attack.",
        rich_help_panel=HELP_PANEL_ATTACK)]

OptAdvListTech: TypeAlias = Annotated[
    bool,
    typer.Option(
        "--list", "-l",
        help="List techniques for Adversarial Attack.",
        rich_help_panel=HELP_PANEL_ATTACK)]

OptAdvImg: TypeAlias = Annotated[
    Optional[str],
    typer.Option(
        "--img", "-i",
        help="Original picture to be used for generating adversarial examples.",
        rich_help_panel=HELP_PANEL_ATTACK)]

OptAdvEpsilons: TypeAlias = Annotated[
    str,
    typer.Option(
        "--epsilons", "-e",
        help="Epsilons to be used for generating adversarial examples. For example, set '0,0.01,0.05,0.1,0.15,0.2,0.25.'",
        rich_help_panel=HELP_PANEL_ATTACK)]

OptAdvNDownloads: TypeAlias = Annotated[
    int,
    typer.Option(
        "--n-downloads", "-n",
        min=0,
        help="Number of examples to download. This option is used for Adversarial Attack. 0 by default is to download all. For example, 2 is to download the last 2 examples.",
        rich_help_panel=HELP_PANEL_ATTACK)]


# Options for Membership Inference Attack

OptMiaDataset: TypeAlias = Annotated[
    str,
    typer.Option(
        "--dataset", "-ds",
        help="Dataset to be used for Membership Inference Attack.",
        rich_help_panel=HELP_PANEL_ATTACK)]


OptMiaListDatasets: TypeAlias = Annotated[
    bool,
    typer.Option(
        "--list-datasets", "-lds",
        help="List supported built-in datasets.",
        rich_help_panel=HELP_PANEL_ATTACK)]
