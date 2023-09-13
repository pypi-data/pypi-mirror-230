from setuptools import setup,find_packages

setup(
    name='ctyun',
    version='0.0.7',
    author='Xizhen Du',
    author_email='xizhendu@gmail.com',
    url='https://github.com/xizhendu/ctyun',
    long_description=open('README.md', 'r').read(),
    long_description_content_type='text/markdown',
    description='Python SDK for China Telecom Cloud(https://www.ctyun.cn)',
    packages = ['ctyun'],
    include_package_data=True,
    data_files=[('api-config-file', ['config/api.yml'])],
    install_requires=[
        "PyYAML",
        "requests",
        "datetime"
    ]
)
