# Copyright 2023 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#    https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.

"""Q-CTRL Sphinx Theme"""
import os

__version__ = "2.1.1"
__author__ = "Q-CTRL <support@q-ctrl.com>"

def setup(app):

    # See https://www.sphinx-doc.org/en/master/development/theming.html#distribute-your-theme-as-a-python-package
    app.add_html_theme(
        "qctrl_sphinx_theme", os.path.abspath(os.path.dirname(__file__))
    )

    # Check each DocSearch and Segment theme option for an available environment
    # variable and, if one exists, set it.
    environment_variables = [
        "DOCSEARCH_API_KEY",
        "DOCSEARCH_APP_ID",
        "DOCSEARCH_INDEX_NAME",
        "SEGMENT_WRITE_KEY",
    ]
    for variable in environment_variables:
        option = variable.lower()
        value = os.getenv(variable, "")
        if value != "":
            app.config.html_theme_options[option] = value
