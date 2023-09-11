from setuptools import setup, find_packages

with open(r'statmanager\README.md', encoding='utf-8') as f:
    description_markdown = f.read()

setup(
    name='statmanager-kr',
    version='1.5.0',
    license='MIT',
    long_description=description_markdown,
    long_description_content_type='text/markdown',
    description='PANDAS 사용자를 위한, 간편하고 유용한 통계 패키지',
    author='ckdckd145',
    author_email='ckdckd145@gmail.com',
    url='https://cslee145.notion.site/statmanager-kr-Manual-c277749fe94b4e08a836236b409642b3?pvs=4',
    install_requires=['pandas', 'scipy', 'statsmodels', 'matplotlib', 'seaborn'],
    packages=find_packages(),
    keywords=['statistic', 'socialscience', 'stats',],
    python_requires='>=3.0',
    package_data={},
    zip_safe=False,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.13',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: Microsoft :: Windows :: Windows 11',
        'Natural Language :: Korean',
        'Development Status :: 4 - Beta',
    ],
)