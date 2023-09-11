# uunIot Framework

- for newest information and documentation, see [UuBookKit](https://uuapp.plus4u.net/uu-bookkit-maing01/38c7532545984b3797c5719390b523a8/book/page?code=71150832)
- for quick start, see `examples/` folder inside this repository and *Getting started* in the aforementioned BookKit.

## Documentation

- the code is auto-documented, meaning that documentation can be automatically generated from comments in the code and the code itself

- the documentation needs to be generated first. To do this, first install [Sphinx](https://www.sphinx-doc.org/en/master/usage/installation.html) and then install the [ReadTheDocs theme](https://github.com/readthedocs/sphinx_rtd_theme).
- see Sphinx documentation in `docs` and `docs-dev` for user and library-developer documentation respectively. HTML output is present in `build/html` subdirectories.

## Testing

- create virtual environment for all uun applications, if you want to test your local version of library, otherwise create separate environments for each application and the library
    - `python3 -m venv env`
    - `. env/bin/activate`
    - cd to library directory (directory where is setup.py)
    - `pip3 install -e .`
    - cd to application directory
    - `pip3 install -e .`
    - install pytest `pip3 install pytest`
    - reactivate environment `deactivate && . env/bin/activate`
- `cd` to main repository directory of the project you want to test and run `pytest`
- `pytest --log-cli-level=DEBUG` for additional information and with lib logger output
- testing involves
	- static phase - test basic observations that should hold about the structure of certain objects
	- dynamic phase - try modules' functionality: heartbeat and config updating
        - config updating can be turned on/off in `tests/conftest.py`, also be sure to introduce change in server configuration with respect to config file `tests/config.json`

## Versioning

- 0.#.#
	- initial releases changing rapidly

