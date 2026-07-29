import subprocess
import os

from pathlib import Path

class Xschem:
    def __init__(self, path: str | Path):
        self.path = path

    def netlist(self, **kwargs) -> dict:
        """
        Generate the netlist for the Xschem schematic.

        Returns:
            dict: A dictionary containing the generated netlist and associated information.
        """

        input_path = self.path
        output_path = kwargs.get("path", Path(input_path).parent)
        name = kwargs.get("name", Path(input_path).with_suffix(".spice"))

        command_format = "xschem --netlist --spice -x --quit -o {output_path} -N {name} {input_path}"

        netlist_command = command_format.format(output_path=output_path, name=name, input_path=input_path)

        # Check if the output directory exists
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        os.chmod(output_path, 0o755)

        output = subprocess.run(netlist_command, 
                                # env=self.env, 
                                shell=True, 
                                capture_output=True, 
                                text=True,
                                check=False)

        return {
            "netlist": output.stdout,
            "errors": output.stderr,
            "path": output_path
        }
