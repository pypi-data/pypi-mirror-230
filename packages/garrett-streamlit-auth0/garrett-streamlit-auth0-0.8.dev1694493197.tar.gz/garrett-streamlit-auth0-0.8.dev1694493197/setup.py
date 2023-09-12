import setuptools
from version import get_next_version


setuptools.setup(
    name="garrett-streamlit-auth0",
    version=get_next_version(),
    author="",
    author_email="",
    description="",
    long_description="",
    long_description_content_type="text/plain",
    url="https://github.com/chris-garrett/garrett-streamlit-auth0",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.6",
    install_requires=[
        # By definition, a Custom Component depends on Streamlit.
        # If your component has other Python dependencies, list
        # them here.
        "streamlit >= 0.63",
        "python-jose == 3.3.0",
        "six"
    ],
)
