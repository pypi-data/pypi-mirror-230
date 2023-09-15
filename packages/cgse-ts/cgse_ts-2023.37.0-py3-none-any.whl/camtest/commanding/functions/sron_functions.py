"""
SRON specific functions

Version 1.0 20211202 First version
        2.0 20211215 fov_angles_to_gimbal_rotations, gimbal_rotations_to_fov_angles both accept scalar and array inputs

P. Royer
"""



import numpy as np

def fov_angles_to_gimbal_rotations(theta,phi):
    """
    fov_angles_to_gimbal_rotations(theta,phi)

    INPUT
    theta, phi : field angles = [elevation, azimuth]

    OUTPUT
    SRON gimbal rotation angles

    REF.
    Adapted from mgse.sron_point_source_to_fov (see PLATO-SRON-PL- PLATO CAM TVAC Gimbal Characterization Report draft)
    """
    phi = 180. - phi
    if isinstance(phi, float):
        if phi > 180:
            phi -= 360
    else:
        sel = np.where(phi > 180)
        phi[sel] = phi[sel] - 360

    theta, phi = np.deg2rad(theta), np.deg2rad(phi)

    gimbal_rx = np.rad2deg(np.arcsin(np.sin(phi) * np.sin(theta)))
    gimbal_ry = np.rad2deg(np.arctan(-1 * np.cos(phi) * np.tan(theta)))

    return gimbal_rx, gimbal_ry


def gimbal_rotations_to_fov_angles(rotx, roty):
    """
    gimbal_rotations_to_fov_angles(rotx, roty)

    INPUT
    rotx, roty : SRON gimbal rotation angles

    OUTPUT
    theta, phi : field angles = [elevation, azimuth]

    REF.
    Adapted from mgse.sron_point_source_to_fov (see PLATO-SRON-PL- PLATO CAM TVAC Gimbal Characterization Report draft)
    """

    tolerance = 1.e-5

    flag_scalar_input = False
    if isinstance(roty, float):
        rotx = np.array([rotx])
        roty = np.array([roty])
        flag_scalar_input = True

    rotx, roty = np.deg2rad(rotx), np.deg2rad(roty)

    theta = np.arccos(np.cos(rotx) * np.cos(roty))

    phi = np.zeros_like(roty)

    sel = np.where(np.abs(roty) < tolerance)
    phi[sel] = np.sign(rotx[sel]) * np.pi/2.

    sel = np.where(np.abs(roty) > tolerance)
    phi[sel] = np.arctan(np.sign(roty[sel]) * np.tan(rotx[sel]) / np.sin(roty[sel]))

    theta, phi = np.rad2deg(theta), np.rad2deg(phi)

    sel = np.where(roty<0.)
    phi[sel] = - 180. - phi[sel]

    sel = np.where(phi < -180)
    phi[sel] = phi[sel] + 360.

    if flag_scalar_input:
        theta, phi = theta[0], phi[0]

    return theta, phi



