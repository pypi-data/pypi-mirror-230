
from rich.console import Console
from rich.markdown import Markdown

MARKDOWN = """
# The PLATO Camera Test Script

The test scripts provide commanding and analysis functions to perform camera testing 
and data analysis of all data acquired during PLATO Camera alignment at CSL and the 
PLATO Camera Thermal Vacuum Tests at IAS, INTA and SRON.

Please use the following links:

* https://ivs-kuleuven.github.io/plato-cgse-doc/ for the full documentation
* https://github.com/IvS-KULeuven/plato-test-scripts/ for the source code

The following commands are available for testing your installation:

* python -m camtest.version        : display information about the version of TS you are using

"""

console = Console(width=100)
md = Markdown(MARKDOWN)
console.print(md)
