from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("VERSION", "r") as version_file:
    version = version_file.read().strip()

setup(
    name='get_user_agent_pls',
    version=version,
    author='David Hooton',
    author_email='get_user_agent_pls@hooton.org',
    description='A package to fetch get-user-agent strings',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/djh00t/get-user-agent-pls',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests',
        'beautifulsoup4',
    ],
    entry_points={
        'console_scripts': [
            'get_user_agent_pls=get_user_agent_pls.get_user_agent_pls:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
