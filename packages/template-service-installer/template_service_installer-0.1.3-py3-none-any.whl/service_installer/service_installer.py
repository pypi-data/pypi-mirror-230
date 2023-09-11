from pathlib import Path
import os
import sys
from typing import Union


def install_services(template_dir: Union[str, Path], working_dir: Union[str, Path]) -> None:
    """
    :param template_dir: Path to directory with service templates
    :param working_dir: Path to service working 'WorkingDirectory'
    :return:
    """
    template_dir = Path(template_dir)
    working_dir = Path(working_dir)
    services = os.listdir(template_dir)
    for service in services:
        with open(template_dir / service, 'r') as file:
            data = file.read()
        with open(f'/etc/systemd/system/{service}', 'w') as file:
            try:
                file.write(data.format(work_dir=working_dir))
            except KeyError:
                raise KeyError(f'Wrong format string in "{service}" file')


if __name__ == '__main__':
    install_services(sys.argv[1], sys.argv[2])
