import numpy as np
import camtest.analysis.convenience as cv
from camtest.commanding.functions.fov_test_geometry import circle_fov_geometry, sort_on_azimuth, fov_geometry_from_table
from egse.coordinates import ccd_to_focal_plane_coordinates, focal_plane_coordinates_to_angles
from camtest.commanding.functions.fov_test_geometry import plotCCDs


def coords_circle(n_pos=20, theta=8.3, distorted=True,  reverse_order=False, verbose=True):
    """

    INPUT
    n_pos=20 : number of positions visited along the circle.
               Must be a multiple of 4

    theta=8.3 : angle from the optical axis defining the circle

    distorted=True : if True the output coordinates include the optical distorsion

    reverse_order=False : if False, the circle is performed in increasing azimuth, from -180 to +180.
                          else it is performed in decreasing order of azimuth

    verbose : info and debug prints

    OUTPUT
    [angles_in, angles_comm, fpcoords_comm, ccdrows, ccdcols, ccdcodes, ccdsides]

    angles_in : computed FoV angles theta, undistorted
    angles_comm: FoV angles corresponding to the FPA commanding, i.e. incl. the optical distortions if requested
    fp_coords_comm: Focal Plane coordinates corresponding to angles_comm
    ccdrows, ccdcols : Rows and Columns on the CCD corresponding to fp_coords_comm
    ccdcodes, ccdsides : CCD (1,2,3,4) and CCD-side (E, F) identifiers corresponding to fp_coords_comm

    """
    if n_pos % 4:
        print(f"ERROR: n_pos must be a multiple of 4. {npos=}")
        return None

    ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig, anglesorig = \
        circle_fov_geometry(n=n_pos, radius=theta, offset=0.5, cam='n', distorted=distorted, verbose=verbose)

    angles_in, [ccdrows, ccdcols, ccdcodes, ccdsides] = sort_on_azimuth(anglesorig,
                                                                        [ccdrowsorig, ccdcolsorig, ccdcodesorig,
                                                                         ccdsidesorig],
                                                                        reverse=reverse_order)

    if verbose:
        print(" #          [theta, phi]       [row, col]         ccd_code  ccd_side")
        c = 0
        for angle, crow, ccol, cside, ccd_side in zip(angles_in, ccdrows, ccdcols, ccdcodes, ccdsides):
            print(
                f"{c:2d}   [{angle[0]:6.2f}, {angle[1]:6.2f}]   [{crow:7.2f}, {ccol:7.2f}]   {cside:1.0f}   {ccd_side}")
            c += 1

    fpcoords_comm = np.array(
        [ccd_to_focal_plane_coordinates(crow, ccol, ccode) for crow, ccol, ccode in zip(ccdrows, ccdcols, ccdcodes)])
    angles_comm = np.array(
        [focal_plane_coordinates_to_angles(xxfp, yyfp) for xxfp, yyfp in zip(fpcoords_comm[:, 0], fpcoords_comm[:, 1])])

    if verbose:
        try:
            pars_comm, circle_comm = cv.fitCircle(fpcoords_comm)
            cenx_comm, ceny_comm, radius_comm = pars_comm

            print()
            print(f"Circle center and radius, as commanded: [{cenx_comm:7.3f}, {ceny_comm:7.3f}], radius  {radius_comm:7.3f} [mm]")
        except:
            print(sys.exc_info())
            print("WARNING: error while fitting a circle to the focal plane coordinates")

        print()
        print("Output values: angles_undistorted, angles_commanded, fpcoords_commanded, ccdrows, ccdcols, ccdcodes, ccdsides")

    return [angles_in, angles_comm, fpcoords_comm, ccdrows, ccdcols, ccdcodes, ccdsides]



