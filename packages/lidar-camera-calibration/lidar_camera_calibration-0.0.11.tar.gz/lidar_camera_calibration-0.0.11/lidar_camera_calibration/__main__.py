import cProfile
import glob
import logging
import os
import sys
from pathlib import Path

import torch
import typer
from rich.progress import track

from lidar_camera_calibration.tools import calibration, dataset

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

log = logging.getLogger(__name__)

wantToUseCuda = True
useCuda = torch.cuda.is_available() and wantToUseCuda
TORCH_DEVICE = "cuda" if useCuda else "cpu"
TORCH_DTYPE = torch.float32


app = typer.Typer(add_completion=False, rich_markup_mode="rich")

filename = os.path.basename(__file__)

docstring = """
A LiDAR camera calibration toolbox that exploits mutual information between camera intensities
and LiDAR reflectance to learn the relative pose between sensors.\n
\b
[bold green]Examples: [/bold green]
# Run LiDAR camera calibration on bag files located in <root_path>/raw
$ lidar_camera_calibration --image_topic <image_topic> --lidar_topic <lidar_topic> <root_path>:open_file_folder:

# Forms time association between point clouds and images within <root_path>/raw and export them to <root_path>/compressed
$ lidar_camera_calibration --image_topic <image_topic> --lidar_topic <lidar_topic> --generate_compressed <root_path>:open_file_folder:

"""


@app.command(help=docstring)
def run_calibration(
    root_path: Path = typer.Argument(
        ...,
        help="The data directory used for running calibration.",
        show_default=False,
    ),
    # Options ---------------------------------------------------------------------------
    lidar_topic: str = typer.Option(
        None,
        "--lidar_topic",
        show_default=False,
        help="The topic name for the LiDAR data located in the bag file(s)",
    ),
    image_topic: str = typer.Option(
        None,
        "--image_topic",
        show_default=False,
        help="The topic name for the image data located in the bag file(s)",
    ),
    generate_compressed: bool = typer.Option(
        False,
        "--generate_compressed",
        show_default=True,
        help="Form time association between point clouds and images the bag file(s) within <root_path>/raw and export them to <root_path>/compressed without performing calibration.",
    ),
    plot_iter: bool = typer.Option(
        False,
        "--plot_iter",
        show_default=True,
        help="Generate a graph of the cost over the iterations of the optimisation.",
    ),
    max_samples: int = typer.Option(
        5e3,
        "--max_samples",
        show_default=True,
        help="Maximum number of LiDAR points to use from each frame (randomly sampled).",
    ),
    learning_rate: float = typer.Option(
        3e-4,
        "--learning_rate",
        show_default=True,
        help="Learning rate for optimisation.",
    ),
    max_epochs: int = typer.Option(
        50,
        "--max_epochs",
        show_default=True,
        help="Maximum number of epochs for optimisation.",
    ),
    refine_camera: bool = typer.Option(
        True,
        "--refine_camera",
        show_default=True,
        help="Refine camera intrinsics.",
    ),
    # Additional Options ---------------------------------------------------------------------------
    x: float = typer.Option(
        0.1148,
        "--x",
        show_default=True,
        help="The initial x translation \[m] of the LiDAR with respect to the camera",
        rich_help_panel="Additional Options",
    ),
    y: float = typer.Option(
        -0.1570,
        "--y",
        show_default=True,
        help="The initial y translation \[m] of the LiDAR with respect to the camera",
        rich_help_panel="Additional Options",
    ),
    z: float = typer.Option(
        -0.0036,
        "--z",
        show_default=True,
        help="The initial z translation \[m] of the LiDAR with respect to the camera",
        rich_help_panel="Additional Options",
    ),
    roll: float = typer.Option(
        -90,
        "--roll",
        show_default=True,
        help="The initial roll angle \[deg] of the LiDAR with respect to the camera",
        rich_help_panel="Additional Options",
    ),
    pitch: float = typer.Option(
        0,
        "--pitch",
        show_default=True,
        help="The initial pitch angle \[deg] of the LiDAR with respect to the camera",
        rich_help_panel="Additional Options",
    ),
    yaw: float = typer.Option(
        -90,
        "--yaw",
        show_default=True,
        help="The initial yaw angle \[deg] of the LiDAR with respect to the camera",
        rich_help_panel="Additional Options",
    ),
):
    typer.echo(f"root_path is {root_path}")

    dir_raw = Path(os.path.join(root_path, "raw"))
    if not dir_raw.is_dir():
        print(dataset.expected_directory_structure(root_path))
        sys.exit(1)

    dir_compressed = Path(os.path.join(root_path, "compressed"))
    reuse_mat_files = False
    if dir_compressed.is_dir():
        mat_files = glob.glob(os.path.join(dir_compressed, "frame-*.mat"))
        has_matfiles = len(mat_files) > 0
        if has_matfiles:
            if generate_compressed:
                typer.echo(
                    f"There are compressed files already within {dir_compressed}. "
                )
                delete = typer.confirm("Do delete these and re-make them?")
                if delete:
                    for file in mat_files:
                        os.remove(file)
                else:
                    print("Nothing to do. Exiting.")
                    sys.exit(0)
            else:
                typer.echo(
                    f"There are compressed files within {dir_compressed}. Using these for calibration saves time. "
                )
                reuse_mat_files = typer.confirm(
                    "Do you want to re-use these files?", default=True
                )
                if not reuse_mat_files:
                    for file in track(
                        mat_files, description=f"Deleting files in {dir_compressed}"
                    ):
                        os.remove(file)

    has_bagfiles = len(glob.glob(os.path.join(dir_raw, "*.bag"))) > 0
    if reuse_mat_files:
        if generate_compressed:
            typer.echo("Ignoring flag --generate_compressed as loading from MATLAB.")
        if lidar_topic is not None:
            typer.echo(
                f"Ignoring flag --lidar_topic={lidar_topic} as loading from MATLAB."
            )
        if image_topic is not None:
            typer.echo(
                f"Ignoring flag --image_topic={image_topic} as loading from MATLAB."
            )
        calframes = dataset.compressed_data_to_calibration_frames(dir_compressed)

    elif has_bagfiles:
        typer.echo(f"--lidar_topic is {lidar_topic}")
        typer.echo(f"--image_topic is {image_topic}")
        calframes = dataset.bagfile_to_calibration_frames(
            dir_raw, lidar_topic, image_topic
        )

        dataset.calibration_frames_to_compressed_data(dir_compressed, calframes)
        if generate_compressed:
            sys.exit(0)

    else:
        print(f"[Error] No bag files within {dir_raw}!")
        print(dataset.expected_directory_structure(root_path))
        sys.exit(1)

    eta0 = (
        torch.tensor(
            [
                x,
                y,
                z,
                roll * torch.pi / 180,
                pitch * torch.pi / 180,
                yaw * torch.pi / 180,
            ]
        )
        .reshape((-1, 1))
        .to(dtype=TORCH_DTYPE, device=TORCH_DEVICE)
    )
    calibration.calibrate(
        calframes,
        root_path,
        eta0,
        plot_iter=plot_iter,
        max_samples=max_samples,
        num_epochs=max_epochs,
        learning_rate=learning_rate,
        learn_camera=refine_camera,
    )


pr = cProfile.Profile()
pr.enable()
app()
pr.disable()

pr.dump_stats("run_calibration_profile.pstat")
