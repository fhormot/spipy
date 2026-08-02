import pytest

import os
from pathlib import Path

from spiceybun.xschem import Xschem

def load_netlist(path: Path) -> list:
    """
    Load the netlist from the specified path.

    Args:
        path (Path): The path to the netlist file.

    Returns:
        list: A list of lines from the netlist file, excluding comments and empty lines.
    """
    with open(path, "r") as f:
        netlist = f.read()

    # Remove comments and empty lines
    netlist = [line for line in netlist.splitlines() if line.strip() and not line.startswith("**")]

    return netlist

@pytest.fixture
def xschem_instance():
    path = Path(__file__).parent
    path_netlist = path / "xschem" / "xschem_tb_rc.sch"

    return Xschem(path_netlist)

def test_netlist_generation(xschem_instance):
    path = Path(__file__).parent
    path_output = path / "outputs" / "xschem_tb_rc"

    result = xschem_instance.netlist(path=path_output)

    with open(result["path"], "r") as f:
        netlist_result = f.read()

    # Remove comments and empty lines
    netlist_result = load_netlist(result["path"])
    netlist_expected = load_netlist(Path(__file__).parent / "netlists" / "input_flat_no_variables.spice")

    assert netlist_result == netlist_expected


