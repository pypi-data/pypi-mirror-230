import os.path
import shutil
import sys
from argparse import ArgumentParser, Namespace

import jinja2

from ..command import Command


class Init(Command):

    NAME = "init"
    HELP = "initialize a new project in the current directory"
    ASYNC_RUN = False

    _quiet: bool = False
    _overwrite: bool = False
    _project_name: str = None

    def init_argument_parser(self, parser: ArgumentParser) -> None:
        parser.add_argument("name", nargs=1, help="project name")
        parser.add_argument("-q", "--quiet", action="store_true", default=False, help="disable progress messages")
        parser.add_argument("-w", "--overwrite", action="store_true", default=False,
                            help="overwrite files and directories if they exist")

    async def setup(self, args: Namespace) -> None:
        self._quiet = args.quiet
        self._overwrite = args.overwrite
        self._project_name = args.name[0]

    def process_directory(self, dir_name: str):
        processed_files = set()

        curr_dir = os.path.abspath(os.curdir)
        for src_filename in os.listdir(dir_name):
            if src_filename == "__pycache__" or src_filename.endswith(".pyc"):
                continue

            tmpl_attrs = {"project_name": self._project_name}

            target_filename = src_filename
            full_src_filename = os.path.join(dir_name, src_filename)

            if os.path.isdir(full_src_filename):
                new_dir = os.path.join(curr_dir, target_filename)
                if new_dir in processed_files:
                    continue

                processed_files.add(new_dir)

                if not self._quiet:
                    print(f"creating new directory {new_dir}")

                create_dir = True
                if os.path.isdir(new_dir):
                    print(f"file or directory {new_dir} already exists")
                    if self._overwrite:
                        create_dir = False
                    else:
                        sys.exit(1)

                if create_dir:
                    os.makedirs(new_dir)

                if not self._quiet:
                    print(f"jumping into {new_dir}")
                os.chdir(new_dir)
                self.process_directory(full_src_filename)
                if not self._quiet:
                    print(f"jumping back into {curr_dir}")
                os.chdir(curr_dir)
            else:
                is_template = False
                new_filename = os.path.abspath(os.path.join(curr_dir, target_filename))

                if new_filename.endswith(".tmpl"):
                    new_filename = new_filename[:-5]
                    is_template = True

                if new_filename in processed_files:
                    continue

                processed_files.add(new_filename)

                if os.path.exists(new_filename) and not self._overwrite:
                    print(f"file or directory {new_filename} already exists")
                    sys.exit(1)

                if not self._quiet:
                    print(f"copying {full_src_filename} to {new_filename}")

                if is_template:
                    with open(full_src_filename) as f:
                        tmpl = jinja2.Template(f.read())
                    with open(new_filename, "w") as f:
                        f.write(tmpl.render(tmpl_attrs))
                else:
                    shutil.copy(full_src_filename, new_filename)
        os.chmod("crcmd.py", 0o755)

    def run_sync(self) -> None:

        init_command_dir = os.path.dirname(__file__)
        croydon_dir = os.path.abspath(os.path.join(init_command_dir, ".."))
        templates_dir = os.path.join(croydon_dir, "templates")
        if not self._quiet:
            print(f"using templates directory {templates_dir}")
        self.process_directory(templates_dir)
