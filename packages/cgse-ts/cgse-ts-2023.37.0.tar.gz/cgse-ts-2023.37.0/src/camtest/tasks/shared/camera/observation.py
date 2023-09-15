from gui_executor.exec import exec_ui

UI_MODULE_DISPLAY_NAME = "1 — Managing observations"


@exec_ui()
def start_observation(description: str = "replace this default description"):
    """Starts a new observation with the given description.

    Args:
        - description: Description of the new observation (which will appear in the obsid table).
    """

    import camtest
    from egse.confman import ConfigurationManagerProxy

    with ConfigurationManagerProxy() as cm_proxy:
        if obsid := cm_proxy.get_obsid().return_code:
            print(f"A observation {obsid} is currently running, end this observation before starting a new one.")
            return None

        obsid = camtest.start_observation(description=description)
        print(f"Observation started with obsid={obsid}")

    return obsid


@exec_ui()
def end_observation():
    """Ends the current observation and reports on the OBSID that was ended."""

    import camtest
    from egse.confman import ConfigurationManagerProxy

    with ConfigurationManagerProxy() as cm_proxy:
        if obsid := cm_proxy.get_obsid().return_code:
            camtest.end_observation()
            print(f"Observation {obsid} is ended.")
        else:
            print("No observation is currently running.")


@exec_ui(use_kernel=True, immediate_run=True)
def get_obsid():
    """Returns the current OBSID or None when no observation is running."""

    from egse.confman import ConfigurationManagerProxy

    with ConfigurationManagerProxy() as cm_proxy:
        if obsid := cm_proxy.get_obsid().return_code:
            print(f"Observation {obsid} is currently running.")
            return obsid
        else:
            print("No observation is currently running.")
            return None
