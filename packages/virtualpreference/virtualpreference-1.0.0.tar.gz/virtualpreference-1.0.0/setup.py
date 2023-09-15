from setuptools import setup

setup(
    name="virtualpreference",
    version="1.0.0",
    description="Virtual Preference APIs Connector",
    author="Virtual Preference Team",
    author_email="team@virtualpreference.com",
    packages=["virtualpreference.storage"],
    install_requires=["django", "requests", "wheel", "termcolor"]
)
