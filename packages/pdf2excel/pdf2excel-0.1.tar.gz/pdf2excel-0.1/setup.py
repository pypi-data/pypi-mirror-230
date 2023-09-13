from setuptools import setup, find_packages

setup(
    name='pdf2excel',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'PyPDF2',
        'pdf2docx',
        'pypandoc',
        'pandas',
        'openpyxl',
        're'
    ],
    entry_points={
        'console_scripts': [
            'pdf2excel=pdf2excel:main',
        ],
    },
)
