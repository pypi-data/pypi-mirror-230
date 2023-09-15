import numpy as np
from camtest.commanding import ogse, dpu
from camtest.commanding.csl_gse import check_and_move_relative_user
from camtest.core.exec import building_block
from camtest import GlobalState


def hex_positions_match(hexapod, hexsim, atol=0.0001, rtol=0.0001):
    """
    hexapod : hexapod hardware
    hexsim  : hexapod simulator

    atol, rtol : parameters from numpy.allclose, used to compare the hexapod coordinate readback between hardware and simulator
    """
    return np.allclose(hexapod.get_user_positions(), hexsim.get_user_positions(), atol=atol, rtol=rtol)


def hex_is_model_sync(model, hexhw, verbose=None, rounding=4, atol=0.0001, rtol=0.0001):
    """
    cslmodel : Reference Frame Model: dictonary with the definitions of all reference frames

    hexhw    : hexapod hardware

    rounding : rounding parameter, for display purposes only

    atol, rtol : parameters from numpy.allclose, used to compare the hexapod coordiates readback with the reference frame model
    """

    coohex = hexhw.get_user_positions()
    coomodtr, coomodrot = model.get_frame('hexusr').getActiveTranslationRotationVectorsTo(model.get_frame('hexobj'))
    coomod = np.concatenate([coomodtr, coomodrot])

    if verbose or (verbose is None):
        if verbose is None: verbose = ""

        print(f"{verbose}Hexapod   : {np.round(coohex, rounding)}")
        print(f"{verbose}Model     : {np.round(coomod, rounding)}")
        print(f"{verbose}Diff      : {np.round(coohex - coomod, rounding)}")

        print(f"{verbose}In synch  : {np.allclose(coohex, coomod, atol=atol, rtol=rtol)}")

    return np.allclose(coohex, coomod, atol=atol, rtol=rtol)


def hex_positions(hexapod, rounding=3):
    """
    Print User and machine coordinates of the input Hexapod

    Parameters
    ----------
    hexapod : Hexapod

    Returns
    -------
    None

    """
    print(f"OBJ vs USR: {np.round(hexapod.get_user_positions(), rounding)}")
    print(f"PLT vs MEC: {np.round(hexapod.get_machine_positions(), rounding)}")
    return


