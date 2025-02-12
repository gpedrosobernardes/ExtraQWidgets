from setuptools import setup

setup(
    name="extra_qwidgets",
    version="0.0.1",
    author="gustavopedrosob",
    author_email="thevicio27@gmail.com",
    description="Extra widgets for Qt/PySide6",
    url="https://github.com/gustavopedrosob/ExtraQWidgets",
    project_urls={
        "Bug Tracker": "https://github.com/gustavopedrosob/ExtraQWidgets/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "source"},
    packages=["extra_qwidgets"],
    install_requires=["emojis", "PySide6"],
    python_requires=">=3.12"
)