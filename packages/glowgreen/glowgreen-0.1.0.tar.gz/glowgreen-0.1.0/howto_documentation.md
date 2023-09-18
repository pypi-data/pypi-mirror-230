# Instructions for generating documentation

Follow these instructions to generate the documentation from scratch, which is required if the **docs/source/** directory does not exist.

## Setting up

Install `sphinx`:

    python -m pip install sphinx

In the **docs** directory run

    sphinx-quickstart

and follow the prompts, e.g.:

    > Separate source and build directories (y/n) [n]: y
    > Project name: glowgreen
    > Author name(s): Jake Forster
    > Project release []:

Run *src/glowgreen_sample.py*.
Save the figures in **docs/source** with filenames *docs_cpat.png* and *docs_cpat_dose.png*.
Check the output still matches the content of *overview.rst*.
Copy *overview.rst* into **docs/source/**.

## Editing *conf.py*
Add the following to *docs/source/conf.py*.
At the top:

    import importlib.metadata
    import os
    import sys

    GLOWGREEN_VERSION = importlib.metadata.version("glowgreen")

    sys.path.insert(0, os.path.abspath('../..'))
    sys.path.insert(0, os.path.abspath('../../src/'))
    sys.path.insert(0, os.path.abspath('../../src/glowgreen/'))

Assign the copyright to SAMI and edit the version:

    release = GLOWGREEN_VERSION

Note the current version of `glowgreen` must be installed for the version to appear correctly here. 

Further down, add:

    extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon']

Document `__init__` by including:

    autoclass_content = 'both'

Choose this style:

    html_theme = 'classic'

## API reference

In the **docs** directory run:

    sphinx-apidoc -o ./source ../src/glowgreen/ -e -M

In *index.rst*, write 'overview' and 'modules' under toctree

Change heading in *modules.rst* to 'API reference'
and add '.. _API reference:' before the heading

in *glowgreen.close_contact.rst*, write ':private-members: _ContactPattern' under automodule

## Finish

In **docs** directory run:

    make html
