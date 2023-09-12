from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='cfclon',
    version='0.1',
    description='Complex functions course character cloning project',
    keywords='barycentric coordinates, mean value coordinates, harmonic coordinates',
    author='Samy Zafrany',
    #url='https://github.com/samyzaf/notebooks/blob/main/fa2.ipynb',
    author_email='sz@samyzaf.com',
    license='MIT',
    packages=['cfclon'],
    install_requires=['numpy', 'matplotlib'],
    zip_safe=False,
)

