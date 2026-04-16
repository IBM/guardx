Security Analysis
=================

GuardX provides a common interface for statically scanning Python code for safety and security issues.

Analysis can be invoked like so::
    result = guardx.Guardx().analyze(python_code, {AnalysisType.UNSAFE_CODE, AnalysisType.DETECT_SECRET})

AnalysisType.UNSAFE_CODE:
Runs `Bandit <https://bandit.readthedocs.io/en/latest/>`_ for static security analysis of Python code and identify security issues before execution.

AnalysisType.DETECT_SECRET:
Runs `detect-secrets <https://github.com/Yelp/detect-secrets>`_  checks for *secrets* in code.

By default, all tests in Bandit and detect-secrets are run. Details of the tests are listed below
and can be found on the respective project's website.

Bandit Tests `ref <https://bandit.readthedocs.io/en/latest/plugins/index.html>`_
---------------------------------------------------------------------------------

Bandit includes tests for various security vulnerabilities. Full list `here <https://bandit.readthedocs.io/en/latest/plugins/index.html#complete-test-plugin-listing>`_

**Injection Vulnerabilities**
  * SQL injection (B608)
  * Command injection via subprocess (B602, B603, B604, B605, B606, B607)
  * Shell injection (B601)
  * XML injection (B318, B320, B405, B406, B407, B408, B409, B410)

**Cryptographic Issues**
  * Weak cryptographic keys (B505)
  * Use of insecure hash functions (B303, B324)
  * Insecure random number generators (B311)
  * Hardcoded passwords and secrets (B105, B106, B107)

**Code Execution**
  * Use of exec() and eval() (B307, B102)
  * Pickle usage (B301, B302, B403, B404)
  * Import of dangerous modules (B401, B402, B403, B404, B405, B406, B407, B408, B409, B410, B411, B412, B413)

**File Operations**
  * Insecure temporary file usage (B108, B109, B110)
  * Path traversal vulnerabilities (B202)
  * Unsafe YAML loading (B506)

**Network Security**
  * SSL/TLS issues (B501, B502, B503, B504)
  * Binding to all network interfaces (B104)
  * Request without timeout (B113)

**Other Issues**
  * Assert usage in production (B101)
  * Try-except-pass patterns (B110)
  * Unsafe deserialization (B301, B302, B303, B304, B305, B306)

Configuration
-------------

Bandit can be configured using a ``.bandit`` configuration file or through command-line options.

Configuration File Format
~~~~~~~~~~~~~~~~~~~~~~~~~

Bandit supports YAML configuration files:

.. code-block:: yaml

    # .bandit configuration file
    
    # Tests to skip
    skips: ['B101', 'B601']
    
    # Tests to run (if specified, only these run)
    tests: ['B201', 'B301']
    
    # Paths to exclude from scanning
    exclude_dirs:
      - '/test'
      - '/build'
      - '/.venv'
    
    # Severity level threshold
    # Options: LOW, MEDIUM, HIGH
    severity: MEDIUM
    

Detect-Secrets
==============

**Secret Types**
  * API keys and tokens
  * Private keys (RSA, SSH, PGP)
  * AWS credentials
  * Azure connection strings
  * GitHub tokens
  * Slack tokens
  * Stripe API keys
  * Basic authentication credentials
  * High entropy strings (potential passwords/keys)
  * JWT tokens
  * NPM tokens
  * Database connection strings


Configuration
-------------

detect-secrets uses a ``.secrets.baseline`` file for configuration:

.. code-block:: json

    {
      "version": "1.4.0",
      "plugins_used": [
        {
          "name": "ArtifactoryDetector"
        },
        {
          "name": "AWSKeyDetector"
        },
        {
          "name": "Base64HighEntropyString",
          "limit": 4.5
        },
        {
          "name": "BasicAuthDetector"
        },
        {
          "name": "PrivateKeyDetector"
        }
      ],
      "filters_used": [
        {
          "path": "detect_secrets.filters.allowlist.is_line_allowlisted"
        }
      ],
      "results": {}
    }
