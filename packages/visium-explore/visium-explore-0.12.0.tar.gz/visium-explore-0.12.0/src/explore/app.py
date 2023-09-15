"""Streamlit app for data exploration."""
import pathlib

import streamlit as st

from explore.explorer_container.main import explorer_container
from explore.graph_container.main import graph_container
from explore.sample_df_container.main import sample_df_container
from explore.utils import parse_dvc_steps_from_dvc_yaml, select_file_container

DATA_PATH = pathlib.Path("data")


def main() -> None:
    """Main function for the Streamlit app."""
    col1, col2 = st.columns([1, 1])
    dvc_steps = parse_dvc_steps_from_dvc_yaml()
    with col1:
        st.title("Explorer")

        selected_dvc_step = st.selectbox(label="DVC Step selection", options=dvc_steps, format_func=lambda x: x.name)
        dvc_step_key = f"select_box_{selected_dvc_step.name}"
        file_path = select_file_container(selected_dvc_step.output_path, dvc_step_key)
    with col2:
        graph_container()

    if file_path:
        st.write("---")
        st.header("Data model")
        sample_df = sample_df_container(file_path=file_path)

        st.write("---")
        st.header("Data exploration")
        explorer_container(file_path, dvc_step_key, sample_df=sample_df)
    else:
        st.warning("No parquet file found for this DVC step.")


if __name__ == "__main__":
    main()
