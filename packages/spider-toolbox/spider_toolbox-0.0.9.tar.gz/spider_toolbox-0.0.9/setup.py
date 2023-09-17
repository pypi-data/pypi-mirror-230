from setuptools import setup

with open('README.md', mode='r', encoding='utf-8') as f:
    long_description = f.read()
setup(
    name='spider_toolbox',
    version='0.0.9',
    author='neco_arc',
    author_email='3306601284@qq.com',
    description='爬虫工具库',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/sweetnotice/spider_toolbox',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    package_dir={'spider_toolbox': 'src'},
    packages=['spider_toolbox'],
    python_requires='>=3.6',
    install_requires=[
        'requests',
        'rich'
    ],
)
