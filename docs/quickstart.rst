Quick start
###########

To install the library, choose one of the following methods:

**git+https** using a `github personal access token <https://help.github.com/articles/creating-an-access-token-for-command-line-use/>`_:

.. code-block:: bash

  pip install guardx@git+https://${GITHUB_TOKEN}@https://github.com/ibm/guardx.git@${GUARDX_VERSION}

**git+ssh**:

.. code-block:: bash

  pip install guardx@git+ssh://git@github.com/ibm/guardx.git@${GUARDX_VERSION} 

**git clone**:

.. code-block:: bash

  git clone git@github.com:ibm/guardx.git
  make -C guardx install
Initialization
**************

The library container images must be built before importing and using the library.

.. code-block:: bash

  guardx init #sudo .venv/bin/guardx init

Library Usage
=============

Here is an example of how to use this library in your code.

.. code-block:: python

  from guardx import Guardx
  from guardx.analysis import AnalysisType

  python_code = """<your code here>"""

  g = Guardx(config_path="./resources/config.yaml")

To analyze code
===============

.. code-block:: python

  result = g.analyze(python_code, {AnalysisType.DETECT_SECRET, AnalysisType.UNSAFE_CODE})
  print(result)

To execute code in sandbox with a default security policy
=========================================================

.. code-block:: python

  result = g.execute(python_code).get_docker_result()
  print(result)
