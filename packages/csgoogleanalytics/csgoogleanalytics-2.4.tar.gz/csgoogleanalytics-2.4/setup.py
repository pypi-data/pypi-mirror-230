from setuptools import setup, find_packages
import sys, os

version = "2.4"

setup(
    name="csgoogleanalytics",
    version=version,
    description=(
        "Google analyticseko gure webguneko datuak hileka edo asteka jasotzeko"
        " tresna"
    ),
    long_description="""\
""",
    classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords="",
    author="Jatsu Argarate",
    author_email="jargarate@codesyntax.com",
    url="",
    license="",
    packages=find_packages(exclude=["ez_setup", "examples", "tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "google-analytics-data == 0.17.0",
        "urllib3 == 1.26.12",
        "google-auth == 2.22.0",
        "protobuf == 4.24.3",
        "requests-oauthlib == 1.3.1",
        "jsonpickle == 3.0.2",
        "python-gflags == 3.1.2",
        "pytz == 2022.4",
        "django-object-actions == 4.1.0",
    ],
    entry_points="""
      # -*- Entry points: -*-
      """,
)
