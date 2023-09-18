from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.3.1'
DESCRIPTION = 'LLM Cost Calculation'
LONG_DESCRIPTION = 'A package that helps calculate costs for LLMs. Only OPEN AI is avaialble.'

# Setting up
setup(
    name="openai_pricing_calc_draft",
    version=VERSION,
    author="Koken Consultng",
    author_email="<ali@koken-consulting.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    url = "https://github.com/kokenconsulting/openai-api-pricing/tree/main/pypi",
    packages=find_packages(),
    install_requires=["requests"],
    keywords=['python', 'video', 'stream', 'video stream', 'camera stream', 'sockets'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)