# from distutils.core import setup
from setuptools import setup

setup(
    name='mozark_sdk',
    packages=['mozark_sdk'],
    version='2.0',
    license='MIT',
    description='Automation test APIs',
    author='Mozark',
    author_email='mozark-aws-staging@mozark.ai',
    url='https://mozark.ai',
    # download_url='https://github.com/user/reponame/archive/v_01.tar.gz',  # I explain this later on
    # long_description_content_type = "text/markdown",
    keywords=['MOZARK', 'AUTOMATION', 'EXPERIENCE'],
    install_requires=[
        'configparser==5.3.0',
        'requests==2.28.1'
    ],
    description_file='README.md',
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3',  # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
