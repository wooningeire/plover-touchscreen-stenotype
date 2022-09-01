from distutils.core import setup
import setuptools
from plover_build_utils.setup import BuildPy, BuildUi

BuildPy.build_dependencies.append("build_ui")
BuildUi.hooks = ["plover_build_utils.pyqt:fix_icons"]

setuptools.setup(cmdclass={
    "build_py": BuildPy,
    "build_ui": BuildUi,
})