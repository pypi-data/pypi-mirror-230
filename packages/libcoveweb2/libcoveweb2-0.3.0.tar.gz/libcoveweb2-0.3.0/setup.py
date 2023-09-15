from setuptools import find_packages, setup

install_requires = []

setup(
    name="libcoveweb2",
    version="0.3.0",
    author="Open Data Services",
    author_email="code@opendataservices.coop",
    packages=find_packages(),
    package_data={
        "libcoveweb2": [
            "static/*",
            "static/*/*",
            "static/*/*/*",
            "static/*/*/*/*",
            "templates/*",
            "templates/*/*",
        ]
    },
    url="https://github.com/OpenDataServices/lib-cove-web-2",
    description="q",
    classifiers=[],
    python_requires=">=3.8",
    install_requires=[
        "sentry-sdk",
        "Django",
        "django-bootstrap3",
        "django-environ",
        "requests",
        "celery[redis]",
    ],
    extras_require={
        "dev": ["black", "isort", "flake8", "mypy"],
    },
)
