from setuptools import setup, find_packages

setup(
    name = "zetane",
    author="Zetane Systems",
    author_email="info@zetane.com",
    description = "The Zetane API for robustness testing of Computer Vision AI models",
    long_description="""
The Zetane API is a Python library designed for robustly developing, testing, augmenting, and deploying computer vision Artificial Intelligence (AI) models. The API allows you to test adverse and out-of-domain conditions, offering a much-needed tool for AI developers, researchers, and data scientists who are eager to push the boundaries of their models, to comprehend their limitations, and to improve upon these performance thresholds.

The Zetane API's core functionalities are derived from its distinctive data transformation capabilities. It is designed to take input images and then transform them in a multitude of ways, mimicking conditions that a model might encounter in real-world applications. The variety of transformations includes but is not limited to, geometric and color augmentations, noise injection, alterations in lighting and contrast, as well as various forms of image degradation and distortions. These transformations effectively broaden the scope of conditions under which AI models are tested, ensuring a model is not just learning from its data, but also generalizing well to unforeseen situations.

Visit our [docs](https://docs.zetane.com) for more details on how to get started with the Zetane API.
""",
    long_description_content_type="text/markdown",
    version = "0.3.4",
    license="LICENSE.md",
    url="https://docs.zetane.com",
    packages=find_packages(include=('protector.*','zetane')),
    entry_points = {
        'console_scripts': [
            'zetane = zetane.__main__:main'
        ]
    },
    python_requires='>=3.7',
    install_requires = ['python-dotenv', 'tqdm', 'requests', 'numpy', 'filetype'],
    include_package_data=True,
    package_data={'zetane': ['*.json']},)
