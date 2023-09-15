from camtest.commanding import csl_gse, ias_gse, inta_gse, sron_gse
from camtest.core.exec import building_block
from egse import coordinates
from egse.fov import store_commanded_fov_position
from egse.state import GlobalState
from egse.coordinates import ccd_to_focal_plane_coordinates, focal_plane_coordinates_to_angles, \
    distorted_to_undistorted_focal_plane_coordinates


@building_block
def point_source_to_fov(theta=None, phi=None, wait=True):
    """ Position source on (theta, phi).

    Position the EGSE mechanisms such that the illuminated position is at the given angular distance from the optical
    axis (theta) and at the given angle from the x-axis of the focal plane (phi).

    Under the hood, this method calls the TH-specific implementation.  In test scripts, only this generic function
    should be used, not the TH-specific implementation.  It is determined from the loaded setup which site you are at.

    Args:
        - theta: Angular distance from the optical axis [degrees].
        - phi: Angle from the x-axis of the focal plane (i.e. in-field angle) [degrees].
        - wait: Whether or not to wait for the stages to reach the commanded positions.
    """
    site = GlobalState.setup.site_id

    sitehash = {
        "CSL": csl_gse.csl_point_source_to_fov,
        "CSL1": csl_gse.csl1_point_source_to_fov,
        "CSL2": csl_gse.csl2_point_source_to_fov,
        "IAS": ias_gse.ias_point_source_to_fov,
        "INTA": inta_gse.inta_point_source_to_fov,
        "SRON": sron_gse.sron_point_source_to_fov,
    }

    sitehash[site](theta=theta, phi=phi, wait=wait)

    store_commanded_fov_position(theta, phi)


@building_block
def point_source_to_fov_translation(theta=None, phi=None, translation_z=None, wait=True):
    """ Position source on (theta, phi).

    Position the EGSE mechanisms such that the illuminated position is at the given angular distance from the optical
    axis (theta) and at the given angle from the x-axis of the focal plane (phi).

    Under the hood, this method calls the TH-specific implementation.  In test scripts, only this generic function
    should be used, not the TH-specific implementation.  It is determined from the loaded setup which site you are at.

    Args:
        - theta: Angular distance from the optical axis [degrees].
        - phi: Angle from the x-axis of the focal plane (i.e. in-field angle) [degrees].
        - translation_z: translation_z: translation in mm along the vertical axis (positive goes up, negative goes down)
        - wait: Whether or not to wait for the stages to reach the commanded positions.
    """
    site = GlobalState.setup.site_id

    sitehash = {
        "CSL": csl_gse.csl_point_source_to_fov_translation,
        "CSL1": csl_gse.csl_point_source_to_fov_translation,
        "CSL2": csl_gse.csl_point_source_to_fov_translation,
        "IAS": ias_gse.ias_point_source_to_fov_translation,
        "INTA": inta_gse.inta_point_source_to_fov_translation,
        "SRON": sron_gse.sron_point_source_to_fov_translation,
    }

    sitehash[site](theta=theta, phi=phi, translation_z=translation_z, wait=wait)

    store_commanded_fov_position(theta, phi)

@building_block
def point_source_to_fp(x=None, y=None, wait=None) -> (float, float):
    """ Position source on (x,y).

    Position the EGSE mechanisms such that the illuminated position is at the given focal-plane coordinates.

    Under the hood, this method calls the TH-specific implementation.  In test scripts, only this generic function
    should be used, not the TH-specific implementation.  It is determined from the loaded setup which site you are at.

    Args:
        - x: Focal-plane x-coordinate to move to [mm].
        - y: Focal-plane y-coordinate to move to [mm].
        - wait: Whether or not to wait for the stages to reach the commanded positions.

    Returns:
        - theta: Angular distance from the optical axis [degrees].
        - phi: Angle from the x-axis of the focal plane (i.e. in-field angle) [degrees].
    """

    fov_setup = GlobalState.setup.camera.fov

    x_undistorted, y_undistorted = \
        coordinates.distorted_to_undistorted_focal_plane_coordinates(x, y, fov_setup.inverse_distortion_coefficients,
                                                                     fov_setup.focal_length_mm)
    theta, phi = coordinates.focal_plane_coordinates_to_angles(x_undistorted, y_undistorted)
    point_source_to_fov(theta=theta, phi=phi, wait=wait)   # Also stores the commanded position


