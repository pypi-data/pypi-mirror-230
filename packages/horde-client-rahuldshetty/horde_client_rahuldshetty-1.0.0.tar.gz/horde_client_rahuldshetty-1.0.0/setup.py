from distutils.core import setup

requirements = [
    'requests==2.27.1',
    'pydantic==2.3.0'   
]

setup(
    name='horde-client',
    version='1.0',
    description='Python Interface for AIHorde',
    author='Rahul D Shettu',
    author_email='35rahuldshetty@gmail.com',
    url='https://github.com/rahuldshetty/horde-client.git',
    install_requires=requirements,
    packages=['horde_client', 'examples'],
)