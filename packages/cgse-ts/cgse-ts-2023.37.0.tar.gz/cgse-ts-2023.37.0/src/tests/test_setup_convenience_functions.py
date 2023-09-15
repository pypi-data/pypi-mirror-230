from camtest import list_setups, get_setup, load_setup


def test_list_setup():

    list_setups()

    setup = get_setup()

    assert setup is not None

    print("*"*80)
    print(setup._filename)

    setup = load_setup(25)

    assert setup is not None

    print("*"*80)
    print(setup._filename)

    setup = get_setup()

    assert setup is not None

    print("*"*80)
    print(setup._filename)

