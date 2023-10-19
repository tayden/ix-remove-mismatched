from pathlib import Path
from typing_extensions import Annotated

import pandas as pd
import typer

NIR_DIR_NAME = "YD030006"
RGB_DIR_NAME = "YC030057"


def main(
        root_dir: Annotated[
            Path,
            typer.Argument(help="Path to a directory containing YC030057 and YD030006 subdirectories")
        ]
):
    rgb_iiq_directory = root_dir / RGB_DIR_NAME
    nir_iiq_directory = root_dir / NIR_DIR_NAME

    data = [{"name": p.name, "type": "RGB"} for p in rgb_iiq_directory.rglob("*.IIQ")] \
           + [{"name": p.name, "type": "NIR"} for p in nir_iiq_directory.rglob("*.IIQ")]

    df = pd.DataFrame(data)

    df['code'] = df['name'].apply(lambda n: n.split("_")[0])

    rgb_df = df[df['type'] == "RGB"]
    rgb_df.set_index('code', inplace=True)
    nir_df = df[df['type'] == "NIR"]
    nir_df.set_index('code', inplace=True)

    matching_df = rgb_df.join(nir_df, lsuffix="_rgb", rsuffix="_nir", how="outer")

    nir_to_remove = matching_df[matching_df["name_rgb"].isna()]
    rgb_to_remove = matching_df[matching_df["name_nir"].isna()]

    (rgb_iiq_directory / 'mismatched').mkdir(exist_ok=True)
    for name in rgb_to_remove['name_rgb']:
        path = rgb_iiq_directory / name
        path.rename(rgb_iiq_directory / 'mismatched' / name)

    (nir_iiq_directory / 'mismatched').mkdir(exist_ok=True)
    for name in nir_to_remove['name_nir']:
        path = nir_iiq_directory / name
        path.rename(nir_iiq_directory / 'mismatched' / name)


def cli():
    typer.run(main)


if __name__ == '__main__':
    typer.run(main)
