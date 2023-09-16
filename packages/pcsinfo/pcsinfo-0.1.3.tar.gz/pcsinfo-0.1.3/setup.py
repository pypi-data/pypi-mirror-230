from setuptools import setup

setup(
    name="pcsinfo",
    version='0.1.3',
    description='A easy module for obtaining information about a PC',
    packages=['pcsinfo'],
    author_email='sasaigrypocta@gmail.com',
    author="barlin41k",
    zip_safe=False,
    long_description="""
# News of updates
#### Fix bugs 0.1.3
- Fixed bug in `__init__.py`

# pcsinfo - what is this?
`pcsinfo` **- a module for obtaining information about the computer and computer users. It has a clear interface, thanks to which there is no need to delve into the module.**

- **Examples and more in the [GitHub](https://github.com/barlin41k/pcsinfo)**
""",
    long_description_content_type="text/markdown",
    url="https://github.com/barlin41k/pcsinfo",
    project_urls={
        "GitHub": "https://github.com/barlin41k/pcsinfo",
    })