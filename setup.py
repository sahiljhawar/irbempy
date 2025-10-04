"""Custom setup.py to install IRBEM Fortran library before building the Python package."""

import subprocess
import os
import sys
from pathlib import Path
import shutil
from setuptools import setup
from setuptools.command.build_py import build_py


class CustomBuild(build_py):
    """Custom build command that builds IRBEM before building Python package."""

    def run(self):
        self.build_irbem()
        super().run()

    def build_irbem(self):
        print("=" * 60)
        print("Building IRBEM Fortran library...")
        print("=" * 60)

        try:
            if os.path.exists(".irbem-temp"):
                self._clean_irbem()

            self._clone_IRBEM()
            self._compile_and_install_irbem()
            self._clean_irbem()
        except subprocess.CalledProcessError as e:
            print(f"✗ Build failed with return code {e.returncode}")
            print(f"Command: {' '.join(e.cmd)}")
            sys.exit(1)
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            sys.exit(1)

    def _clone_IRBEM(self):
        print("Initializing IRBEM ...")
        subprocess.check_call(
            ["git", "clone", "https://github.com/PRBEM/IRBEM.git", ".irbem-temp"]
        )

    def _get_fortran_compiler_darwin(self):
        try:
            fc = subprocess.check_output(
                ["bash", "-c", "compgen -c gfortran | sort -V | tail -n1"], text=True
            ).strip()
            fc = fc if fc else "gfortran"
        except subprocess.CalledProcessError:
            fc = "gfortran"

        return fc

    def _compile_and_install_irbem(self):
        print("Installing IRBEM library...")
        if sys.platform == "darwin":
            fc = self._get_fortran_compiler_darwin()
            base_cmd = ["make", "OS=osx64", f"FC={fc}", f"LD={fc}"]
            subprocess.check_call(base_cmd + ["all"], cwd=".irbem-temp")
            subprocess.check_call(base_cmd + ["install"], cwd=".irbem-temp")
        else:
            subprocess.check_call(["make"], cwd=".irbem-temp")
            subprocess.check_call(["make", "install", "."], cwd=".irbem-temp")

        shutil.copy2(
            ".irbem-temp/libirbem.so",
            Path(__file__).parent,
        )

    def _clean_irbem(self):
        print("Cleaning up IRBEM build files...")
        shutil.rmtree(".irbem-temp", ignore_errors=True)


with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="IRBEM",
    description="Python wrapper for IRBEM",
    author="Mykhaylo Shumko",
    author_email="msshumko@gmail.com",
    url="https://sourceforge.net/projects/irbem/",
    packages=["IRBEM"],
    include_package_data=True,
    python_requires=">=3.11",
    cmdclass={"build_py": CustomBuild},
    install_requires=required,
    version="0.1.0",
)
