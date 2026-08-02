import os
import re
import subprocess
from itertools import product
from pathlib import Path

from spiceybun.measure_ngspice import Measure_ngspice
from spiceybun.variable import Variable


class Ngspice:
        def __init__(self, path_netlist, **kwargs):
                """
                Initialize the Ngspice class with the path to the netlist and optional keyword arguments.
                
                Args:
                        path_netlist (str): Path to the netlist file.
                
                """
                self._netlist           = []

                # Netlist sections
                self._analysis          = []
                self._variables         = []
                self._libraries         = []
                self._plots             = []
                self._spiceinit         = ''

                # Control statements
                self._plot_all          = False

                # Paths
                self._path_netlist      = path_netlist

                self._output_path       = Path(__file__).parent

                # Measurement control
                self.measure            = Measure_ngspice()

                # Outputs
                self._results            = {}

                # Preparation during init
                self._read_dut_nelist()

# Internal methods

        def _read_dut_variables(self) -> None:
                """
                Read the netlist and extract variables defined in the netlist. Variables are identified by the pattern '{variable_name}' in the netlist lines. If a variable is found that is not already in the list of variables, it is added to the list.

                Returns:
                        None
                """

                variables = []

                for line in self._netlist_dut:
                        result = re.findall(r'\{\w+\}', line)

                        if len(result) > 0:
                                variables.extend(result)

                variables = list(set(variables))

                for variable in variables:
                        name = variable.strip('{}')

                        if not any(v.get_name() == name for v in self._variables):
                                self._variables.append(Variable(name))

        def _read_dut_nelist(self) -> None:
                """
                Read the netlist from the specified path and extract variables defined in the netlist. The netlist is read line by line, and variables are identified and stored in the list of variables.
                
                Raises:
                        ValueError: If the netlist path is empty.
                        FileNotFoundError: If the netlist file does not exist at the specified path.
                Returns:
                        None
                """

                if not self._path_netlist:
                        raise ValueError("Spiceybun: Netlist path cannot be empty.")

                if not os.path.isfile(self._path_netlist):
                        raise FileNotFoundError(f"Spiceybun: The file '{self._path_netlist}' does not exist.")

                with open(self._path_netlist, 'r') as f:
                        self._netlist_dut = f.readlines()

                # TODO: Strip existing control statements

                # Extract variables
                self._read_dut_variables()

        def _include(self, path, **kwargs) -> str:
                """
                Include a netlist file in the current netlist. The included file is specified by the `path` argument, and an optional section can be specified using the `section` keyword argument.

                Args:
                        path (str): The path to the netlist file to include.
                        section (str, optional): The section of the netlist to include. Default is an empty string, which includes the entire file. If a section is specified, it will be appended to the include statement.

                Returns:
                        str: The include statement added to the netlist.
                """

                str = f'.include {path}'

                if 'section' in kwargs:
                        str = str + ' ' + kwargs['section']

                self._netlist.append(str)

                return str

        def _write_netlist_dut(self, **kwargs) -> str:
                """
                Write the DUT netlist to a file. The netlist is written to the output directory specified by the `output_path` attribute, and an optional subfolder can be specified using the `id` keyword argument.

                Args:
                        **kwargs: 
                        - The `id` keyword can be used to specify a subfolder for the output netlist file. If not provided, the netlist will be written to the main output directory.

                Returns:
                        str: The path to the written netlist file.
                """

                subfolder = kwargs.get('id', '')

                output_path = os.path.join(self._output_path, subfolder)
                output_netlist = os.path.join(output_path, 'netlist.spice')

                with open(output_netlist, 'w') as f:
                        f.writelines(self._netlist_dut)
                os.chmod(output_netlist, 0o755)

                return output_netlist

        def _write_netlist(self, **kwargs) -> str:
                """
                Write the complete netlist to a file. The netlist is written to the output directory specified by the `output_path` attribute, and an optional subfolder can be specified using the `id` keyword argument.
                
                Args:
                        **kwargs: 
                        - The `id` keyword can be used to specify a subfolder for the output netlist file. If not provided, the netlist will be written to the main output directory.

                Returns:
                        str: The path to the written netlist file.
                """

                subfolder = kwargs.get('id', '')

                self._add_control(**kwargs)

                self._netlist.append('.end')

                output_path = os.path.join(self._output_path, subfolder)
                output_netlist = os.path.join(output_path, 'tb_test.spice')

                with open(output_netlist, 'w') as f:
                        f.write('\n'.join(self._netlist))
                os.chmod(output_netlist, 0o755)

                self._netlist_output = output_netlist

                return output_netlist

        def _write_run_command(self, **kwargs) -> str:
                """
                Write a shell script to run the ngspice simulation. The script is written to the output directory specified by the `output_path` attribute, and an optional subfolder can be specified using the `id` keyword argument.

                Args:
                        **kwargs:
                        - The `id` keyword can be used to specify a subfolder for the output command file. If not provided, the command will be written to the main output directory.

                Returns:
                        str: The path to the written command file.
                """

                subfolder = kwargs.get('id', '')

                folder_path = os.path.join(self._output_path, subfolder)

                path_output_netlist = self._netlist_output

                # command_format = "#!/bin/bash\nngspice -i -o {output_path} {input_path} -a || sh"
                command_format = "#!/bin/bash\nngspice -o {output_path} {input_path} -a"
                command_format = "#!/bin/bash\nngspice -b -o {output_path} {input_path} -a"

                command_path = os.path.join(folder_path, 'run_command')
                output_path = os.path.join(folder_path, 'output.log')
                input_path = path_output_netlist

                netlist_command = command_format.format(
                        output_path=output_path, 
                        input_path=input_path
                        )
                
                with open(command_path, 'w') as f:
                        f.write(netlist_command)
                os.chmod(command_path, 0o755)

                return command_path

        def _write_spiceinit(self, **kwargs) -> str:
                """
                Write the .spiceinit file to the output directory. If a .spiceinit file has been specified, it will be copied to the output directory. An optional subfolder can be specified using the `id` keyword argument.
                
                Args:
                        **kwargs:
                        - The `id` keyword can be used to specify a subfolder for the output .spiceinit file. If not provided, the .spiceinit file will be written to the main output directory.

                Returns:
                        str: The path to the written .spiceinit file.
                """

                if self._spiceinit == '':
                        return ''

                subfolder = kwargs.get('id', '')

                output_path = os.path.join(self._output_path, subfolder)
                output_spiceinit = os.path.join(output_path, '.spiceinit')

                with open(self._spiceinit, 'r') as f:
                        spiceinit_content = f.read()

                with open(output_spiceinit, 'w') as f:
                        f.write(spiceinit_content)
                os.chmod(output_spiceinit, 0o755)

                return output_spiceinit

        def _add_control(self, **kwargs) -> list:
                """
                Add control statements to the netlist. Control statements include variable definitions, analysis commands, and measurement commands. The control statements are appended to the netlist.

                Args:
                        **kwargs: Optional keyword arguments. The `mc` keyword can be used to specify whether to perform a Monte Carlo analysis. If `mc` is set to True, additional control statements for Monte Carlo analysis will be added.

                Returns:
                        list: A list of control statements added to the netlist.
                """

                # Kwargs
                mc = kwargs.get('mc', False)

                control_statement = []
                control_statement.append('\n* Control statements added by spicybun')

                # Parameter definitions
                variables = kwargs.get('variables', self._libraries + self._variables)
                for variable in variables:
                        control_statement.append(variable.get_value_definition())

                if mc:
                        seed = kwargs.get('seed', 1)
                        mc_runs = kwargs.get('mc_runs', 350)

                # Start of control statements
                control_statement.append('\n.control')

                # Section
                # Measurement file preparation
                control_statement.extend(self._netlist_define_measurement_setup(**kwargs))

                # Section Monte Carlo
                if mc:
                        control_statement.append('\n\t* Monte Carlo analysis')
                        control_statement.append(f'\tsetseed {seed}')
                        control_statement.append(f'\tlet mc_runs={mc_runs}')
                        control_statement.append('\tlet mc_index=0')

                        control_statement.append('\n\twhile mc_index < mc_runs')

                # Section
                # Append analysis
                for element in self._analysis:
                        control_statement.append(f'\t\t{element}')

                        # suffix = element.split()[0]

                # Section
                # Save statements
                # TODO: Wrap measurements and save statments with their respective analysis
                control_statement.extend(self._netlist_define_plot(**kwargs))

                # Measureement definition and write to file
                control_statement.extend(self._netlist_define_measurement_write(**kwargs))

                if mc:
                        control_statement.append('\n\t\tlet mc_index = mc_index + 1')
                        control_statement.append('\t\treset')

                        control_statement.append('\n\t* End of Monte Carlo iteration')
                        control_statement.append('\tend')

                control_statement.append('\n\texit')
                control_statement.append('.endc\n')

                self._netlist.extend(control_statement)
                return control_statement

        def _netlist_define_plot(self, **kwargs) -> list:
                """
                Define the plot statements for the netlist. The plot statements specify which signals to save during the simulation. If the `plot_all` flag is set to True, all signals will be saved; otherwise, only the specified signals will be saved.

                Args:
                        **kwargs: 
                        - The `id` keyword can be used to specify a subfolder for the output plot files. If not provided, the plot files will be written to the main output directory.

                Returns:
                        list: A list of plot statements added to the netlist.
                """

                control_statement = []

                subfolder = kwargs.get('id', '')
                output_path = os.path.join(self._output_path, subfolder, 'output.raw')

                # Keep vector names in the header
                control_statement.append('\n\t\tset wr_vecnames')
                
                # Use a single scale (column) for all signals
                control_statement.append('\t\tset wr_singlescale')

                if not self._plot_all:
                        control_statement.append(f'\t\twrdata {output_path} {' '.join(self._plots)}')
                else:
                        control_statement.append('\t\tsave all')
                        control_statement.append(f'\t\twrdata {output_path} all')

                return control_statement

        def _netlist_define_measurement_setup(self, **kwargs) -> list:
                """
                Define the measurement setup for the netlist. This method prepares the measurement output file and writes a header with the names of the measurements to be performed during the simulation.

                Args:
                        **kwargs:
                        - The `id` keyword can be used to specify a subfolder for the output measurement file. If not provided, the measurement file will be written to the main output directory.

                Returns:
                        list: A list of control statements for the measurement setup added to the netlist.
                """

                control_statement = []

                subfolder = kwargs.get('id', '')
                output_path = os.path.join(self._output_path, subfolder, 'results', 'measurements.raw')


                measurements = self.measure.get_measurements()
                if len(measurements)>0:
                        control_statement.append('\t*Prepare measurement output file with a header')
                        measurement_list = ' '.join([measure['name'] for measure in measurements])
                        control_statement.append(f'\techo "{measurement_list}" > {output_path}')

                return control_statement

        def _netlist_define_measurement_write(self, **kwargs) -> list:
                """
                Define the measurement write statements for the netlist. This method appends the measurement commands to the netlist, which will be executed during the simulation to perform the specified measurements and write the results to a file.

                Args:
                        **kwargs:
                        - The `id` keyword can be used to specify a subfolder for the output measurement file. If not provided, the measurement file will be written to the main output directory.

                Returns:
                        list: A list of control statements for the measurement write commands added to the netlist.
                """

                control_statement = []

                subfolder = kwargs.get('id', '')
                output_path = os.path.join(self._output_path, subfolder, 'results', 'measurements.raw')

                control_statement.append('\n\t\t* Measurements')

                measurements = self.measure.get_measurements()
                for measure in measurements:
                        control_statement.append(f'\t\t{measure["measure"]}')

                if len(measurements) > 0:
                        control_statement.append('\n\t\t* Measurement output in separate files')
                        measurement_list = ' '.join([f'$&{measure['name']}' for measure in measurements])
                        control_statement.append(f'\t\techo "{measurement_list}" >> {output_path}')

                return control_statement

        def _run_single_run(self, **kwargs) -> dict:
                """
                Run a single simulation with the current netlist and settings. The simulation is executed using the ngspice command, and the output is captured. The results are stored in a dictionary, which includes the standard output, standard error, return code, result path, and measurement path.
                
                Args:
                        **kwargs:
                        - The `id` keyword can be used to specify a subfolder for the output files. If not provided, the output files will be written to the main output directory.
                        
                Returns:
                        dict: A dictionary containing simulation output results, including stdout, stderr, return code, result path, and measurement path.
                """

                subfolder = kwargs.get('id', '')

                output_path = os.path.join(self._output_path, subfolder)

                # Verify the output folder exists
                if not os.path.exists(output_path):
                        os.makedirs(output_path)
                        os.chmod(output_path, 0o755)

                # Verify that the results folder is available
                if not os.path.exists(os.path.join(output_path, "results")):
                        os.makedirs(os.path.join(output_path, "results"))
                        os.chmod(os.path.join(output_path, "results"), 0o755)

                path_input_netlist = self._write_netlist_dut(**kwargs)
                self._write_spiceinit(**kwargs)

                self._include(path_input_netlist)
                self._write_netlist(**kwargs)

                command_path = self._write_run_command(**kwargs)

                output = subprocess.run(
                        command_path, 
                        # env=self.env, 
                        shell=True, 
                        capture_output=True, 
                        text=True,
                        check=True
                )

                run_path = os.path.join(output_path, 'run.log')

                with open(run_path, 'w') as f:
                        f.write(output.stdout)
                os.chmod(command_path, 0o755)

                return_dict = {
                        'stdout': output.stdout,
                        'stderr': output.stderr,
                        'returncode': output.returncode,
                        'result_path': os.path.join(output_path, 'output.raw'),
                        'measurement_path': os.path.join(output_path, 'results', 'measurements.raw')
                        }

                return return_dict

        def _run_sweep(self, sweep_list, **kwargs) -> dict:
                """
                Run a sweep of simulations with the current netlist and settings. The sweep is performed over all combinations of variations specified in the `sweep_list`. Each combination is executed as a separate simulation, and the results are collected in a list of dictionaries.

                Args:
                        sweep_list (list): A list of combinations of variations to be simulated. Each combination is a list of Variable objects representing the variations for that run.
                        **kwargs:
                        - The `id` keyword can be used to specify a subfolder for the output files. If not provided, the output files will be written to the main output directory.

                Returns:
                        dict: A dictionary containing simulation output results for each run in the sweep. The results are organized by keys, with each key corresponding to a list of values for that key across all runs.
                """

                results = []

                for idx, run in enumerate(sweep_list):
                        self._netlist = []
                        results.append(self._run_single_run(variables=run, id=f'{idx}', **kwargs))

                return { key: [d[key] for d in results] for key in results[0].keys()}

