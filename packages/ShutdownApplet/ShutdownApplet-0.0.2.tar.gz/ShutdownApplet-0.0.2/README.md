# Shutdown Timer

This Applet does nothing more than scheduling a system shutdown according to the entered time.
Increase and decrease the timer value with the mouse wheel, start and stop the timer via left click.

Additions welcome!
  - different colors
  - cli options
  - OSX support

Todo:
  - window icon (shutdown button merged with clock dial)
  - linux support
  - support for dark themes

## Installation

    python3 -m pip install ShutdownApplet

### Troubleshooting
pip likely installs to your local path, which is not included by default. Try adding .local/bin to your path:

    echo export PATH=$HOME/usr/local/bin:$PATH >> .bashrc && source .bashrc

## Releasing a new version to PyPI
Consider testing the release on test.pypi.org first!

    # clone the repo
    git clone https://github.com/tobiglaser/ShutdownApplet.git

    # install locally
    python3 -m pip install .

    #test
    ShutdownApplet
    
    # build the package
    export PYTHONIOENCODING=utf-8  # because it complaines otherwise
    python3 -m build

    # upload to PyPI
    twine upload dist/*

    # clean up before next upload
    rm dist/*

### More packaging info:
[testpypi](https://packaging.python.org/en/latest/guides/using-testpypi/)

[packaging projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/)

[CI/CD ?](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)