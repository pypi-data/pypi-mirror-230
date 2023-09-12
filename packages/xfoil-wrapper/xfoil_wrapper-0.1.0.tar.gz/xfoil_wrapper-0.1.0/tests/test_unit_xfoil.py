import os
from xfoil_wrapper import XFoil, get_xfoil_exe


def test_get_xfoil():
    """
    Unit test for getting the xfoil executable file.
    """
    xfoil_path = get_xfoil_exe()
    assert os.path.isfile(xfoil_path), "Invalid XFoil exectuable file!"


def test_xfoil_run(airfoil_name: str = "naca0012"):
    """
    Unit test for running the xfoil simulation
    """
    # Assign
    alphas = [0, 4, 8]
    re_numbers = [5e5, 1e6]
    # Act
    case = XFoil(f"tests/airfoils/{airfoil_name}.dat", root=None)
    run_data = case.run_alphas(alphas=alphas, re=re_numbers, get_sectload=True)
    # Assert
    assert_msg = "Results do not match the input amount of"
    assert len(run_data) == len(re_numbers), f"{assert_msg} Re"
    for i, re_number in enumerate(re_numbers):
        assert run_data[i]["re"] == re_number
        cp = run_data[i]["cp"]
        assert len(cp) == len(alphas), f"{assert_msg} Alphas"
        assert len(cp[0]) > 0, f"Invalid Cp results for Re = {re_numbers[i]}"
