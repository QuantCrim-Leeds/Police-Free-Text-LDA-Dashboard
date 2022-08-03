from setuptools import setup, find_packages

def readme():
    with open('readme.md') as f:
        return f.read()

setup(
    name='topic_model_to_Shiny_app',
    url='https://github.com/Sparrow0hawk/topic_model_to_Shiny_app',
    version="1.4.0-dev",
    author='Alex Coleman',
    author_email='a.coleman1@leeds.ac.uk',
    description='An implementation of Gensim topic modelling that identifies the number of topics using coherence scores.',
    long_description=readme(),
    long_description_content_type='text/markdown',
    python_requires= '>=3.5',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True


)