def csl_model_from_file(filename=None, location=None, setup=None, verbose=True):
    """
    csl_model_from_file(filename=None, location=None, setup=None, verbose=True)

    INPUTS
    filename : CSL METROLOGY ('output excel file')

    location : directory of filename. Default = env. variable "PLATO_CONF_DATA_LOCATION"

    setup : default = GlobalState.setup

    """
    import os
    from camtest import GlobalState
    from egse.coordinates.cslmodel import CSLReferenceFrameModel
    from egse.coordinates.refmodel import print_vectors
    from egse.coordinates.laser_tracker_to_dict import laser_tracker_to_dict

    if location is None:
        location = os.getenv("PLATO_CONF_DATA_LOCATION")

    if setup is None:
        setup = GlobalState.setup

    ###############################################################################
    #
    # PREDEFINED REFERENCES
    #
    ###############################################################################

    ## TODO : CAST THESE IN A CONFIG FILE ?

    # Every ref. frame is attached to a "reference" reference frame
    # Those references are not mentioned in the excel sheet, they must be pre-existing in the setup
    # This section sets it for all reference frames present in the

    # All ReferenceFrames measured or defined in CSL, i.e. all in the excelll sheet are expressed wrt gliso
    predef_refs = {}
    predef_refs['Master'] = 'Master'

    # CSL GSE
    predef_refs['gliso'] = 'Master'  # csl
    # predef_refs['glfix'] = 'glrot'
    # predef_refs['glrot'] = 'gliso'

    # HEXAPOD
    predef_refs['hexiso'] = 'gliso'  # csl (originally hex_mec)
    # predef_refs['hexmec'] = 'hexiso'
    # predef_refs['hexplt'] = 'hexiso'
    # predef_refs['hexobj'] = 'hexplt'
    # predef_refs['hexusr'] = 'hexmec'
    # predef_refs['hexobusr'] = 'hexusr'

    # FPA
    predef_refs['fpaaln'] = 'gliso'  # csl
    predef_refs['fpamec'] = 'gliso'  # csl
    predef_refs['fpasen'] = 'gliso'  # csl

    # TOU
    predef_refs['toumec'] = 'gliso'  # csl
    predef_refs['toualn'] = 'gliso'  # csl
    predef_refs['touopt'] = 'gliso'  # csl
    predef_refs['touint'] = 'gliso'  # csl
    predef_refs['toul6'] = 'gliso'  # csl

    #predef_refs['toubip'] = 'gliso'  #
    predef_refs['bipmec'] = 'gliso'  # csl
    predef_refs['bipint'] = 'gliso'  # csl
    predef_refs['bolt'] = 'gliso'  # csl

    # CAMERA
    predef_refs['camint'] = 'gliso'  # csl
    predef_refs['marialn'] = 'gliso'  # tbd
    predef_refs['cambor'] = 'toualn' # tbd

    # HARTMANN PLANE
    predef_refs['hartmann'] = 'gliso'  # csl

    setup.csl_model = {}
    setup.csl_model.default_refs = predef_refs

    ###############################################################################
    #
    # LOAD XLS FILE & ASSEMBLE CSLREFERENCEFRAMEMODEL
    #
    ###############################################################################

    filexls = location + '/' + filename

    # Read the excel file
    refFrames = laser_tracker_to_dict(filexls, setup)  # -> dict

    # for k,v in zip(refFrames.keys(), refFrames.values()):
    #    print(f"{k:>10} -- {v.split('|')[-3]}[{v.split('|')[-2]}]")

    # Assemble the model
    model = CSLReferenceFrameModel(refFrames)

    # CHECK. At this stage, the ref. frames from the excel sheet are in the model, but only those.
    # The frames have the proper reference, but not links
    if verbose:
        print("CSL MODEL : XLS SHEET")
        print(model.summary())

    ###############################################################################
    #
    # COMPLETE THE MODEL
    #
    ###############################################################################

    zeros = [0, 0, 0]

    # HEX_MEC
    model.add_frame(name="hexmec", translation=zeros, rotation=zeros, ref="hexiso")

    # HEX_PLT --> HEX_MEC -- no link
    model.add_frame(name="hexplt", translation=zeros, rotation=zeros, ref="hexmec")

    # HEX_USR --> HEX_MEC
    transformation = model.get_frame("hexmec").getActiveTransformationTo(model.get_frame("toul6"))
    model.add_frame(name="hexusr", transformation=transformation, ref="hexmec")

    # HEX_OBJ == FPA_SEN--> HEX_PLT
    transformation = model.get_frame("hexplt").getActiveTransformationTo(model.get_frame("fpasen"))
    model.add_frame(name="hexobj", transformation=transformation, ref="hexplt")

    # HEX_OBUSR
    transformation = model.get_frame("hexusr").getActiveTransformationTo(model.get_frame("hexobj"))
    model.add_frame(name="hexobusr", transformation=transformation, ref="hexusr")

    # TODO: DEFINE MARI_ALN (CAM_BOR, TBD)

    # CHECK. At this stage, ALL ref. frames must be in the model.
    # The frames have the proper reference, but not links
    if verbose:
        print("CSL MODEL : ALL FRAMES")
        print(model.summary())

    ###############################################################################
    #
    # INCLUDE THE LINKS
    #
    ###############################################################################

    model.add_link("Master", "gliso")

    # # HEXAPOD
    model.add_link("hexiso", "gliso")
    model.add_link("hexmec", "hexiso")
    model.add_link("hexobj", "hexplt", )
    model.add_link("hexobj", "hexobusr")
    model.add_link("hexusr", "hexmec")

    model.add_link("fpasen", "hexobj", )
    model.add_link("fpasen", "fpamec")
    model.add_link("fpamec", "fpaaln")

    model.add_link("toul6", "hexusr")
    model.add_link("toul6", "toumec")
    model.add_link("toumec", "gliso")
    model.add_link("toumec", "toualn")
    model.add_link("touopt", "toualn")
    model.add_link("touint", "toualn")
    #model.add_link("toubip", "toumec")
    model.add_link("bipmec", "toumec")
    model.add_link("bipint", "toumec")

    model.add_link("bolt", "toumec")
    model.add_link("hartmann", "toumec")

    model.add_link("camint", "toumec")

    if verbose:
        print("CSL MODEL : COMPLETE")
        print(model.summary())

    ###############################################################################
    #
    # SANITY CHECK & CROSS CHECK WITH LASER TRACKER SOFTWARE
    #
    ###############################################################################

    if verbose:
        print("CSL REFERENCE FRAME -- SANITY CHECKS")
        print()
        print("Checks for the alignment procedure")
        print_vectors('hexmec', 'toul6', model=model)
        print_vectors('hexmec', 'fpasen', model=model)
        print_vectors('hexmec', 'bipint', model=model)
        print()
        print("Upwards progression")
        print_vectors('gliso', 'hexiso', model=model)
        print_vectors('hexiso', 'hexmec', model=model)
        print_vectors('hexmec', 'hexobj', model=model)
        print_vectors('hexobj', 'fpasen', model=model)
        print_vectors('fpasen', 'bipint', model=model)
        print_vectors('bipint', 'toul6', model=model)
        print()
        print("Rotations")
        print_vectors('toumec', 'toualn', model=model)
        print_vectors('toumec', 'touopt', model=model)
        print_vectors('toumec', 'camint', model=model)
        print_vectors('bipmec', 'bipint', model=model)
        print_vectors('touopt', 'touint', model=model)
        print_vectors('touint', 'camint', model=model)
        print_vectors('bipint', 'touint', model=model)
        print()
        print("Various")
        print_vectors('hexobj', 'hexobusr', model=model)
        print_vectors('bipint', 'bolt', model=model)
        print()
        print("Basic checks from the model")
        print_vectors('gliso', 'fpasen', model=model)
        print_vectors('gliso', 'toul6', model=model)
        print_vectors('gliso', 'bipint', model=model)
        print()
        print("For more, use: print_vectors, e.g.  print_vectors('gliso', 'toumec', model=model)")

    ###############################################################################
    #
    # RETURN THE MODEL AND THE UPDATED SETUP
    #
    ###############################################################################

    csl_dict = model.serialize()

    setup.csl_model.model = csl_dict

    return model, setup


