# yppm
Yingshaoxo Python Package Manager

## Install
```bash
python3 -m pip install yppm --break-system-packages
alias yppm="python3 -m yppm"

yppm about
```

or

```bash
# sudo su
# wget https://github.com/yingshaoxo/yppm/raw/main/Install.sh -O - | sudo bash


Fuck the github because they banned my github account for no clear reason, when you visit "https://github.com/yingshaoxo/yppm", you'll only see 404 page.
```

## Usage
### Init a project
```bash
cd <your_project_folder>
yppm init
```

### Install a package
```bash
yppm install auto_everything
```

### Install all package
```bash
yppm install
```

### Run a script in package.json
```bash
yppm run ?
```

or 

```bash
yppm run <script_name>
```

### Build a project
```bash
yppm build
```

## Feature
### Finished
* npm package.json like syntax.
* Can compile a python project into a single binary file.
### Not Finished
* Has a backend and frontend template built_in (similar to SpringBoot).
* Built in python binary files that will never upgrade, and free to use offline
* File_path based relative import supporting. (`import * as x from './lib.py'`)

## Based on
* venv: https://packaging.python.org/en/latest/key_projects/#standard-library-projects
* auto_everything