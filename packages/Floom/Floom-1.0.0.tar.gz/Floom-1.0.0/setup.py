from setuptools import setup, find_packages

setup(
    name='Floom', #Floom Python SDK
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        # No third-party packages
    ],
    author='Floom.AI',
    author_email='max@floom.ai',
    description='Floom orchestrates & executes Generative AI pipelines, Empowering Developers and DevOps to focus on what matters.',
    url='https://github.com/FloomAI/FloomSDK-Python',
)
