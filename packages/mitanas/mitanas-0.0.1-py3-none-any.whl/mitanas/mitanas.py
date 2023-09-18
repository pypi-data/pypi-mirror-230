import os
import re
import subprocess
from shlex import quote
from typing import List, Optional

import PyInstaller.__main__


class CrontabManager:
    @staticmethod
    def get_crontab() -> str:
        return subprocess.run(
            ["crontab", "-l"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ).stdout.decode("utf-8")

    @staticmethod
    def set_crontab(crontab: str) -> None:
        subprocess.run(
            f"echo {quote(crontab)} | crontab -",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )


class StartupHandler:
    def __init__(self, executable_path: str, executable_args: List[str] = None):
        self.main_command = f"@reboot {executable_path}"
        self.full_command = (
            f"{self.main_command} {' '.join(executable_args or [])}".strip()
        )

    def already_exists_at_startup(self) -> Optional[str]:
        """checks if the program is already scheduled to start with the system

        Return:
            str: the command if it exists, None otherwise
        """
        regex = re.compile(f"^{re.escape(self.main_command)}(?: |$)")
        old_crontab = CrontabManager.get_crontab()
        for line in old_crontab.split("\n"):
            if regex.search(line):
                return line.strip()
        return None

    def add_at_startup(self) -> None:
        """adds the program indicated in the path to be
         started along with the system"""
        old_crontab = CrontabManager.get_crontab().strip()
        command_already_present = self.already_exists_at_startup()
        if command_already_present:
            new_crontab = old_crontab.replace(
                command_already_present, self.full_command
            )
        else:
            new_crontab = (
                (old_crontab + "\n") if old_crontab else ""
            ) + self.full_command
        CrontabManager.set_crontab(new_crontab)


class Mitanas:
    """generates executable from the python script present
    in the project where it was installed and configures
    initialization along with the system
    """

    def __init__(self, project_name: str, path_to_main: str, dist_path: str = None):
        self.project_name = project_name
        self.path_to_main = path_to_main
        home_directory = os.path.expanduser("~")
        self.dist_path = (
            dist_path
            if dist_path
            else os.path.join(home_directory, f".mitanas/{self.project_name}")
        )
        self.executable_path = os.path.join(self.dist_path, self.project_name)

    def generate_executable(self) -> str:
        PyInstaller.__main__.run(
            [
                self.path_to_main,
                "--onefile",
                "--noconfirm",
                "--log-level",
                "ERROR",
                # "--noconsole", # windows option
                "--name",
                self.project_name,
                "--distpath",
                self.dist_path,
            ]
        )
        return self.executable_path

    def configure(self) -> str:
        """generates script executable and configures
        it to start along with the system

        Return:
            str: the path to the executable
        """
        executable_path = self.generate_executable()
        startup_handler = StartupHandler(self.executable_path, [])
        startup_handler.add_at_startup()
        return executable_path
