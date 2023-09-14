from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.3'
DESCRIPTION = "GoodError is a Python library that enhances exception handling, including integration with GPT-3 for additional context."

LONG_DESCRIPTION = """
GoodError is a Python library that improves the way exceptions are handled in your code. It provides a custom exception handler that can enhance the output of exceptions and even send them to GPT-3 for additional context. This can help you better understand and debug issues in your code.

Key Features:
- Enhanced exception messages
- Integration with GPT-3 for context
- Easy to use and integrate into your projects

For more information, please visit the [GitHub repository](https://github.com/TeaByte/GoodError).
"""


setup(
    name="gooderror",
    version=VERSION,
    author="01270",
    author_email="yazanemails@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['openai'],
    keywords=["exception handling", "GPT-3", "Python library"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ],
    url='https://github.com/TeaByte/GoodError/',
    project_urls={
        'Source': 'https://github.com/TeaByte/GoodError/',
        'Bug Reports': 'https://github.com/TeaByte/GoodError/issues',
        'Documentation': 'https://github.com/TeaByte/GoodError/'
    },
)