def prepare_hexapod(model=None, setup=None):
    """
    prepare_hexapod(model=None, setup=None)

    . Connect to the hexapod (or generate an hexapod simulator)
    . Configure it with the input model

    INPUT :
        model = CSLReferenceFrameModel, e.g. created with csl_model_from_file
        setup = setup. Default = GlobalState.setup

        The two inputs are redundant. If both are given, the model is preferred.

    OUTPUT :
        hexapod = hardware if available, else PunaSimulator
    """
    import numpy as np
    from camtest.commanding.csl_gse import is_model_sync, hex_positions
    from egse.hexapod.symetrie.puna import HexapodError
    from egse.hexapod.symetrie.puna import PunaProxy
    from egse.hexapod.symetrie.puna import PunaSimulator
    from egse.coordinates.cslmodel import CSLReferenceFrameModel
    from egse.coordinates.refmodel import print_vectors

    ###############################################################################
    #
    # CONNECT TO HEXAPOD
    #
    ###############################################################################
    try:
        hexhw = PunaProxy()
        hexhw.info()
    except HexapodError:
        hexhw = PunaSimulator()
    except NotImplementedError:
        hexhw = PunaSimulator()

    hexhash = {False: "CONNECTED TO REAL HARDWARE", True: "A SIMULATOR"}
    print(f"The hexapod is : {hexhash[hexhw.is_simulator()]}")

    ###############################################################################
    #
    # Use the input model, else extract it from the setup
    #
    ###############################################################################

    if model is None:

        if setup is None:
            setup = GlobalState.setup

        refFrames = setup.csl_model.model
        model = CSLReferenceFrameModel(refFrames)

    ###############################################################################
    #
    # CONFIGURE HEX_USR WRT THE MEASURED POSITION OF TOU L6S2 (Laser Tracker)
    #
    ###############################################################################

    usrtrans, usrrot = model.get_frame("hexmec").getActiveTranslationRotationVectorsTo(model.get_frame("hexusr"))
    objtrans, objrot = model.get_frame("hexplt").getActiveTranslationRotationVectorsTo(model.get_frame("hexobj"))

    rounding = 6
    usrtrans = np.round(usrtrans, rounding)
    usrrot = np.round(usrrot, rounding)
    objtrans = np.round(objtrans, rounding)
    objrot = np.round(objrot, rounding)

    hexhw.configure_coordinates_systems(*usrtrans, *usrrot, *objtrans, *objrot)

    ###############################################################################
    #
    # VERIFY THE MATCH BETWEEN MODEL AND HARDWARE
    #
    ###############################################################################
    print("Positions from the Hexapod")
    hex_positions(hexhw, rounding=4)

    print()
    print("Positions from the Model")
    print_vectors('hexusr', 'hexobj', model)
    print_vectors('hexmec', 'hexplt', model)

    print()
    if is_model_sync(model, hexhw):
        print()
        print("MODEL & HW in SYNC. READY TO PROCEED.")
    else:
        print()
        print("CRITICAL: MODEL & HW OUT OF SYNC. IF THE DIFFERENCE IS OUT OF SAFETY MARGINS, "
              "BRING THE HEXAPOD TO REFERENCE (ZERO-)POSITION AND RERUN THIS.")

    return hexhw


