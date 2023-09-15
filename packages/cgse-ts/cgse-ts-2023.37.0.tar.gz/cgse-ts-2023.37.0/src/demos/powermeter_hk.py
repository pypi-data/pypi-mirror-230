from camtest.commanding.powermeter_thorlabs_bb import get_value, get_wavelength, get_range, set_wavelength
from camtest.core.exec import building_block


@building_block
def powermeter_hk():
    value = get_value()
    print(f"powermeter_hk: {value}")
    wavelength = get_wavelength()
    print(f"wavelength set to: {wavelength} nm")
    range = get_range()
    print(f"Upper measurement range set to: {range} W")


@building_block
def correction_wavelength():
    set_wavelength(wave=800)

    wavelength = get_wavelength()
    print(wavelength)
