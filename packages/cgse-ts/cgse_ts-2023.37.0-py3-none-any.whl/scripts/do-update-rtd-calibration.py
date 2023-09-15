from egse.setup import load_setup
from camtest import start_observation, end_observation, building_block

setup = load_setup()

sensor_name = "6666A7777"
sensor_name_serial_number = 12345
sensor_name_conversion = "frtd_3"

conversion_name = "frtd_3"
conversion = [6, 5, 4, 3, 2, 1]


@building_block
def update_setup_with_rtd_calibration(
        setup=None, sensor_name=None, serial_number=None, conversion_name=None, conversion=None):

    setup.gse.tcs.calibration.conversion[conversion_name] = conversion
    setup.gse.tcs.calibration.sensors[sensor_name] = dict(
        serial_number=serial_number,
        conversion = conversion_name
    )

    return setup


start_observation("Setup: Update TCS RTD calibration")

setup = update_setup_with_rtd_calibration(
    setup=setup,
    sensor_name="tou_rtd_1",
    sensor_name_serial_number="2047A001",
    conversion_name="frtd_1",
    conversion=[1, 2, 3, 4]
)

end_observation()