@building_block
def focus_sweep(zvalues=None, ogse_attenuations=None, exposure_times=None, n_fee_parameters=None, cslmodel=None,
                setup=None, verbose=True):
    """
    PRECONDITION -- INITIAL STATE:
    - N-FEEs in Dump mode
    - Mechanisms:
        . camera in field position
        . FPA in focus-sweep starting position

    focus_sweep(zvalues=None, ogse_attenuations=None, exposure_times=None, n_fee_parameters=None)

    POST-EXECUTION STATE
    - N-FEEs in Dump mode (ccd_order & ccd_side as specified for the present building-block)
    - Mechanisms:
        . camera in same field position as initially
        . FPA in focus-sweeps ending position

    INPUT

    zvalues = list or numpy array of z-positions. Does not have to be equidistant
              Used to compute the sequential list of delta-z translations to be applied.

    ogse_attenuations = list of ogse attenuation factors.
                        list or numpy array, with the same length as zvalues

    exposure_times = list of exposure times [seconds]
                     list or numpy array, with the same length as zvalues

    n_fee_parameters = fixed n_fee configuration parameters for n_cam_partial_int_sync (except exposure_times)
                    num_cycles  : nb of images / delta_z
                    row_start, row_end, col_end, : partial readout parameters
                    rows_final_dump : final clearout
                    ccd_order, ccd_side : selection of half-ccd.
                                          Also used to configure the n_fee_to_dump at the end

    cslmodel = Reference Frame model (dictonary of ReferenceFrame definitions)
               Used to verify that all movements obey the avoidance volumes

    setup = GlobalState.setup -- optional -- passing it shortens the execution time of the hexapod movements

    verbose : triggers some verbose prints

    """

    if setup is None:
        setup = GlobalState.setup

    # Delta_z
    delta_zs = np.diff(np.array(zvalues))

    # No rotation is applied during the focus sweep (pure delta-z)
    rotation = [0., 0., 0.]

    # Number of cycles will be made different wrt the execution of OGSE filter-wheel movements or not
    num_cycles = n_fee_parameters.pop("num_cyles")

    # ACQUISITION AT INITIAL POSITION
    #################################

    # OGSE Intensity
    ogse.set_fwc_fraction(fwc_fraction=ogse_attenuations[0])
    # Acquisition
    dpu.n_cam_partial_int_sync(num_cycles=num_cycles, **n_fee_parameters, exposure_time=exposure_times[0])

    # FOCUS SWEEP
    #############
    for i, delta_z in enumerate(delta_zs):

        # Re-position the FPA / Hexapod
        translation = [0., 0., delta_z]
        check_and_move_relative_user(cslmodel=cslmodel, translation=translation, rotation=rotation, setup=setup,
                                     verbose=verbose)

        # OGSE Intensity
        if ogse_attenuations[i] != ogse_attenuations[i - 1]:
            ogse.set_fwc_fraction(fwc_fraction=ogse_attenuations[i])
            ogse_cycle = 1
        else:
            ogse_cycle = 0

        # Acquisition
        dpu.n_cam_partial_int_sync(num_cycles=num_cycles + ogse_cycle, **n_fee_parameters,
                                   exposure_time=exposure_times[i])
