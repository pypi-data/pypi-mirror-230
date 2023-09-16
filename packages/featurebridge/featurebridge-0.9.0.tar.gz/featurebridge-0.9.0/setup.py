from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="featurebridge",
    version="0.9.0",
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
    zip_safe=True,
    python_requires=">=3.6",
    author="Netanel Eliav",
    author_email="inetanel@me.com",
    url="https://github.com/iNetanel/featurebridge",
    author_url="https://inetanel.com",
    description="FeatureBridge: Revolutionizing ML adaptive modelling for handling missing features. Predict and fill gaps in real-world data.",
    long_description=open("README.md").read(),
    long_description_content_type='text/markdown',  # Specify Markdown format
    license="MIT",
    keywords="python, package, example",

    project_urls={
    "Author Website": "https://inetanel.com",
    "Documentation": "https://github.com/iNetanel/featurebridge/wiki",
    "Source Code": "https://github.com/iNetanel/featurebridge",
    "Issue Tracker": "https://github.com/iNetanel/featurebridge/issues",
                },
    classifiers=[
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "Intended Audience :: Information Technology",
    "Intended Audience :: System Administrators",
    "Intended Audience :: Education",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
                ],
        )