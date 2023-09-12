# from setuptools import setup, find_packages
# import sys
#
# for arg in sys.argv:
#     if arg == "upload" or arg == "register":
#         print("Package not intended for publication.")
#         sys.exit(-1)
#
#
# test_deps = [
#     'pytest',
#     'scipy',
# ]
# extras = {
#     'test': test_deps,
# }
#
#
# setup(
#     name="asl_utility",
#     version="0.0.2-alpha",
#     author="Autonomous Systems Lab",
#
#     packages=find_packages(include=('asl_utility*',)),
#
#     python_required='>=3.7',
#     install_requires=[
#         'numpy >=1.21.0',
#         'typing-extensions >=4.4.0, ==4.4.*'
#     ],
#     tests_require=test_deps,
#     extras_require=extras,
#
# )

import setuptools

if __name__ == '__main__':
    setuptools.setup()
