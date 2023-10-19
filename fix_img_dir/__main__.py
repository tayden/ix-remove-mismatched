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

    data = [{"name": p.name, "type": "RGB", "path": p} for p in rgb_iiq_directory.rglob("*.IIQ")] \
           + [{"name": p.name, "type": "NIR", "path": p} for p in nir_iiq_directory.rglob("*.IIQ")]

    df = pd.DataFrame(data)

    df['code'] = df['name'].apply(lambda n: n.split("_")[0])

    rgb_df = df[df['type'] == "RGB"]
    rgb_df.set_index('code', inplace=True)
    nir_df = df[df['type'] == "NIR"]
    nir_df.set_index('code', inplace=True)

    matching_df = rgb_df.join(nir_df, lsuffix="_rgb", rsuffix="_nir", how="outer")

    nir_to_remove = matching_df[matching_df["name_rgb"].isna()]
    rgb_to_remove = matching_df[matching_df["name_nir"].isna()]

    if len(rgb_to_remove) > 0:
        (rgb_iiq_directory / 'mismatched').mkdir(exist_ok=True)
        for path in rgb_to_remove['path_rgb']:
            name = path.name
            path.rename(rgb_iiq_directory / 'mismatched' / name)

        print(f"Moved {len(rgb_to_remove)} RGB files to {rgb_iiq_directory / 'mismatched'}")

    if len(nir_to_remove) > 0:
        (nir_iiq_directory / 'mismatched').mkdir(exist_ok=True)
        for path in nir_to_remove['path_nir']:
            name = path.name
            path.rename(nir_iiq_directory / 'mismatched' / name)

        print(f"Moved {len(nir_to_remove)} NIR files to {nir_iiq_directory / 'mismatched'}")


def cli():
    typer.run(main)


if __name__ == '__main__':
    typer.run(main)
