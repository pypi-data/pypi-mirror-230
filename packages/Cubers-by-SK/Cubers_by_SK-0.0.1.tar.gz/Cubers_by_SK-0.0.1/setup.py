from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 11',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup(
    name='Cubers_by_SK',
    version='0.0.1',
    description='A very basic cubing library.',
    long_description=open('README.txt', encoding='utf-8').read() + '\n\n' + open('CHANGELOG.txt', encoding='utf-8').read(),
    long_description_content_type='text/plain',  # Set content type to plain text
    url='',
    author='Shashvat Kumar',
    author_email='shashvatkr3@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='Cube',
    packages=find_packages(),
    install_requires=['keyboard']
)
