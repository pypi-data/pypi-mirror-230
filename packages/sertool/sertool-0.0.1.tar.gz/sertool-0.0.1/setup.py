
from setuptools import setup

from sertool import __version__

setup(
    name='sertool',
    packages=['sertool'],
    setup_requires=['setuptools_scm'],
    version=__version__,
    license='MIT',
    author='Adrian Rothenbuhler',
    author_email='adrian@redhill-embedded.com',
    description='Serial Port Helper Tool',
    keywords='Serial port',
    url='https://github.com/redhill-embedded/sertool.git',
    download_url='https://github.com/redhill-embedded/sertool/archive/v_010.tar.gz',
    package_data={
        "sertool": [
            "package_version"
        ]
    },
    python_requires=">=3.8",
    install_requires=["pyserial"],
    entry_points={
        "console_scripts": [
            "sertool=sertool.__main__:main",
        ]
    },
)