from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="featurebridge",
    version="1.0",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">3.7",
    author="Netanel Eliav",
    author_email="inetanel@me.com",
    description="Revolutionizing ML adaptive modelling for handling missing features. Predict and fill gaps in real-world data.",
    long_description="Introducing FeatureBridge: Revolutionizing ML adaptive modelling for handling missing features. Predict and fill gaps in real-world data, ensuring accurate AI predictions. Tailor feature selection and optimize model performance effortlessly. Seamlessly integrate into your ML pipeline",
    url="https://github.com/iNetanel/featurebridge",
    project_urls={
    "Author's Website": "https://inetanel.com",
    "Source Code": "https://github.com/iNetanel/featurebridge",
},
)