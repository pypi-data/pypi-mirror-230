from setuptools import setup

with open('README.md', encoding='utf-8') as _f:
    long_description = _f.read()

setup(
    name='miraelogger',  # package name
    version='0.0.3',  # package version
    packages=['miraelogger'],
    url='https://github.com/milktea0614/miraelogger',  # Deploy url (e.g. GitHub repository url)
    license='',
    author='Jang, Mirae',
    author_email='milktea0614@naver.com',
    description='Custom logger for Jang, Mirae',
    keywords=['pypi deploy', 'miraelogger'],
    python_requires='>=3',  # Requires python version
    classifiers=[
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    long_description=long_description,  # for pypi description
    long_description_content_type='text/markdown'
)
