from setuptools import setup

__project__ = "axelsolver"
__version__ = "0.0.2"
__description__ = "AxelSolver are a series of Solvers (classes) that run specific tasks, for example: VoiceSolver is for Text-to-Speech and NuclearSolver is for a KillSwitch website (just in case AI takes over.)"
__packages__ = ["axelsolver"]
__author__ = "NullDev (Naiel V)"
__install_requires__ = ["gtts", "requests", "pygame"]

setup(
    name = __project__,
    version = __version__,
    description = __description__,
    packages = __packages__,
    author = __author__,
    install_requires = __install_requires__,
)