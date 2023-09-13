from setuptools import setup, find_packages

# 读取 README.md 的内容
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='pdf2excel',
    version='0.2',  # 更新版本号以反映更改
    packages=find_packages(),
    install_requires=[
        'PyPDF2',
        'pdf2docx',
        'pypandoc',
        'pandas',
        'openpyxl',
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",  # 指定long_description的格式为markdown
    entry_points={
        'console_scripts': [
            'pdf2excel=pdf2excel:main',
        ],
    },
)
