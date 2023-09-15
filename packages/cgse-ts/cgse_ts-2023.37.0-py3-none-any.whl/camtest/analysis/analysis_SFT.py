import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from camtest.analysis import convenience as cv
from camtest import load_setup
from camtest.analysis.observation import Observation

def addstring(sref, s, verbose=True):
    """
    adds s to sref
    if verbose is True, prints s
    """
    sref = sref + s+'\n'
    if verbose: print(s)
    return sref

def analysis_SFT_HK(obsid, camera=None, data_dir=None, output_dir=None, setup=None, verbose=True, showplots=True):
    """
    obsid : obsid
    camera : camera ID, as in the data directory name ("achel", "brigand", "chimay", ..._
             default : setup.camera.ID
    data_dir : full path to the "/obs/" directory above the obsid-directory
    output_dir  : ouput directory (for both images & text file)
    setup : setup object
    verbose : boolean, triggers print statements
    showplots : displays the plots during the execution, or saves them without display
    """
    # BASIC VARIABLE DECLARATIONS
    lightgray = (0.75, 0.75, 0.75)
    lightblue = (0.5, 0.5, 1.0)
    stringout = ""
    sobsid = str(obsid).zfill(5)

    # NFEE MODES DEFINITIONS
    hmode = {"ON":0, "ON_MODE":0, "STANDBY_MODE":4, "STANDBY":4, "FULL_IMAGE":5, "FULL_IMAGE_MODE":5}

    # DEFAULTS FROM THE SETUP
    if setup is None:
        setup = load_setup()

    if camera is None:
        camera = setup.camera.ID

    # OBSERVATION OBJECT
    if data_dir is None:
        # if PLATO_LOCAL_DATA_LOCATION is defined; else set datadir to "/.../obs/"
        obs = Observation(obsid=obsid, data_dir=None)
    else:
        # if PLATO_LOCAL_DATA_LOCATION is defined; else set datadir to "/.../obs/"
        obs = Observation(obsid=obsid, data_dir=data_dir)

    # FRAME TIMES
    # If frames exist, start of image acquisition = t0 = first frame time = start of readout of the first frame.
    # Else t0 = start of the N-FEE-HK
    try:
        ftimes = obs.get_frame_times()
        t0 = ftimes[0]
        relftimes = ftimes-t0
        hkonly = False
    except:
        hkonly = True

    #########
    # NFEE-HK
    #########
    device = "N-FEE-HK"

    hkn = obs.get_hk(device=device, verbose=False)

    if hkonly:
        t0 = hkn["finetime"][0]

    nreltime = hkn["finetime"] - t0
    dtn = np.diff(nreltime)

    nfeemode = hkn["NFEE_MODE"]

    ########
    # AEU HK
    ########
    device = "AEU-CRIO"

    hkt = obs.get_hk(device=device, verbose=False)

    reltime = hkt["finetime"]-t0


    ##################
    # TEST SEQUENCING
    ##################
    # Extracting the time periods where the NFEE is ON, STANDBY, DUMP, FULL_IMAGE
    # DUMP cannot be extracted from the csv telemetry at the moment (see ticket plato-common-egse #2532).
    # It could be FULL_IMAGE when not measuring, but it's actually not used.

    # Start of ON-MODE
    t_on = nreltime[:-1][np.where(dtn < 7.)[0][0]]

    # End of the test
    t_end = max(reltime[-1], nreltime[-1])

    try:
        # Start of STANDBY-MODE
        t_stdby = nreltime[np.where(nfeemode == hmode["STANDBY"])[0][0]]
        reach_stdby = True
    except:
        reach_stdby = False
        t_stdby = t_end
    try:
        # Start of FULL-IMAGE-MODE (dump)
        t_full = nreltime[np.where(nfeemode == hmode["FULL_IMAGE"])[0][0]]
        reach_full = True
    except:
        reach_full = False
        t_full = t_end

    ###############################
    # LOAD TM LIMITS FROM THE SETUP
    ###############################

    v_keys = ["GAEU_V_CCD_NFEE", "GAEU_V_AN1_NFEE", "GAEU_V_AN2_NFEE", "GAEU_V_AN3_NFEE", "GAEU_V_CLK_NFEE", "GAEU_V_DIG_NFEE"]
    vn_keys = ["NFEE_VCCD", "NFEE_VAN1_R", "NFEE_VAN2_R", "NFEE_VAN3_R", "NFEE_VCLK_R", "NFEE_VDIG"]

    i_keys = ["GAEU_I_CCD_NFEE", "GAEU_I_AN1_NFEE", "GAEU_I_AN2_NFEE", "GAEU_I_AN3_NFEE", "GAEU_I_CLK_NFEE", "GAEU_I_DIG_NFEE"]

    limits = {}

    vtol_type = setup.camera.fee.power_consumption.voltages.tolerance
    if vtol_type == "absolute":
        for v_key in v_keys:
            ref = setup.camera.fee.power_consumption.voltages[v_key]
            limits[v_key] = [ref[0]-ref[1], ref[0]+ref[1]]
    elif vtol_type == "relative":
        for v_key in v_keys:
            ref = setup.camera.fee.power_consumption.voltages[v_key]
            limits[v_key] = [ref[0]*(1-ref[1]/100.), ref[0] * (1+ref[1]/100.)]

    itol_type = setup.camera.fee.power_consumption.currents.tolerance
    if itol_type == "relative":
        for i_key in i_keys:
            limits[i_key] = {}
            for feemode in ["on_mode", "standby_mode", "full_image_mode_readout", "full_image_mode_integration"]:
                ref = setup.camera.fee.power_consumption.currents[feemode][i_key]
                limits[i_key][feemode] = [(ref[0]*(1-ref[1]/100.)) / 1000., (ref[0] * (1+ref[1]/100.)) / 1000.]
    else:
            print("Setup indicates an absolute error specification for the current")
            raise(NotImplementedError)

    ##################
    # TM STATS / FEE MODE
    ##################

    hok = {True: " OK", False: "NOK"}

    ### ON MODE  ###
    s = "NFEE ON-MODE"
    stringout = addstring(stringout, s, verbose=verbose)

    feemode = 'on_mode'
    tsel = np.where((reltime>=t_on) & (reltime <=t_stdby))
    tnsel = np.where((nreltime>=t_on) & (nreltime <=t_stdby))

    allvok, allvnok, alliok = True, True, True
    for v_key,vn_key, i_key in zip(v_keys, vn_keys, i_keys):
        V = np.mean(hkt[v_key][tsel])
        I = np.mean(hkt[i_key][tsel])
        Vn = np.mean(hkn[vn_key][tnsel])

        vlow, vhigh = limits[v_key][0], limits[v_key][1]
        if vlow > vhigh:
            vlow, vhigh = limits[v_key][1], limits[v_key][0]

        ilow, ihigh = limits[i_key][feemode][0], limits[i_key][feemode][1]
        if ilow > ihigh:
            ilow, ihigh = limits[i_key][feemode][1], limits[i_key][feemode][0]

        #s = f"      {v_key:15s} {V:7.3f} in [{vlow:7.3f},{vhigh:7.3f}] {hok[(V >= vlow) & (V <= vhigh)]}      {i_key:15s} {I:7.3f} in [{ilow:7.3f},{ihigh:7.3f}] {hok[(I >= ilow) & (I <= ihigh)]}       P=V*I {V * I:7.3f}"
        s = f"      {v_key:15s} {V:7.3f} in [{vlow:7.3f},{vhigh:7.3f}] {hok[(V >= vlow) & (V <= vhigh)]}      {vn_key:15s} {Vn:7.3f} in [{vlow:7.3f},{vhigh:7.3f}] {hok[(Vn >= vlow) & (Vn <= vhigh)]}      {i_key:15s} {I:7.3f} in [{ilow:7.3f},{ihigh:7.3f}] {hok[(I >= ilow) & (I <= ihigh)]}       P=V*I {V * I:7.3f}"
        stringout = addstring(stringout, s, verbose=verbose)

        if (V<vlow) | (V>vhigh): allvok = False
        if (I<ilow) | (I>ihigh): alliok = False
        if (Vn<vlow) | (Vn>vhigh): allvnok = False

    s = f"      AEU Voltages OK: {str(allvok):5s} {' ' * 24}       FEE Voltages OK: {str(allvnok):5s} {' ' * 30} Currents OK: {alliok}"
    stringout = addstring(stringout, s, verbose = verbose)

    ### STANDBY MODE  ###
    if reach_stdby:
        s = "NFEE STANDBY-MODE"
        stringout = addstring(stringout, s, verbose=verbose)

        feemode = "standby_mode"
        tsel = np.where((reltime >= t_stdby) & (reltime <= t_full))
        tnsel = np.where((nreltime >= t_stdby) & (nreltime <= t_full))

        allvok, allvnok, alliok = True, True, True
        for v_key, vn_key, i_key in zip(v_keys, vn_keys, i_keys):
            V = np.mean(hkt[v_key][tsel])
            I = np.mean(hkt[i_key][tsel])
            Vn = np.mean(hkn[vn_key][tnsel])

            vlow, vhigh = limits[v_key][0], limits[v_key][1]
            if vlow > vhigh:
                vlow, vhigh = limits[v_key][1], limits[v_key][0]

            ilow, ihigh = limits[i_key][feemode][0], limits[i_key][feemode][1]
            if ilow > ihigh:
                ilow, ihigh = limits[i_key][feemode][1], limits[i_key][feemode][0]

            #s = f"      {v_key:15s} {V:7.3f} in [{vlow:7.3f},{vhigh:7.3f}] {hok[(V>=vlow) & (V<=vhigh)]}      {i_key:15s} {I:7.3f} in [{ilow:7.3f},{ihigh:7.3f}] {hok[(I>=ilow) & (I<=ihigh)]}       P=V*I {V*I:7.3f}"
            s = f"      {v_key:15s} {V:7.3f} in [{vlow:7.3f},{vhigh:7.3f}] {hok[(V >= vlow) & (V <= vhigh)]}      {vn_key:15s} {Vn:7.3f} in [{vlow:7.3f},{vhigh:7.3f}] {hok[(Vn >= vlow) & (Vn <= vhigh)]}      {i_key:15s} {I:7.3f} in [{ilow:7.3f},{ihigh:7.3f}] {hok[(I >= ilow) & (I <= ihigh)]}       P=V*I {V * I:7.3f}"
            stringout = addstring(stringout, s, verbose=verbose)

            if (V<vlow) | (V>vhigh): allvok = False
            if (I<ilow) | (I>ihigh): alliok = False
            if (Vn<vlow) | (Vn>vhigh): allvnok = False

        s = f"      AEU Voltages OK: {str(allvok):5s} {' ' * 24}       FEE Voltages OK: {str(allvnok):5s} {' ' * 30} Currents OK: {alliok}"
        stringout = addstring(stringout, s, verbose=verbose)

    ######################################
    ### FULL_IMAGE_MODE - ACQUISITION  ###
    ######################################
    if reach_full:
        # = excluding the initial & ending period in DUMP MODE
        tsel = np.where((reltime >= 0.) & (reltime <= t_end))
        tnsel = np.where((nreltime >= 0.) & (nreltime <= t_end))

        # 1. identify modes
        i_key = "GAEU_I_CLK_NFEE"
        current = hkt[i_key][tsel]
        try:
            modes = cv.kde_modes(current, bw_method=0.1, kde_threshold=None, verbose=False)
        except:
            s = "WARNING : NO BIMODAL DISTRIBUTION OF CURRENT IDENTIFIED IN FULL_IMAGE_MODE"
            stringout = addstring(stringout, s, verbose=verbose)

            modes = [np.arange(len(current))]

        if len(modes)!=2:
            s = f"WARNING : CURRENT DOES NOT EXHIBIT A BIMODAL DISTRIBUTION IN FULL_IMAGE_MODE: nmodes = {len(modes)}"
            stringout = addstring(stringout, s, verbose=verbose)

        # 2. map the modes to readout or integration
        modes_i = np.array([np.mean(current[mode]) for mode in modes])
        hmodes = {}
        hmodes['full_image_mode_readout'] = modes[np.where(modes_i == max(modes_i))[0][0]]
        hmodes['full_image_mode_integration'] = modes[np.where(modes_i == min(modes_i))[0][0]]

        # 3. Apply to all
        hfeemode = {'full_image_mode_readout':"FULL_IMAGE_MODE_READOUT", 'full_image_mode_integration':"FULL_IMAGE_MODE_INTEGRATION"}
        for feemode in ['full_image_mode_integration', 'full_image_mode_readout']:
            s = f"{hfeemode[feemode]}"
            stringout = addstring(stringout, s, verbose=verbose)

            allvok, allvnok, alliok = True, True, True
            for v_key, vn_key, i_key in zip(v_keys, vn_keys, i_keys):
                V = np.mean(hkt[v_key][tsel][hmodes[feemode]])
                I = np.mean(hkt[i_key][tsel][hmodes[feemode]])
                Vn = np.mean(hkn[vn_key][tnsel])

                vlow, vhigh = limits[v_key][0], limits[v_key][1]
                if vlow > vhigh:
                    vlow, vhigh = limits[v_key][1], limits[v_key][0]

                ilow, ihigh = limits[i_key][feemode][0], limits[i_key][feemode][1]
                if ilow > ihigh:
                    ilow, ihigh = limits[i_key][feemode][1], limits[i_key][feemode][0]

                #s = f"      {v_key:15s} {V:7.3f} in [{vlow:7.3f},{vhigh:7.3f}] {hok[(V>=vlow) & (V<=vhigh)]}      {i_key:15s} {I:7.3f} in [{ilow:7.3f},{ihigh:7.3f}] {hok[(I>=ilow) & (I<=ihigh)]}       P=V*I {V*I:7.3f}"
                s = f"      {v_key:15s} {V:7.3f} in [{vlow:7.3f},{vhigh:7.3f}] {hok[(V >= vlow) & (V <= vhigh)]}      {vn_key:15s} {Vn:7.3f} in [{vlow:7.3f},{vhigh:7.3f}] {hok[(Vn >= vlow) & (Vn <= vhigh)]}      {i_key:15s} {I:7.3f} in [{ilow:7.3f},{ihigh:7.3f}] {hok[(I >= ilow) & (I <= ihigh)]}       P=V*I {V * I:7.3f}"
                stringout = addstring(stringout, s, verbose=verbose)

                if (V<vlow) | (V>vhigh): allvok = False
                if (I<ilow) | (I>ihigh): alliok = False
                if (Vn < vlow) | (Vn > vhigh): allvnok = False

            s = f"      AEU Voltages OK: {str(allvok):5s} {' ' * 24}       FEE Voltages OK: {str(allvnok):5s} {' ' * 30} Currents OK: {alliok}"
            stringout = addstring(stringout, s, verbose=verbose)

    ##################
    # OUTPUT TM STATS
    ##################
    output_filename = output_dir + f"sft_analysis_HK_{sobsid}_{camera}_TM_stats.txt"
    file = open(output_filename, 'w')
    file.write(stringout)
    file.close()

    ###############
    # PLOT VOLTAGES
    ###############

    if not showplots: plt.ioff()

    fontsize = 15

    c=-1
    fig = plt.figure(figsize=(14, 14))
    gs = GridSpec(2, 1)

    axv = fig.add_subplot(gs[0, 0])

    ytf = [-10,40]
    if not hkonly:
        plt.plot([relftimes[0], relftimes[0]], ytf, c=lightgray, ls='--', label='Frames')
        for tf in relftimes[1:]:
            plt.plot([tf,tf],ytf, c=lightgray, ls='--')

    plt.plot([t_on, t_on], ytf, c=lightblue, ls='--')
    plt.plot([t_stdby,t_stdby],ytf, c=lightblue, ls='--')
    plt.plot([t_full,t_full],ytf, c=lightblue, ls='--', label="NFEE mode transitions")

    for key, nkey in zip(v_keys, vn_keys):
        c+=1
        plt.plot(reltime, hkt[key], c=cv.get_color(c), ls="-", marker=".", lw=2, label=f"{key}")# {np.mean(hkt[key]):.2f} +- {np.std(hkt[key]):.2f}")
        plt.plot(nreltime, hkn[nkey], c=cv.get_color(c), ls="-", marker="o", lw=2, label=f"{nkey}", alpha=0.5)# {np.mean(hkt[key]):.2f} +- {np.std(hkt[key]):.2f}")

    c+=1
    plt.plot(nreltime, hkn["NFEE_MODE"], c=cv.get_color(c), ls="-", marker="o", lw=2, label=f"NFEE_MODE")

    plt.title(f"{camera} {sobsid} AEU-CRIO & NFEE - Voltages", size=fontsize)
    plt.xlabel("Relative time [s]", size=fontsize)
    plt.ylabel("Voltages [V]", size=fontsize)
    plt.grid(alpha=0.25)
    plt.legend()
    if showplots:
        plt.show()

    ###############
    # PLOT CURRENTS
    ###############
    c=-1

    axi = fig.add_subplot(gs[1, 0])

    ytf = [-0.2,1.]
    if not hkonly:
        plt.plot([relftimes[0], relftimes[0]], ytf, c=lightgray, ls='--', label='Frames')
        for tf in relftimes[1:]:
            plt.plot([tf,tf],ytf, c=lightgray, ls='--')

    plt.plot([t_on, t_on], ytf, c=lightblue, ls='--')
    plt.plot([t_stdby, t_stdby], ytf, c=lightblue, ls='--')
    plt.plot([t_full, t_full], ytf, c=lightblue, ls='--', label="NFEE mode transitions")

    for key in i_keys:
        c+=1
        plt.plot(reltime, hkt[key], c=cv.get_color(c), ls="-", marker=".", lw=2, label=f"{key}")# {np.mean(hkt[key]):.2f} +- {np.std(hkt[key]):.2f}")

    c+=1
    plt.plot(nreltime, hkn["NFEE_MODE"] / 5., c=cv.get_color(c), ls="-", marker="o", lw=2, label=f"NFEE_MODE/5")

    axv.get_shared_x_axes().join(axv, axi)

    plt.title(f"{camera} {sobsid} {device} - Currents", size=fontsize)
    plt.xlabel("Relative time [s]", size=fontsize)
    plt.ylabel("Currents [A]"
               "", size=fontsize)
    plt.grid(alpha=0.25)
    plt.legend()
    if showplots:
        plt.show()

    viplotname = output_dir+f"sft_analysis_HK_{sobsid}_{camera}_{device}_VI.png"
    plt.savefig(viplotname)

    if not showplots:
        plt.ion()

    if verbose:
        print(f"\nGraphical and numerical results can be found in\n{output_filename}\n{viplotname}")#\n{iplotname}")
