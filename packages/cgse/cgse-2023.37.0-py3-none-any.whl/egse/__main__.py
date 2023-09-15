
from rich.console import Console
from rich.markdown import Markdown

MARKDOWN = """
# The Common-EGSE for the PLATO Camera Test

The Common-EGSE provides a framework to perform the PLATO Camera alignment at CSL and 
the PLATO Camera Thermal Vacuum Tests at IAS, INTA and SRON.

Please use the following links:

* https://ivs-kuleuven.github.io/plato-cgse-doc/ for the full documentation
* https://github.com/IvS-KULeuven/plato-common-egse/ for the source code

The following commands are available for testing your installation:

* python -m egse.version        : display information about the version of the CGSE you are using
* python -m egse.settings       : display the settings as they will be used by CGSE commands
* python -m egse.setup          : display the latest Setup that is known for your site
* python -m egse.setup --use-cm : display the Setup that is currently loaded in the 
  configuration manager
* python -m egse.system         : display some basic information about your system
* python -m egse.env            : display the environment variables [--full]
* python -m egse.resource       : display the default resources and their location

You can download a cheat sheet for the Common-EGSE from: ...
"""

console = Console()
md = Markdown(MARKDOWN)
console.print(md)
