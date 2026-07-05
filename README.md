# SPICEybun

An NGSPICE wrapper for simplified verification.

# Usage

```Python
from spiceybun.ngspice import Ngspice

# Simulator setup
simulator = Ngspice(path_netlist)
simulator.set_output_path(path_output)

simulator.add_transient(500e-9, t_step=10e-12)

simulator.save_signal('V(v_out)')

output = simulator.run()

```

# Documentation
TBD

# Long term roadmap

- [ ] Enabling basic functionality:
    - [ ] All analysis statements
        - [x] Transient
    - [ ] Libraries
        - [x] Library inclusion
        - [x] Library sweep
        - [ ] Library correlation
    - [ ] Variables
        - [x] Simple variables
        - [ ] Equations
        - [ ] Advanced variable features (distribution, limits, etc.)
    - [ ] Measurements
        - [x] Explicit spice input
- [x] Sweeps
- [x] Monte Carlo
- [ ] Advanced features
    - [ ] Netlist from XSchem
    - [ ] Simulator options
    - [ ] Report generation
    - [ ] Simulator error handling