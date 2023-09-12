from setuptools import setup

name = "types-requests-oauthlib"
description = "Typing stubs for requests-oauthlib"
long_description = '''
## Typing stubs for requests-oauthlib

This is a PEP 561 type stub package for the `requests-oauthlib` package. It
can be used by type-checking tools like
[mypy](https://github.com/python/mypy/),
[pyright](https://github.com/microsoft/pyright),
[pytype](https://github.com/google/pytype/),
PyCharm, etc. to check code that uses
`requests-oauthlib`. The source for this package can be found at
https://github.com/python/typeshed/tree/main/stubs/requests-oauthlib. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/main/README.md for more details.
This package was generated from typeshed commit `32535ee8952dffecbe7a9fd04e5ed8ba0f1c8da2` and was tested
with mypy 1.5.1, pyright 1.1.326, and
pytype 2023.8.31.
'''.lstrip()

setup(name=name,
      version="1.3.0.0",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/requests-oauthlib.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=['types-oauthlib', 'types-requests'],
      packages=['requests_oauthlib-stubs'],
      package_data={'requests_oauthlib-stubs': ['__init__.pyi', 'compliance_fixes/__init__.pyi', 'compliance_fixes/douban.pyi', 'compliance_fixes/ebay.pyi', 'compliance_fixes/facebook.pyi', 'compliance_fixes/fitbit.pyi', 'compliance_fixes/instagram.pyi', 'compliance_fixes/mailchimp.pyi', 'compliance_fixes/plentymarkets.pyi', 'compliance_fixes/slack.pyi', 'compliance_fixes/weibo.pyi', 'oauth1_auth.pyi', 'oauth1_session.pyi', 'oauth2_auth.pyi', 'oauth2_session.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
