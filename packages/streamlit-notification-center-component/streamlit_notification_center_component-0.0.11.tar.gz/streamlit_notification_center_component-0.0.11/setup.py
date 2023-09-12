from pathlib import Path

import setuptools

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name="streamlit_notification_center_component",
    version="0.0.11",
    author="Brielle Harrison",
    author_email="bharrison@raptive.com",
    description="Streamlit component that listens for postMessage events and reports back",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.7",
    install_requires=[
        # By definition, a Custom Component depends on Streamlit.
        # If your component has other Python dependencies, list
        # them here.
        "streamlit >= 0.63",
        'beautifulsoup4',
        'lxml',        
    ],
)
