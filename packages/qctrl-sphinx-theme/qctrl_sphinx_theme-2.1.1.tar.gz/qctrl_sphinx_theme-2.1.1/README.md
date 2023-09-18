# Q-CTRL Sphinx Theme

The Q-CTRL Sphinx Theme is a very opinionated [Sphinx](https://www.sphinx-doc.org/) theme intended for use with public [Q-CTRL Documentation](https://docs.q-ctrl.com/) websites such as the [Q-CTRL Python package](https://docs.q-ctrl.com/boulder-opal/references/qctrl/).

## Installation

1. Install the Q-CTRL Sphinx Theme package.
    ```shell
    pip install qctrl-sphinx-theme
    ```
1. Add `qctrl-sphinx-theme` as a dev dependency in your `pyproject.toml` file.
1. Add the following to your project’s `conf.py` file:
    ```python
    html_theme = "qctrl_sphinx_theme"
    ```

## Configuration

The Q-CTRL Sphinx Theme requires no configuration and there is no need to set any `html_thene_options` in your project’s `conf.py` file. The theme will automatically set all necessary theme options and will update any theme option with an available environment variable if one exists.
