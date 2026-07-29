import pytest

import os
from pathlib import Path

from spiceybun.xschem import Xschem

@pytest.fixture
def xschem_instance():
    path = Path(__file__).parent
    path_netlist = path / "xschem" / "xschem_tb_rc.sch"

    return Xschem(path_netlist)

def test_netlist_generation(xschem_instance):
    path = Path(__file__).parent
    path_output = path / "outputs" / "xschem_tb_rc"

    result = xschem_instance.netlist(path=path_output)

