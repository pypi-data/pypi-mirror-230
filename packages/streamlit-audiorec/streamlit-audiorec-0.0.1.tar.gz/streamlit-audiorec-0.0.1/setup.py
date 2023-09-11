from pathlib import Path
import setuptools

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name="streamlit-audiorec",
    version="0.0.1",
    author="Stefan Rummer",
    author_email="stefan.rummer@outlook.com",
    description="[steamlit-audio-recorder by stefanrmmr] Record Audio from the Client's Microphone, in Apps that are deployed to the Web. (via Browser Media-API)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/stefanrmmr/streamlit_audio_recorder",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.7",
    install_requires=[
        "streamlit>=0.63",
    ],
)