def coords_from_table(table_name="reference_full_40", use_angles=False, distorted_input=True, distorted_output=True, sort_fov_pos_in_azimuth=False,  reverse_order=False, verbose=True):
    """

    INPUT
    table_name : setup table from where the FoV positions should be extracted.
                  Typically setup.fov_positions.reference_full_40

    use_angles : Assuming that the input table has 4 keys and that these correspond to 2 sets of data:
                ['theta', 'phi', 'x', 'y']
                    ['theta', 'phi'] are computed FoV angles. To read those: use_angles = True
                    ['x','y']        are measured FP coordinates. To read those: use_angles = False

    distorted_input:
                if True, the optical distortion is "undone" prior to the computation. Use this with use_angles=False
                if False, it is assumed that the input FoV angles on input are un-distorted. Use with use_angles=True

    distorted_output=True : if True the output coordinates include the optical distorsion

    reverse_order=False : if False, the circle is performed in increasing azimuth, from -180 to +180.
                          else it is performed in decreasing order of azimuth

    sort_fov_pos_in_azimuth : if True, the FoV positions will be sorted in azimuth

    verbose : info and debug prints

    OUTPUT
    [angles_in, angles_comm, fpcoords_comm, ccdrows, ccdcols, ccdcodes, ccdsides]

    angles_in : computed FoV angles theta, undistorted
    angles_comm: FoV angles corresponding to the FPA commanding, i.e. incl. the optical distortions if requested
    fp_coords_comm: Focal Plane coordinates corresponding to angles_comm
    ccdrows, ccdcols : Rows and Columns on the CCD corresponding to fp_coords_comm
    ccdcodes, ccdsides : CCD (1,2,3,4) and CCD-side (E, F) identifiers corresponding to fp_coords_comm


    USAGE

    The commanding is based upon computed FoV angles, i.e. analysis of data obtained with use_angles=True:

    [angles_in, angles_comm, fpcoords_comm, ccdrows, ccdcols, ccdcodes, ccdsides] =
    coords_from_table(table_name="reference_full_40", use_angles=True, distorted_input=False, distorted_output=True, sort_fov_pos_in_azimuth=True,  reverse_order=False, verbose=True)


    The commanding is based upon measured focal plane coordinates, i.e. analysis of data obtained with use_angles=False:

    [angles_in, angles_comm, fpcoords_comm, ccdrows, ccdcols, ccdcodes, ccdsides] =
    coords_from_table(table_name="reference_full_40", use_angles=False, distorted_input=True, distorted_output=True, sort_fov_pos_in_azimuth=False,  reverse_order=False, verbose=True)
    """

    ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig, anglesorig = fov_geometry_from_table(distorted=distorted_output, distorted_input=distorted_input, table_name=table_name, use_angles=use_angles, verbose=verbose)

    if sort_fov_pos_in_azimuth:
        angles_in, [ccdrows, ccdcols, ccdcodes, ccdsides] = sort_on_azimuth(anglesorig,[ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig],reverse=reverse_order)
    else:
        angles_in, ccdrows, ccdcols, ccdcodes, ccdsides = anglesorig, ccdrowsorig, ccdcolsorig, ccdcodesorig, ccdsidesorig

    if verbose:
        print(" #          [theta, phi]       [row, col]         ccd_code  ccd_side")
        c = 0
        for angle, crow, ccol, ccode, ccd_side in zip(angles_in, ccdrows, ccdcols, ccdcodes, ccdsides):
            print(
                f"{c:2d}   [{angle[0]:6.2f}, {angle[1]:6.2f}]   [{crow:7.2f}, {ccol:7.2f}]   {ccode:1.0f}   {ccd_side}")
            c += 1

    fpcoords_comm = np.array([ccd_to_focal_plane_coordinates(crow, ccol, ccode) for crow, ccol, ccode in zip(ccdrows, ccdcols, ccdcodes)])
    angles_comm   = np.array([focal_plane_coordinates_to_angles(xxfp, yyfp) for xxfp, yyfp in zip(fpcoords_comm[:, 0], fpcoords_comm[:, 1])])

    if verbose:
        import matplotlib.pyplot as plt
        plotCCDs(figname="FoV") #,setup=setup)
        plt.plot(fpcoords_comm[:,0], fpcoords_comm[:,1], 'ro-')

        print()
        print("Output values: angles_undistorted, angles_commanded, fpcoords_commanded, ccdrows, ccdcols, ccdcodes, ccdsides")

    return [angles_in, angles_comm, fpcoords_comm, ccdrows, ccdcols, ccdcodes, ccdsides]

