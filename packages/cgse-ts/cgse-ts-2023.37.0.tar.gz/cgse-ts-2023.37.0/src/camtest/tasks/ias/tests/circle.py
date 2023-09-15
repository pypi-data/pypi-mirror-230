import os
from pathlib import Path

from gui_executor.exec import exec_ui, Directory
from gui_executor.utypes import ListList

from camtest import load_setup

UI_MODULE_DISPLAY_NAME = "2 — Circle around optical axis"

ICON_PATH = Path(__file__).parent.parent.resolve() / "icons/"
DATA_PATH = Path(os.environ.get("PLATO_DATA_STORAGE_LOCATION"))


@exec_ui(display_name="Command",
         input_request=("y (continue) / n (abort)",),
         icons=(ICON_PATH / "command.svg", ICON_PATH / "command-selected.svg"))
def command_circle(
        num_cycles: int = 5,
        exposure_time: float = 0.2,
        elevation: float = 8.3,
        n_pos: int = 20,
        n_rows: int = 1500,
        reverse_order: bool = False,
        description: str = "Ambient. 1 atm. Reference circle at 8.3 deg of elevation",
):
    """ Command a circle of exposures around the optical axis at the given elevation.

    Args:
        - num_cycles: Number of exposures to acquire at each FOV position.
        - exposure_time: Exposure time [s].
        - elevation: Elevation angle [degrees].
        - n_pos: Number of positions on the circle.
        - n_rows: umber of CCD rows to read out around the source position.
        - reverse_order: Set to true if the observation should be performed in order of descending azimuth.
        - description: Description of the observation.
    """
    import camtest
    from camtest.commanding.cam_aat_050_ambient_circle import cam_aat_050_ambient_circle

    camtest.load_setup()
    camtest.execute(
        cam_aat_050_ambient_circle,
        num_cycles=num_cycles, exposure_time=exposure_time, elevation=elevation, n_pos=n_pos, n_rows=n_rows,
        reverse_order=reverse_order, description=description
    )


@exec_ui(display_name="Reduce",
         icons=(ICON_PATH / "reduce.svg", ICON_PATH / "reduce-selected.svg"))
def reduce_circle(
        data_dir: Directory = DATA_PATH / "obs",
        output_dir: Directory = DATA_PATH / "reduced",
        n_pos: int = 20,
        theta: float = 8.3,
        obsid: int = 3344,
        n_layers: int = 5,
        cube_selection: list = None,
        layer_selection: tuple = (1, 2, 3, 4),
        reverse_order: bool = False,
        verbose: bool = True,
):
    """ Reduction of a given "Circle" observation.

    Args:
        - data_dir: Folder where the input data is (usually the 'obs' folder).
        - output_dir: Folder where the reduction results will be stored.
        - n_pos: Number of positions on the circle.
        - theta: Elevation angle of the circle [degrees].
        - obsid: Obsid to reduce.
        - n_layers: Number of layers in data every cube.
        - cube_selection: Selection of cubes (= FITS files) to be reduced. Default = None = reduce all cubes.
        - layer_selection: Selection of layers to analyse in every cube. Default = None = analyse all images.
        - reverse_order: Default = False. Set to true if the observation was performed in order of descending azimuth.
        - verbose: Whether to print out verbose information.

    Returns:
        - Table with all results, also saved in FITS files.
    """
    import camtest.analysis.functions.fov_utils as fovu
    from camtest.analysis.functions.hartmann_utils import hartmann_reduction

    angles_in, angles_comm, fpcoords_comm, ccdrows, ccdcols, ccdcodes, ccdsides = fovu.coords_circle(
        n_pos=n_pos, theta=theta, distorted=True, reverse_order=reverse_order, verbose=verbose
    )

    data_dir = f"{str(data_dir)}/"  # make sure the folder name ends with a '/'
    output_dir = f"{str(output_dir)}/"  # make sure the folder name ends with a '/'

    ctab = hartmann_reduction(
        obsid=obsid, nlayers=n_layers, layer_selection=layer_selection, cube_selection=cube_selection,
        fov_angles=angles_in, datadir=data_dir, outputdir=output_dir, verbose=True)

    print(f"{ctab = }")

    return ctab


@exec_ui(display_name="Analyse", use_gui_app=True,
         icons=(ICON_PATH / "analysis.svg", ICON_PATH / "analysis-selected.svg"))
def analyse_circle(
        obsids: ListList([int, str, str], [900, "IAS", "IAS PFM"]),
        reduced_dir: Directory = DATA_PATH / "reduced",
        output_dir: Directory = DATA_PATH / "analysed/pngs/",
        n_sigma: float = 3.,
        meas_error: float = 5.,
        save: bool = True,
        verbose: bool = True
):
    """ Analysis of a given "Circle" observation (after the reduction thereoff).
    Args:
        - obsids : Obsids to analyse and how to label each of them in the plot. This is a list of lists:
          [obsid, site, plot_label], of types [int, str, str]
        - reduced_dir: Folder where the reduction results were be stored.
        - output_dir: Folder where the analysis results (png & txt file) will be stored.
        - n_sigma & meas_error: Define the tolerance to accept that 2 measurements are compatible within tolerance and
                                measurement uncertainty.  If meas_error is None, it is derived from the standard
                                deviation of the measurements (= assuming there's no systematic error on it, e.g. a
                                tilt).
        - save : If True, the PNG and txt file (quantitative results) are written to output_dir.
        - verbose: Whether to print out verbose information.

    Returns:
        - Current figure
        - Current axes  instance on the current figure
        - String matching the content of the output text file, as well as the series of print statements issued when
          verbose=True
    """

    import os
    import matplotlib.pyplot as plt
    from camtest.analysis.functions import hartmann_utils

    print(f"{os.getenv('PLATO_LOCAL_DATA_LOCATION') = }")

    reduced_dir = f"{str(reduced_dir)}/"  # make sure the folder name ends with a '/'
    output_dir = f"{str(output_dir)}/"  # make sure the folder name ends with a '/'

    setup = load_setup()
    print(f"{setup=}")

    plotname, resultstr = hartmann_utils.hartmann_analysis_circle(obsids, tau=None, datadir=reduced_dir,
                                                                  figname="Circle", verbose=verbose, radiusmm=None,
                                                                  setup=setup, n_sigma=n_sigma, meas_error=meas_error)

    if save:
        plt.savefig(Path(output_dir) / plotname)

        txtname = f"{plotname.split('.')[0]}.txt"

        with open(Path(output_dir) / txtname, "w") as file:
            file.write(resultstr)

        print(f"Hartman analysis:  plot  saved as {output_dir}/{plotname}")
        print(f"                  result saved as {output_dir}/{txtname}")

    return plt.gcf(), plt.gca(), resultstr
