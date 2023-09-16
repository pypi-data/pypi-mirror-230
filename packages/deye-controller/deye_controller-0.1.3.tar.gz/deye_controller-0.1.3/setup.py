# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['deye_controller', 'deye_controller.modbus', 'deye_controller.utils']

package_data = \
{'': ['*']}

install_requires = \
['pysolarmanv5>=2.4.0']

entry_points = \
{'console_scripts': ['deye-read = '
                     'deye_controller.deye_reader:read_from_inverter',
                     'deye-regtest = deye_controller.deye_reader:test_register',
                     'deye-regwrite = deye_controller.deye_reader:test_write',
                     'deye-scan = '
                     'deye_controller.deye_reader:scan_for_loggers']}

setup_kwargs = {
    'name': 'deye-controller',
    'version': '0.1.3',
    'description': 'MODBUS Controller for DEYE inverters',
    'long_description': "DEYE-controller\n===================\n\n* A library and simple tools for interaction with DEYE hybrid inverters\n* The communication with the inverter requires a SOLARMAN datalogger\n* `pysloarmanv5 <https://github.com/jmccrohan/pysolarmanv5>`_  based library\n* Command line tools (exposed after install):\n    - deye-read - read everything from the inverter (use --help for filters/options)\n    - deye-regcheck - for quick check on specific register(s)\n    - deye-scan is a scanner for dataloggers in the local network (not DEYE related)\n    - deye-regwrite - for writing to individual registers\n\n* Tested with:\n    - SUN-12K-SG04LP3 / LSW-3\n\nINSTALL\n========\n\n.. code-block:: console\n\n  pip install deye-controller\n\n\nTODO List\n=============\n\n\nExamples\n==============\n* Basic usage:\n\n    * read a register from the inverter\n\n    .. code-block:: python\n\n        >>> from deye_controller import HoldingRegisters, WritableRegisters\n        >>> from pysolarmanv5 import PySolarmanV5\n        >>> inv = PySolarmanV5('192.168.1.100', 2712345678)\n        >>> register = HoldingRegisters.BMSBatteryCapacity\n        >>> res = inv.read_holding_registers(register.address, register.len)\n        >>> register.value = res[0] if register.len == 1 else res\n        >>> print(register.description, register.format(), register.suffix)\n        bms_battery_SOC 24 %\n        >>> inv.disconnect()\n    ..\n\n    * write\n\n    .. code-block:: python\n\n        >>> from deye_controller import HoldingRegisters, WritableRegisters\n        >>> from pysolarmanv5 import PySolarmanV5\n        >>> inv = PySolarmanV5('192.168.1.100', 2712345678)\n        >>> register = WritableRegisters.SellModeSOC3\n        >>> register.set(23)\n\n        >>> inv.write_multiple_holding_registers(register.address, [register.modbus_value])\n        1\n        >>> inv.disconnect()\n\n\n\n* SellMode programming:\n\n  .. code-block:: python\n\n    >>> from deye_controller import SellProgrammer\n    >>> prog = SellProgrammer('192.168.1.108', 2799999999)\n    >>> prog.show_as_screen()\n    ____________________________________________________\n    | Grid  |  Gen  |      Time     |   Pwr    |  SOC % |\n    |       |       | 00:00 | 03:00 |     3500 |   100% |\n    |       |       | 03:00 | 04:00 |     3500 |    30% |\n    |       |       | 04:00 | 05:00 |     3500 |    30% |\n    |       |       | 05:00 | 10:00 |     3500 |    30% |\n    |       |       | 10:00 | 23:00 |     3500 |   100% |\n    |       |       | 23:00 | 00:00 |     3500 |    30% |\n    ----------------------------------------------------\n    >>> prog.update_program(3, start_t='6:30', power=2500, soc=35, grid_ch=True)\n    Program updated\n     >>> prog.show_as_screen()  # For visual confirmation of the settings\n    ____________________________________________________\n    | Grid  |  Gen  |      Time     |   Pwr    |  SOC % |\n    |       |       | 00:00 | 03:00 |     3500 |   100% |\n    |       |       | 03:00 | 04:00 |     3500 |    30% |\n    |       |       | 04:00 | 06:30 |     3500 |    30% |\n    |   ✓   |       | 06:30 | 10:00 |     2500 |    35% |\n    |       |       | 10:00 | 23:00 |     3500 |   100% |\n    |       |       | 23:00 | 00:00 |     3500 |    30% |\n    ----------------------------------------------------\n    >>> prog.upload_settings()  # In order to upload the settings to the inverter\n    >>> prog.disconnect()  # Needed if PySolarmanV5 >= 3.0.0\n\n\nNotes\n=========\n* It is possible the inverter to be completely deactivated by writing 0 to register 80\n  WritableRegisters.SwitchOnOff.set(False) but it will raise an alarm and will show error F19.\n  The normal state is restored as soon as the register is set to its default value 1.\n* The WritableRegisters.GridExportLimit register can be used if the grid export is not desired\n  when the battery is charged and the PV generation exceeds the load.\n",
    'author': 'githubDante',
    'author_email': 'github@dante.tk',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/githubDante/deye-controller',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
