from setuptools import setup

setup(
    name='ctyun',
    version='0.0.12',
    author='Xizhen Du',
    author_email='xizhendu@gmail.com',
    url='https://github.com/xizhendu/ctyun',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    description='Python SDK for China Telecom Cloud(https://www.ctyun.cn)',
    packages=['ctyun'],
    package_data = {
        '': ['api.yml']
    },
    include_package_data=True,
    install_requires=[
        "PyYAML",
        "requests",
        "datetime"
    ]
)
