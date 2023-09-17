import setuptools
from openai_pricing_calc_draft.version import Version


setuptools.setup(name='openai_pricing_calc_draft',
                 version=Version('0.1.1').number,
                 description='A starting template for Python programs',
                 #long_description=open('README.md').read().strip(),
                 author='M.Ali Koken',
                 author_email='ali@koken-consulting.com',
                 url='http://path-to-my-packagename',
                 py_modules=['openai_pricing_calc_draft'],
                 install_requires=[],
                 license='MIT License',
                 zip_safe=False,
                 keywords='boilerplate package',
                 #classifiers=['Packages', 'Boilerplate']
                 )
