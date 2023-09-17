from setuptools import find_packages, setup

setup(
    name='openai_pricing_calc_draft',
                 version='0.2.4',
                 description='Pricing Calc for OpenAI API',
                 author='M.Ali Koken',
                 author_email='ali@koken-consulting.com',
                 url='https://github.com/kokenconsulting/openai-api-pricing',
                 python_requires='>=3.6',
                 packages=find_packages("src/"),
                 #classifiers=['Packages', 'Boilerplate']
                 )
