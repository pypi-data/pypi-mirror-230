from typing import Dict, Any

from sphinx.application import Sphinx

from .builders import SphinxGlobalTOCJSONHTMLBuilder

__version__ = '0.1.5'


def setup(app: Sphinx) -> Dict[str, Any]:
    app.add_builder(SphinxGlobalTOCJSONHTMLBuilder, override=True)
    app.add_config_value("globaltoc_collapse", True, "env", [bool])

    return {
        'version': __version__,
        'parallel_read_safe': True
    }
