from setuptools import setup

# import logging

# logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
# log = logging.getLogger(__name__)

# with open("src/dmtoolkit/__init__.py", "r") as vptr:
#     version_text = vptr.readlines()

#     log.info(f"Version text: {version_text}")

#     version_str = version_text[0]
#     version = version_str.split("=")[1].strip().strip('"')
#     vno_parts = version.split(".")
#     major_vno = int(vno_parts[0])
#     minor_vno = int(vno_parts[1])
#     incremental_vno = int(vno_parts[-1])
#     update_vno = incremental_vno + 1
#     new_version_text = f"""
#     __version__ = "{major_vno}.{minor_vno}.{update_vno}"
#         {"/n".join(version_text[1:])}
#     """

# with open("src/dmtoolkit/__init__.py", "w") as vptr:
#     vptr.write(new_version_text)

setup()
