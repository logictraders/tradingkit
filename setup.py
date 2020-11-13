import setuptools

setuptools.setup(
      name="tradingkit",
      version="1.1.6",
      author="QBit Artifacts, SL",
      author_email="lluis@logictraders.com",
      license="Propietary",
      description="Criptocurrency trading framework",
      long_description=open("README.md", "r").read(),
      long_description_content_type="text/markdown",
      url="https://github.com/logictraders/tradingkit",
      packages=setuptools.find_namespace_packages(where="src", include=['tradingkit.*']),
      package_dir={"": "src"},
      package_data={"": ["src/config"]},
      entry_points={
            "console_scripts": [
                  "tk = tradingkit.cli.cli:CLI.main"
            ]
      },
      classifiers=[
            "Development Status :: 2 - Pre-Alpha",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.7",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            "Intended Audience :: Developers",
            "Topic :: Internet",
            "Topic :: Software Development",
            "Topic :: Software Development :: Build Tools",
            "Topic :: Software Development :: Libraries",
            "Topic :: Software Development :: Libraries :: Python Modules"
      ],
      install_requires=[line.strip() for line in open("requirements.txt").readlines() if len(line) > 1]
)
