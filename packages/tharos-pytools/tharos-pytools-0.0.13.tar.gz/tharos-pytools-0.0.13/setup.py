from setuptools import setup
setup(
    name='tharos-pytools',
    version='0.0.13',
    description='Collection of quality-of-life functions',
    url='https://github.com/Tharos-ux/tharos-pytools',
    author='Tharos',
    author_email='dubois.siegfried@gmail.com',
    license='MIT',
    packages=['tharospytools'],
    zip_safe=False,
    install_requires=['matplotlib', 'mycolorpy', 'resource', 'rich']
)
