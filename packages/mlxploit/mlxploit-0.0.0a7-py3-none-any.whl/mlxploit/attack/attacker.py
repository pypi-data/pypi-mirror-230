from rich.console import Console
from typing import Optional

from mlxploit.base import Base


class Attacker(Base):
    """
    The Attacker Base class which is inherited each attacker class.
    """

    def __init__(
        self,
        console: Console,
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


    # def _attack(self):
    #     if self.model_file is not None:
    #         # Attack model from file path
    #         target_abs_path = Path(self.model_file).absolute()
    #         if target_abs_path.is_dir():
    #             pass
    #         else:
    #             file_ext = os.path.splitext(target_abs_path)[1]
    #             if file_ext == '':
    #                 self.console.print(
    #                     f":exclamation: There is not file extension of the model path.",
    #                     style="red")
    #                 return
                
    #             if file_ext in Attacker._supported_pytorch_extensions():
    #                 self._attack(file_path=path)
    #             else:
    #                 self.console.print(f":exclamation: File extension not supporeted!: {file_ext}", style="red")
                
    #             # self._attack_file(path=target_abs_path, extension=file_ext)
    #     elif self.model_hf is not None:
    #         # Attack Hugging Face model
    #         self.console.print(f":hugging_face: Start attacking Hugging Face model [bright_green]`{self.model_hf}`[/bright_green]...")
    #         self._attack(repo_id=self.model_hf)


    # def _attack_file(self, path: Path, extension=str):
    #     self.console.print(f":rocket: Start attacking ML model from file path [bright_green]`{self.model_file}`[/bright_green]...")

    #     if extension in Attacker._supported_pytorch_extensions():
    #         self._attack(file_path=path)
    #     else:
    #         self.console.print(f":exclamation: File extension not supporeted!: {extension}", style="red")


    # def _attack(self, file_path: str or Path = None, repo_id: str = None):
    #     if self.mode == 'adversarial':
    #         if self.technique.lower() == 'fgsm':
    #             AdversarialFGSM.attack(
    #                 console=self.console,
    #                 file_path=file_path, repo_id=repo_id,
    #                 device=self.device,
    #                 img=self.img,
    #                 epsilons=self.epsilons,
    #                 n_downloads=self.n_downloads,
    #                 outdir=self.outdir)
    #         elif self.technique.lower() == 'lbfgs':
    #             AdversarialLBFGS.attack(
    #                 console=self.console,
    #                 file_path=file_path, repo_id=repo_id,
    #                 device=self.device,
    #                 img=self.img,
    #                 n_downloads=self.n_downloads,
    #                 outdir=self.outdir)
    #         else:
    #             self.console.print(f":exclamation: You specified unknown attack technique: {self.technique}", style="red")
    #     elif self.mode == 'membership':
    #         MembershipInference.attack(
    #             console=self.console,
    #             file_path=file_path,
    #             repo_id=repo_id,
    #             device=self.device,
    #             outdir=self.outdir
    #         )
    #     else:
    #         self.console.print(f":exclamation: You specified unknown attack mode: {self.mode}", style="red")


    @staticmethod
    def _supported_pytorch_extensions() -> list[str]:
        """
        Supported PyTorch model file extensions
        """
        return [".pt", ".pth"]