@building_block
def point_source_to_ccd_coordinates(row=None, column=None, ccd_code=None, wait=None) -> (float, float):
    """ Position source on a given [ccd, row, col].

    Position the EGSE mechanisms such that the illuminated position is at the given CCD coordinates.

    Under the hood, this method calls the TH-specific implementation.  In test scripts, only this generic function
    should be used, not the TH-specific implementation.  It is determined from the loaded setup which site you are at.

    Args:
        - ccd: CCD identifier, in [1, 2, 3, 4]
        - row: CCD y-coordinate to move to [pixel], in [0,4509].
        - col: CCD x-coordinate to move to [pixel], in [0,4509] (no need to specify 'E' or 'F')
        - wait: Whether or not to wait for the stages to reach the commanded positions.

    Returns:
        - theta: Angular distance from the optical axis [degrees].
        - phi: Angle from the x-axis of the focal plane (i.e. in-field angle) [degrees].
    """

    # CCD --> Distorted Focal Plane
    xfp, yfp = ccd_to_focal_plane_coordinates(row, column, ccd_code)

    # Distorted --> Undistorted
    setup = GlobalState.setup
    inverse_distortion_coeffs = setup.camera.fov.inverse_distortion_coefficients
    focal_length_mm = setup.camera.fov.focal_length_mm
    x_undistorted, y_undistorted = distorted_to_undistorted_focal_plane_coordinates(xfp, yfp, inverse_distortion_coeffs,
                                                                                    focal_length=focal_length_mm)

    # Focal Plane --> FoV Angles
    theta, phi = focal_plane_coordinates_to_angles(x_undistorted, y_undistorted)

    # MGSE Movement
    point_source_to_fov(theta=theta, phi=phi, wait=wait)

    # Register position in the HK
    store_commanded_fov_position(theta, phi)


@building_block
def enable():
    """ Enable control of the camera rotation mechanism for pointing.
    If not None, the positions_lists parameter is a string (positions_lists="full" or positions_lists="single") and
    allows to specify which theta and phi lists are used (reference_single or reference_full_40).

    Under the hood, this method calls the TH-specific implementation.  In test scripts, only this generic function
    should be used, not the TH-specific implementation.  It is determined from the loaded setup which site you are at.
    """

    site = GlobalState.setup.site_id

    sitehash = {
        "CSL": csl_gse.csl_enable,
        "CSL1": csl_gse.csl_enable,
        "CSL2": csl_gse.csl_enable,
        "IAS": ias_gse.ias_enable,
        "INTA": inta_gse.inta_enable,
        "SRON": sron_gse.sron_enable,
    }

    sitehash[site]()


@building_block
def disable():
    """ Move the camera rotation mechanism to the equilibrium position and release the controller.

    When pointing is not needed (e.g during warm up phases), the camera rotation mechanisms is moved to the
    equilibrium position and the controller is released.

    Under the hood, this method calls the TH-specific implementation.  In test scripts, only this generic function
    should be used, not the TH-specific implementation.  It is determined from the loaded setup which site you are at.
    """

    site = GlobalState.setup.site_id

    sitehash = {
        "CSL": csl_gse.csl_disable,
        "CSL1": csl_gse.csl_disable,
        "CSL2": csl_gse.csl_disable,
        "IAS": ias_gse.ias_disable,
        "INTA": inta_gse.inta_disable,
        "SRON": sron_gse.sron_disable,
    }

    sitehash[site]()
