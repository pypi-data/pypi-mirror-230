from pathlib import Path
from typing import Optional, Dict
import os
import ruamel.yaml
from .utils import Message
from .scan import ScanData
from .utils import DirTree

message = Message()


class DataProfiler(ScanData):
    """
    Create a dataset profile as .yml file that can be used
    in many different senarios like validate, and check quality
    of similar datasets in production or test/validation datasets,
    also create data cleaning and automatic transformation pipeline
    to be used in certain conditions based on dataset.

    creating an instance of DataProfiler will automatically create a directory on
    your current working directory(default), or any other path on your
    system that will hold .yml files of datasets.

    all profiles that will be created using this instance will be in
    this directory.

    Parameters
    ----------
    path : path of the directory that holds all data-profiles .yml files.

    Attributes
    ----------
    cwd : current working directory.

    profiler_path : path of the directory that holds all data-profiles .yml files
    if passed as a parameter to DataProfiler, else it will be in
    the current working directory.

    profiler_config : path of the directory in your system.
    """

    def __init__(self, path: Optional[str] = None) -> None:
        super().__init__()
        self.cwd = Path(os.getcwd())

        def _profiler_path() -> Path:
            if path:
                profiler_path = Path(path)
            else:
                profiler_path = self.cwd
            return profiler_path

        self.profiler_path = _profiler_path()

        def _create_config_dir() -> Path:
            try:
                profiler_dir = self.profiler_path.joinpath(".dprofiler")
                if not profiler_dir.exists():
                    profiler_dir.mkdir()
                    message.printit("new data-profile created successfully.", "info")
                else:
                    message.printit("profiler already exists", "warn")
                return profiler_dir
            except FileNotFoundError:
                raise FileNotFoundError(f"{self.profiler_path} doesn't exist")

        self.profiler_config = _create_config_dir()

    def __str__(self) -> str:
        return f"Profile of:{self.profiler_path}"

    def create_profile(
        self, data_profile: Dict, file_name: str, override: Optional[bool] = None
    ) -> None:
        """
        create .yml file of the dataset, that will contain all information
        of the dataset.

        Parameters
        ----------
        data_profile : dictionary that holds all information of dataset.
        file_name : file name of the .yml file to avoid duplication issues.
        override : this is the option to override the information in
        .yml file if exist and rewrite the profile again.
        """
        if not (file_name.endswith(".yml") or file_name.endswith(".yaml")):
            file_name = file_name + ".yml"
        if self.profiler_config.joinpath(file_name).exists():
            if override:
                with open(self.profiler_config.joinpath(file_name), "w") as conf:
                    yaml = ruamel.yaml.YAML()
                    yaml.indent(sequence=4, offset=2)
                    yaml.dump(data_profile, conf)
            else:
                message.printit("profile already exists", "warn")
        else:
            with open(self.profiler_config.joinpath(file_name), "w") as conf:
                yaml = ruamel.yaml.YAML()
                yaml.indent(sequence=4, offset=2)
                yaml.dump(data_profile, conf)

    def del_profile(self, file_name: str) -> None:
        """
        delete .yml profile.

        Parameters
        ----------
        file_name : file name that will be deleted.
        """
        try:
            if not (file_name.endswith(".yml") or file_name.endswith(".yaml")):
                file_name = file_name + ".yml"
            self.profiler_config.joinpath(file_name).unlink()
        except FileNotFoundError:
            raise FileNotFoundError(
                f"No Data Profile Exists in profiler with name: {file_name}"
            )

    def profiler_tree(self) -> str:
        """
        Generate the File Structure of profiler as tree

        Returns
        -------
        str of tree file structure of profiler
        """
        profiler_tree = DirTree(self.profiler_config)
        return profiler_tree.generate()
