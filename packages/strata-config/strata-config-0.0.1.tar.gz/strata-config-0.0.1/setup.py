from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(name='strata-config',
      version='0.0.1',
      description='Configuration Utility for Strata SASE',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/ktanushree/strata_config',
      author='Palo Alto Networks Developer Support',
      author_email='tkamath@paloaltonetworks.com',
      license='MIT',
      packages=['strata-config'],
      classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10"
      ]
      )
