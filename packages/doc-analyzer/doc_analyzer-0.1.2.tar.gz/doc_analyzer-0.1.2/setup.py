from setuptools import setup, find_packages

setup(
    name='doc_analyzer',
    author='Peter Darche',
    version='0.1.2',
    packages=find_packages(),
    install_requires=[
        'PyMuPDF',
        'PyPDF2',
        'requests',
        'langchain',
        'llama_index',
        'boto3',
        'scikit-learn',
        'openai',
        'pydantic',
        'pydub',
        'pandas',
        'textract'
    ],
)
