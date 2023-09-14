from setuptools import setup, find_packages

setup(
    name="strada",
    version="0.1.3",
    packages=find_packages(where="strada"),
    package_dir={"": "strada"},
    install_requires=[
        # your dependencies here
        "google-api-python-client",
        "google-auth",
        "google-auth-oauthlib",
        "google-auth-httplib2",
    ],
    author="Strada",
    description="Strada SDK",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)
