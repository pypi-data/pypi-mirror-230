"""Utility functions for the explore module."""
import pathlib

import streamlit as st
import yaml
from pydantic import BaseModel  # pylint: disable=no-name-in-module


def select_file_container(dvc_step_data_path: pathlib.Path, tab_key: str) -> pathlib.Path:
    """Container for selecting a file in the DVC step."""
    list_of_files = list(dvc_step_data_path.glob("*"))
    parquet_data_path = [path for path in list_of_files if path.suffix == ".parquet"]

    def _format_path(path: pathlib.Path) -> str:
        return path.parts[-1]

    file_path = st.selectbox(
        "Select a file in the DVC step:",
        options=parquet_data_path,
        format_func=_format_path,
        key=tab_key,
    )
    return file_path


def get_path_last_part(list_of_full_path: list[pathlib.Path]) -> list[str]:
    """Returns a list with the last part of the path for each path in the list."""
    list_of_last_part = [path.parts[-1] for path in list_of_full_path]
    return list_of_last_part


class DVCStep(BaseModel):
    """Data model representing a DVC step."""

    name: str
    output_path: pathlib.Path


def parse_dvc_steps_from_dvc_yaml() -> list[DVCStep]:
    """Parse the DVC steps from the dvc.yaml file."""
    with open("dvc.yaml", "r", encoding="utf-8") as f:
        dvc_yaml = yaml.safe_load(f)

    stages_dict = dvc_yaml["stages"]
    steps = []
    for stage_name, stage_content in stages_dict.items():
        output_path = stage_content["outs"][0]
        steps.append(DVCStep(name=stage_name, output_path=output_path))
    return steps
