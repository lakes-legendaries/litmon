from setuptools import find_packages, setup


if __name__ == '__main__':
    setup(

        # standard info
        name='litmon',
        version='0.0.4',
        description='literature monitoring project',
        author='Mike Powell PhD',
        author_email='mike@lakeslegendaries.com',

        # longer info
        long_description=open('README.rst').read(),
        license=open('LICENSE').read(),

        # packages to include
        packages=find_packages(),

        # requirements
        install_requires=[],
        python_requires='>=3.9',
    )
