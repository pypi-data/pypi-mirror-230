from setuptools import setup

setup(
    name='sncscan',
    version='1.0.0',
    packages=[''],
    url='https://github.com/usdAG/sncscan',
    license='GPLv3',
    author='Jonas Wamsler, Nicolas Schickert',
    author_email='jonas.wamsler@usd.de',
    description='sncscan: Tool for analyzing SAP Secure Network Communications (SNC).',
    entry_points = {
        'console_scripts': [
            'sncscan = sncscan:main'
        ]
    }
    )

