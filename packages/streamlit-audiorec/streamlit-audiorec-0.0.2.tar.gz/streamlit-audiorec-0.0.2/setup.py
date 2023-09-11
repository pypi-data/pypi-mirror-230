from pathlib import Path
import setuptools

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name="streamlit-audiorec",
    version="0.0.2",
    author="Stefan Rummer",
    author_email="stefan.rummer@outlook.com",
    description="Record audio from the user's microphone in apps that are deployed to the web. (via Browser Media-API) [GitHub: steamlit-audio-recorder] ",
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