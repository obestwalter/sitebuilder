"""
pip install -e /path/to/here
"""

from setuptools import setup


with open("requirements.txt") as f:
    requirements = f.readlines()

setup(
    name='Sitebuilder',
    description='Build static sites with Flask and FlatPages',
    version='indefinite-development',
    license='BSD',
    url='http://github.com/obestwalter/sitebuilder/',
    author='Oliver Bestwalter',
    author_email='oliver@bestwalter.de',
    long_description='',
    packages=['sitebuilder'],
    include_package_data=True,
    zip_safe=False,
    platforms='Unix',
    install_requires=requirements,
    entry_points=dict(console_scripts=['sibu=sitebuilder.sitebuilder:main']),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
