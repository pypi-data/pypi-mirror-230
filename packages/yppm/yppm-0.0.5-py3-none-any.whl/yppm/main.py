#!/usr/bin/env /usr/bin/python3
from typing import Any

import os
import sys
import platform
import json

from auto_everything.io import IO   
from auto_everything.disk import Disk
from auto_everything.python import Python
from auto_everything.terminal import Terminal, Terminal_User_Interface
from auto_everything.string import String


py = Python()
io_ = IO()
terminal = Terminal()
disk = Disk()
python_ = Python()
terminal_user_interface = Terminal_User_Interface()
string_tool = String()


class Tools():
    def __init__(self) -> None:
        # get static resource folder
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            #print('running in a PyInstaller bundle')
            def resource_path(relative_path: str) -> str:
                if hasattr(sys, '_MEIPASS'):
                    return os.path.join(sys._MEIPASS, relative_path) #type: ignore
                return os.path.join(os.path.abspath("."), relative_path)
            resource_basic_folder_path = resource_path(".")
        else:
            #print('running in a normal Python process')
            resource_basic_folder_path = disk.get_directory_path(__file__)
        self.resource_basic_folder_path = disk.join_paths(resource_basic_folder_path, 'resources').replace("/./", "/")

        # get python executable path
        self.host_python_executable_path = "python"
        if " 3." in terminal.run_command("python --version"):
            self.host_python_executable_path = "python"
        elif " 3." in terminal.run_command("python3 --version"):
            self.host_python_executable_path = "python3"

        # get git user email and username
        self.git_user_email = terminal.run_command("git config user.email").strip().split('\n')[0]
        self.git_user_name = terminal.run_command("git config user.name").strip().split('\n')[0].lower()
        if self.git_user_name == "":
            try:
                self.git_user_name = string_tool.remove_all_special_characters_from_a_string(os.getlogin(), white_list_characters='_').strip().lower()
            except Exception as e:
                print(e)
                self.git_user_name = ""
            if self.git_user_name == "":
                self.git_user_name = platform.system().lower().strip()

        # get project base folder
        self.project_root_folder = os.getcwd()

        # get virtual env folder
        self.virtual_env_folder = disk.join_paths(self.project_root_folder, ".venv")
        # self.env_activate_file_path = disk.join_paths(self.virtual_env_folder, "bin/activate")

        # get package json file
        self.package_json_file_path = disk.join_paths(self.project_root_folder, "package.json")
    
    def _add_to_gitignore(self, name: str):
        gitignore_path = disk.join_paths(self.project_root_folder, ".gitignore")
        if disk.exists(gitignore_path):
            text = io_.read(gitignore_path)
            if name not in text:
                text = f"{name}\n" + text 
                io_.write(gitignore_path, text)
        else:
            text = name
            io_.write(gitignore_path, text)

    def _create_virtual_env(self):
        if disk.exists(self.virtual_env_folder):
            return
        
        print(f"Creating virtual envirnoment by using '{self.host_python_executable_path}'...")

        terminal.run(f"""
        {self.host_python_executable_path} -m venv {self.virtual_env_folder}
                     """)

        # change permission of activate file
        # terminal.run(f"""chmod 777 {self.env_activate_file_path}""")
        
        # ignore .venv folder
        self._add_to_gitignore(".venv/")
    
    def _get_virtual_env_python_excutable_path(self):
        self._create_virtual_env()

        return disk.join_paths(self.virtual_env_folder, "bin", "python3")

    def _get_virtual_env_pip_path(self):
        self._create_virtual_env()

        return disk.join_paths(self.virtual_env_folder, "bin", "pip3")

    def _hack_into_virtual_env_bash_command(self):
        self._create_virtual_env()

        the_bin_path = disk.join_paths(self.virtual_env_folder, "bin")

        return f"""
        export PATH="{the_bin_path}:$PATH"
        """.strip()
    
    def _get_package_json_object(self) -> Any:
        try:
            text = io_.read(self.package_json_file_path)
            lines = []
            for line in text.split("\n"):
                if line.strip().startswith("#") or line.strip().startswith("//"):
                    #ignore comments
                    pass
                else:
                    lines.append(line)
            text = "\n".join(lines)
            json_object = json.loads(text)
            return json_object
        except Exception as e:
            print(e)
            return None
    
    def create_a_new_project(self):
        global default_template_name, default_project_name

        # select teplates
        default_template_name = "basic_python_project"
        default_template_name = terminal_user_interface.selection_box(
            "Which project template you want to use? ", [
                ("basic python project", None),
                # ("backend and frontend project", set_to_backend_and_frontend_project)
            ]
        )

        # handle project name
        default_project_name = ""

        def assign_name(text: str):
            global default_project_name
            text = text.strip()
            if text == "":
                print("You can't give me an empty name!")
                exit()
            default_project_name = text

        terminal_user_interface.input_box(
            f"\n\nPlease give me the new project name: ", 
            default_value=default_project_name,
            handle_function=assign_name
        )

        # copy template folder
        project_path = disk.join_paths(disk.get_current_working_directory(), default_project_name)
        disk.delete_a_folder(project_path)
        if default_template_name == "basic_python_project":
            source_folder_path = disk.join_paths(self.resource_basic_folder_path, "basic_python_project")
            disk.copy_a_folder(source_folder_path=source_folder_path, target_folder_path=project_path)

            os.chdir(project_path)
            self.__init__()

            self.init(name=default_project_name)

            print(f"\n\nNow you could go to the new project by using: \ncd {default_project_name}")
        elif default_project_name == "backend_and_frontend_project":
            pass

    def init(self, name: str = ""):
        # create package.json file in current folder if there does not have one
        if disk.exists(self.package_json_file_path):
            print("There already has a 'package.json' file.")
        else:
            json_content = """
            {
                "name": "",
                "version": "",
                "author": "",
                "main": "main.py",
                "scripts": {},
                "dependencies": [
                    "auto_everything"
                ]
            }
            """
            package_object = json.loads(json_content)
            print("\n")

            # handle project name
            name = name.strip()
            if name == "":
                default_project_name = disk.get_directory_name(self.project_root_folder)
                def assign_name(text: str):
                    package_object["name"] = text.strip()
                terminal_user_interface.input_box(
                    f"Please give me a project name (default '{default_project_name}'): ", 
                    default_value=default_project_name,
                    handle_function=assign_name
                )
            else:
                package_object["name"] = name

            # handle project version
            default_project_version = "0.0.0"
            def assign_version(text: str):
                package_object["version"] = text.strip()
            terminal_user_interface.input_box(
                f"Please give me a project version (default '{default_project_version}'): ", 
                default_value=default_project_version,
                handle_function=assign_version
            )

            # handle author name
            default_author = self.git_user_email
            if "@" not in default_author:
                default_author = "" 
            def assign_author(text: str):
                package_object["author"] = text.strip()
            terminal_user_interface.input_box(
                f"Please give me your name (default '{default_author}'): ", 
                default_value=default_author,
                handle_function=assign_author
            )

            io_.write(self.package_json_file_path, json.dumps(package_object, indent=4))
            self._create_virtual_env()

            self.install()

            main_py_file_path = disk.join_paths(self.project_root_folder, "main.py")
            if not disk.exists(main_py_file_path):
                io_.write(main_py_file_path, 'print("Hello World!")')

    def run(self, script_name: str = ""):
        if not disk.exists(self.package_json_file_path):
            print("You have to run `yppm init` first.")
            return
        self._create_virtual_env()

        package_object = self._get_package_json_object()

        scripts = package_object.get("scripts")
        if scripts == None:
            print('package.json should have a key called {"scripts": {}}')
            return

        entry_point_python_script = package_object.get("main")
        if entry_point_python_script == None:
            print('package.json should have a key called {"main": "main.py"}')
            return

        script_name = script_name.strip()
        if script_name == "":
            # {self.env_activate_file_path}
            terminal.run(f"""
            {self._hack_into_virtual_env_bash_command()}

            {self._get_virtual_env_python_excutable_path()} {entry_point_python_script}
                         """)
        elif script_name == "?":
            if len(scripts.keys()) == 0:
                print("There has no scripts to run.")
            else:
                selections = []
                for script_name in scripts.keys():
                    selections.append(
                        (f'{script_name}', lambda: script_name.strip())
                    )
                selection = terminal_user_interface.selection_box(
                    "Which script you want to run?", 
                    selections
                )
                if selection in scripts.keys():
                    terminal.run(f"{scripts[selection]}")
        else:
            if script_name in scripts.keys():
                # {self.env_activate_file_path}
                terminal.run(f"""
                {self._hack_into_virtual_env_bash_command()}

                {scripts[script_name]}
                            """)
            else:
                print(f"Sorry, script '{script_name}' not exists in the package.json")

    def _install_package(self, package_name: str, upgrade: bool = False):
        pip_path = self._get_virtual_env_pip_path()

        yes_exists = terminal.run_command("yes --version")
        if ("copyright" in yes_exists.strip().lower()):
            yes_exists = True
        else:
            yes_exists = False

        if upgrade == False:
            # {self.env_activate_file_path}
            terminal.run(f"""
            {self._hack_into_virtual_env_bash_command()}
            yes | {pip_path} install {package_name}
                        """)
        else:
            # {self.env_activate_file_path}
            terminal.run(f"""
            {self._hack_into_virtual_env_bash_command()}
            yes | {pip_path} install {package_name} --upgrade
                        """)

    def _uninstall_package(self, package_name: str):
        pip_path = self._get_virtual_env_pip_path()

        # {self.env_activate_file_path}
        terminal.run(f"""
        {self._hack_into_virtual_env_bash_command()}
        {pip_path} uninstall {package_name} -y
                        """)

    def install(self, package_name: str = ""):
        if not disk.exists(self.package_json_file_path):
            print("You have to run `yppm init` first.")
            return
        self._create_virtual_env()

        package_object = self._get_package_json_object()

        dependencies = package_object.get("dependencies")
        if dependencies == None:
            print('package.json should have a key called {"dependencies": []}')
            return

        package_name = package_name.strip()
        if package_name == "":
            # install all package
            for package_name in dependencies:
                self._install_package(package_name=package_name)
        else:
            # install one package
            if package_name not in dependencies:
                # install once
                self._install_package(package_name=package_name)
            else:
                # install again
                self._install_package(package_name=package_name, upgrade=True)
            
            if package_name not in dependencies:
                package_object["dependencies"].append(package_name)
                io_.write(self.package_json_file_path, json.dumps(package_object, indent=4))

    def uninstall(self, package_name: str = ""):
        if not disk.exists(self.package_json_file_path):
            print("You have to run `yppm init` first.")
            return
        self._create_virtual_env()

        package_object = self._get_package_json_object()

        dependencies = package_object.get("dependencies")
        if dependencies == None:
            print('package.json should have a key called {"dependencies": []}')
            return

        package_name = package_name.strip()
        if package_name == "":
            pass
        else:
            if package_name not in dependencies:
                pass
            else:
                self._uninstall_package(package_name=package_name)
            
            if package_name in dependencies:
                package_object["dependencies"] = [one for one in package_object["dependencies"] if one != package_name]
                io_.write(self.package_json_file_path, json.dumps(package_object, indent=4))

    def build(self, pyinstaller_arguments: str = ""):
        package_object = self._get_package_json_object()

        name = package_object.get("name")
        if name == None:
            print('package.json should have a key called {"name": "your_app_name"}')
            return

        entry_point_python_script = package_object.get("main")
        if entry_point_python_script == None:
            print('package.json should have a key called {"main": "main.py"}')
            return

        self._add_to_gitignore(".build/")
        self._add_to_gitignore(".dist/")
        self._add_to_gitignore("*.spec")

        terminal.run(f"""
        {self._hack_into_virtual_env_bash_command()}

        export PIP_BREAK_SYSTEM_PACKAGES=1
        {self._get_virtual_env_python_excutable_path()} -m pip install pyinstaller

        {self._get_virtual_env_python_excutable_path()} -m PyInstaller {entry_point_python_script} --noconfirm --onefile {pyinstaller_arguments} --hidden-import auto_everything --name {name}
                     """)

    def clean(self):
        disk.delete_a_folder(self.virtual_env_folder)
        disk.delete_a_folder("./build")
        disk.delete_a_folder("./dist")
        terminal.run(f"""
        rm -fr *.spec
                     """)

    # def env(self):
    #     print(f""" Please run:\n\n{self.env_activate_file_path} """.strip())

    def about(self):
        terminal.run("clear")
        print("""
YPPM: Yingshaoxo Python Package Manager. 
              
(yingshaoxo is my name)
        """.strip())


try:
    py.fire2(Tools)
except Exception as e:
    pass
