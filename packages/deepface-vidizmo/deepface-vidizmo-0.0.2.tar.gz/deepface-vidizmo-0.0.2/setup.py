import setuptools


with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().split("\n")

f.close()

setuptools.setup(
    name="deepface-vidizmo",
    version="0.0.2",
    author="Huzaifa Tariq",
    author_email="huzaifat65@outlook.com",
    description="A Lightweight Face Recognition and Facial Attribute Analysis Framework (Age, Gender, Emotion, Race) for Python",
    long_description="""A Lightweight Face Recognition and Facial Attribute Analysis Framework (Age, Gender, Emotion, Race) for Python.
                    This library is for customized usage only and is delveloped for VIDIZMO application only.""",
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": ["deepface = deepface.DeepFace:cli"],
    },
    python_requires="==3.8.4",
    install_requires=requirements,
)
