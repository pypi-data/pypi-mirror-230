from setuptools import setup, find_packages

setup(
    name = "JETDNN",
    version = "1.3.1",
    author = "S. Frankel, J. Simpson and E. Solano.",
    author_email = "s.frankel2@newcastle.ac.uk",
    url = "https://github.com/quasoph/JETDNN",
    description = "JETDNN: a Python package using Deep Neural Networks (DNNs) to find H-mode plasma pedestal heights from multiple engineering parameters.",
    packages = find_packages()
)