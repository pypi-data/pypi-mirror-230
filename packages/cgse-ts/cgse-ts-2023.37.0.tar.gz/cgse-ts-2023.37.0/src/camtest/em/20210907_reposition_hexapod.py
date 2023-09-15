import numpy as np
import rich

from camtest import execute
from camtest.commanding.csl_gse import check_and_move_relative_user
from egse.coordinates.cslmodel import CSLReferenceFrameModel
from egse.hexapod.symetrie.puna import PunaProxy
from egse.setup import load_setup
from egse.setup import submit_setup


def is_model_sync(model, hexhw, verbose=None, rounding=4, atol=0.0001, rtol=0.0001):
    if verbose is None:
        verbose = ""

    coohex = hexhw.get_user_positions()
    coomodtr, coomodrot = model.get_frame('hexusr').getActiveTranslationRotationVectorsTo(
        model.get_frame('hexobj')
        )
    coomod = np.concatenate([coomodtr, coomodrot])

    print(f"{verbose}Hexapod   : {np.round(coohex, rounding)}")
    print(f"{verbose}Model     : {np.round(coomod, rounding)}")
    print(f"{verbose}Diff      : {np.round(coohex - coomod, rounding)}")

    print(f"{verbose}In synch  : {np.allclose(coohex, coomod, atol=atol, rtol=rtol)}")

    return


hexhw = PunaProxy()

setup = load_setup()

setupmodel = setup.csl_model.model
model = CSLReferenceFrameModel(setupmodel)
print(model.summary())

is_model_sync(model, hexhw)

vtrans = [0, 0, -20]
vrot = [0, 0, 0]
verbose = True

move_ok = execute(
    check_and_move_relative_user, cslmodel=model, translation=vtrans, rotation=vrot, setup=setup,
    verbose=verbose
    )

is_model_sync(model, hexhw)

csl_dict = model.serialize()
setup.csl_model.model = csl_dict
rich.print(setup)
setup = submit_setup(
    setup, "CSLReferenceFrameModel EM 003 20210907 EOB - FPA [0, 0, -20] from Hartmann plane"
    )
rich.print(setup)