# Public methods

        def get_variables(self) -> list:
                """
                Get the list of variables in the netlist.

                Returns:
                        list: A list of dictionaries representing available variables.
                """

                return [variable.get_dict() for variable in self._variables]

        def get_sim_output(self) -> dict:
                """
                Get the simulation output results.

                Returns:
                        dict: A dictionary containing simulation output results, including stdout, stderr, return code, result path, and measurement path.
                """
                return self._results

        def get_measurements(self) -> list:
                """
                Get the list of measurements resulted from the simulation.
                
                Returns:
                        list: A list of dictionaries representing resulting measurements. Measurements are returned as a list of pandas DataFrames, one for each measurement file generated during the simulation. Returns an empty list if no measurements were defined or generated.
                """

                locations = self.get_sim_output()

                if 'measurement_path' not in locations:
                        return []

                results = []

                locations = locations['measurement_path']
                locations = [locations] if type(locations) is not list else locations

                for location in locations:
                        if os.path.exists(location):
                                results.append(self.measure.process_measure(location))

                return results

        def set_variable(self, name: str, value: float | str | list) -> dict | None:
                """
                Set the value of a variable.

                Args:
                        name (str): The name of the variable.
                        value (int | float | str | list): The value to set. Setting the value to a list will create multiple variations of the netlist for each value in the list.

                Returns:
                        dict | None: A dictionary representing the updated variable, or None if the variable was not found.
                """

                for variable in self._variables:
                        if variable.get_name() == name:
                                variable.set_value(value)
                                return variable.get_dict()

                return None

        def set_temperature(self, temperature: float | str | list) -> dict:
                """
                Set the temperature for the simulation. If a temperature variable already exists, it will be updated; otherwise, a new temperature variable will be created.

                Args:
                        temperature (int | float | str | list): The temperature value(s) to set. Setting the value to a list will create multiple variations of the netlist for each value in the list.

                Returns:
                        dict: A dictionary representing the updated or newly created temperature variable.
                """

                for variable in self._variables:
                        if variable.get_name() == 'temperature':
                                variable.set_value(temperature)
                                return variable.get_dict()

                temp = Variable(name='temperature', type='temperature')
                temp.set_value(temperature)

                self._variables.append(temp)

                return temp.get_dict()

        def add_library(self, library_path: str, section: str | list = '') -> dict:
                """
                Add a library to the netlist. If the library already exists, it will be updated with the new section; otherwise, a new library will be created.

                Args:
                        library_path (str): The path to the library file.
                        section (str): The section of the library to include. Default is an empty string. Setting the value to a list will create multiple variations of the netlist for each value in the list.

                Returns:
                        dict: A dictionary representing the added or updated library.
                """

                for library in self._libraries:
                        if library.get_name() == library_path:
                                library.set_value(section)
                                return library.get_dict()

                library = Variable(name=library_path, type='library')
                library.set_value(section)
                self._libraries.append(library)

                return library.get_dict()

        def add_transient(self, t_stop: float | str, **kwargs) -> str:
                """
                Add a transient analysis statement to the netlist. If a transient statement already exists, it will be overwritten with the new parameters.
                
                Args:
                        t_stop (float): The stop time for the transient analysis.
                        t_step (float, optional): The time step for the transient analysis. Default is calculated as (t_stop - t_start) / 50.
                        t_start (float, optional): The start time for the transient analysis. Default is 0.
                        t_max (float, optional): The maximum time for the transient analysis. Default is 10 times the time step.

                Returns:
                        str: The transient analysis statement added to the netlist.
                """

                # Overwrite previous transient statement if it exists
                self._analysis = [x for x in self._analysis if not x.startswith("tran")]

                # TODO: Calculate suggested/maximum steps
                # Step 1: calculate based on stop time --> Bad for long sims with sharp transients
                # Step 2: Find/assume fastest signal in netlist and adjust t_step accordingly
                # --> Not accounting for fast digital signals 
                # TODO: Define transient statement using variables
                t_stop = float(t_stop)
                t_start = float(kwargs.get('t_start', 0))
                t_step = float(kwargs.get('t_step', (t_stop-t_start)/50))
                t_max = float(kwargs.get('t_max', t_step*10))

                transient_statement = f'tran {t_step} {t_stop} {t_start} {t_max}'

                self._analysis.append(transient_statement)

                return transient_statement

        def add_ac(self, f_start: float | str, f_stop: float | str, n: int, **kwargs) -> str:
                """
                Add an AC analysis statement to the netlist. If an AC statement already exists, it will be overwritten with the new parameters.

                Args:
                        f_start (float): The start frequency for the AC analysis.
                        f_stop (float): The stop frequency for the AC analysis.
                        n (int): The number of points per decade for the AC analysis.
                        type (str, optional): The type of AC analysis. Default is 'dec' for a decade sweep. Other options include 'oct' for an octave sweep and 'lin' for a linear sweep.

                Returns:
                        str: The AC analysis statement added to the netlist.
                """
                # Overwrite previous AC statement if it exists
                self._analysis = [x for x in self._analysis if not x.startswith("ac")]

                f_start = float(f_start)
                f_stop = float(f_stop)
                n_x = int(n)

                type = kwargs.get('type', 'dec')

                ac_statement = f'ac {type} {n_x} {f_start} {f_stop}'

                self._analysis.append(ac_statement)

                return ac_statement

        def add_op(self) -> str:
                """
                Add an operating point analysis statement to the netlist. If an operating point statement already exists, it will be overwritten.

                Returns:
                        str: The operating point analysis statement added to the netlist.
                """
                # Overwrite previous operating point statement if it exists
                self._analysis = [x for x in self._analysis if not x.startswith("op")]

                op_statement = 'op'

                self._analysis.append(op_statement)

                return op_statement

        def add_spiceinit(self, spiceinit_path) -> str:
                """
                Define the path to a .spiceinit file to be used during the simulation. If a .spiceinit file already exists, it will be overwritten with the new path.

                Args:
                        spiceinit_path (str): The path to the .spiceinit file.

                Returns:
                        str: The path to the .spiceinit file.
                """
                self._spiceinit = spiceinit_path

                return self._spiceinit

        def save_signal(self, signal: str | list) -> list:
                """
                Specify the signals to be saved during the simulation. If signals have already been specified, the new signals will be added to the existing list.

                Args:
                        signal (str or list): The signal or signals to be saved.

                Returns:
                        list: The updated list of signals to be saved.

                Raises:
                        ValueError: If the signal is not a string or a list of strings.
                """
                if not isinstance(signal, (str, list)):
                        raise TypeError("Spiceybun: Signal must be a string or a list of strings.")
                
                #TODO: Check if valid net/port
                #TODO: Remove duplicates from self._plots
                if type(signal) is list:
                        self._plots.extend(signal)
                else:
                        self._plots.append(signal)

                return self._plots

        def save_signal_all(self, flag) -> bool:
                """
                Set a flag to save all signals during the simulation. If the flag is set to True, all signals will be saved; if set to False, only specified signals will be saved.

                Args:
                        flag (bool): A boolean flag indicating whether to save all signals (True) or not (False).

                Returns:
                        bool: The updated flag indicating whether to save all signals.
                """

                self._plot_all = flag

                return self._plot_all

        def set_output_path(self, output_path) -> None:
                """
                Define the path to the output directory for the simulation results.

                Args:
                        output_path (str): The path to the output directory.

                Returns:
                        None

                Raises:
                        ValueError: If the output path is empty.
                """

                self._output_path = output_path

        def run(self, **kwargs) -> dict:
                """
                Run the simulation with the current netlist and settings. If there are no variations in variables or libraries, a single run will be executed; otherwise, a sweep of all combinations of variations will be performed.

                Args:
                        **kwargs: 
                        - mc (bool): Flag to indicate whether to perform a Monte Carlo analysis. Default is False.
                        - mc_runs (int): Number of Monte Carlo runs to perform. Default is 350.

                Returns:
                        dict: A dictionary containing simulation output results, including stdout, stderr, return code, result path, and measurement path. If a sweep is performed, the results will be a list of dictionaries, one for each run in the sweep.
                """

                total_variations = self._libraries + self._variables

                if len(total_variations) == 0:
                        self._results = self._run_single_run(**kwargs)
                        return self.get_sim_output()
                
                #Create all variation combinations
                permutation_pre_list = [variable.get_split() for variable in total_variations]
                permutations = list(product(*permutation_pre_list))

                if len(permutations) == 1:
                        self._results = self._run_single_run(**kwargs)
                else:
                        self._results =  self._run_sweep(permutations, **kwargs)

                return self.get_sim_output()