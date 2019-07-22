from setuptools import setup, find_packages

def readme():
    with open('readme.md') as f:
        return f.read()

def read_reqs():
    with open('requirements.txt') as f:
        return [pkg.rstrip('\n') for pkg in f]

setup(
    name='topic_model_to_Shiny_app',
    url='https://github.com/Sparrow0hawk/topic_model_to_Shiny_app',
    version=1.1,
    author='Alex Coleman',
    author_email='a.coleman1@leeds.ac.uk',
    description='An implementation of Gensim topic modelling that identifies the number of topics using coherence scores.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    python_requires= '>=3.5',
    packages=find_packages(),


)
