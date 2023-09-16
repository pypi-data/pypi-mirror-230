import os
from pathlib import Path
from rich.console import Console
from typing import Optional

from mlxploit.utils import is_zipfile, select_device


class Base:
    def __init__(
        self,
        console: Console,
        model_file: Optional[str] = None,
        model_hf: Optional[str] = None,
        device: Optional[str] = None,
        outdir: Optional[str] = None,
        quiet: bool = False,
        verbose: bool = False,
    ) -> None:
        # Configure general options
        self.device = select_device(device)
        self.outdir = Path(os.getcwd()) if outdir is None else Path(outdir)
        if not self.outdir.exists():
            self.console.print(":file_folder: Specified output directory does not exist. Creating the new one...")
            os.mkdir(self.outdir)

        self.quiet = quiet
        self.verbose = verbose
        self.console = console

        # Target is a zip file (.pt, .h5, etc.) or not.
        self.is_zipfile = is_zipfile(model_file)

        # Model
        self.model_file = model_file
        self.model_hf = model_hf
