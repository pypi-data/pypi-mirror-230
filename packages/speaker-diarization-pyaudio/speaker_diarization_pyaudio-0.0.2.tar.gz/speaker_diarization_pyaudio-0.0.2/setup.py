import setuptools

with open("README.md", "r") as fh:
	description = fh.read()

setuptools.setup(
	name="speaker_diarization_pyaudio",
	version="0.0.2",
	author="FaithN",
	author_email="faithnchifor@gmail.com",
	packages=["speaker_diarization_pyn"],
	description="A speaker diarization pipeline made with pyannote",
	long_description=description,
	long_description_content_type="text/markdown",
	url="https://github.com/faith-nchifor/sd_pyannote",
	license='MIT',
	python_requires='>=3.8',
	install_requires=['whisper','torch','pyannote.audio','einops','numpy','huggingface_hub']
)
