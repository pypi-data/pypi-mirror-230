from setuptools import setup, find_packages

setup(
    name='tabler-qicon',
    version='0.1.0',
    description='Python package that provides easy access to Tabler Icons for PyQt and PySide applications.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Charin Rungchaowarat',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    license='MIT',
    extras_require={
        'PyQt5': ['PyQt5'],
        'PyQt6': ['PyQt6'],
        'PySide2': ['PySide2'],
        'PySide6': ['PySide6'],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Natural Language :: English',
        'Typing :: Typed',
    ],
)
