from distutils.util import convert_path
from pathlib import Path

from setuptools import setup, find_packages

package_name = 'api_compose'


def get_version():
    main_ns = {}
    path = convert_path('src/api_compose/version.py')
    with open(path) as file:
        exec(file.read(), main_ns)
    return main_ns['__version__']


def get_cli():
    main_ns = {}
    path = convert_path('src/api_compose/app.py')
    with open(path) as file:
        exec(file.read(), main_ns)
    return main_ns['__app__']


this_directory = Path(__file__).parent
long_description = this_directory.joinpath("README.rst").read_text()

if __name__ == '__main__':
    setup(
        name=package_name,
        version=get_version(),
        python_requires='>=3.9',
        description="A Framework for orchestrating, asserting and reporting on API calls with templates",
        long_description=long_description,
        long_description_content_type='text/x-rst',
        author="Ken",
        author_email="kenho811job@gmail.com",
        packages=find_packages("src"),
        package_dir={"": "src"},
        include_package_data=True,
        package_data = {
            # Recursively include data files
            '': ['**/*.yaml', '**/*.j2', '**/*.rst', '**/*.py'],
        },

        # include all core templates and value files
        install_requires=[
            "requests==2.29.0",
            "jsonpath_ng==1.5.3",
            "typer[all]==0.9.0",
            "jinja2==3.1.2",
            "pyyaml==6.0",
            "pydantic==2.0.3",
            "pydantic-settings==2.0.3",
            "networkx==3.1",
            "python-dotenv==1.0.0",
            "matplotlib==3.7.2",
            "lxml==4.9.3",
            "cmd2==2.4.3",
            "jsonschema==4.19.0",
        ],
        extras_require={
            "test": [
                "pytest==7.3.1",
                "pytest-env==1.0.1",
                # Mock REST server
                "connexion==2.14.2",
                "connexion[swagger-ui]",
                'pydeps==1.12.8',
                'dicttoxml==1.7.16',
            ],
            "dist": [
                'twine==4.0.2',
            ]
        },
        entry_points={
            'console_scripts': [
                f'{get_cli()}=api_compose.cli.main:app',
            ]
        },
    )
