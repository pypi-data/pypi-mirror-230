import os
from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md"), "r", encoding="utf-8") as fobj:
    long_description = fobj.read()

with open(os.path.join(here, "requirements.txt"), "r", encoding="utf-8") as fobj:
    requires = [x.strip() for x in fobj.readlines() if x.strip()]


setup(
    name="django-static-ionicons",
    version="2.0.1.4",
    description="Django application contain ionicons static files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Chen ZhiXing",
    author_email="chenzhixing@zencore.cn",
    maintainer="Chen ZhiXing",
    maintainer_email="chenzhixing@zencore.cn",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords=["django-static-ionicons"],
    packages=find_packages(
        ".",
        exclude=[
            "django_static_ionicons_demo",
            "django_static_ionicons_example",
            "django_static_ionicons_example.migrations",
        ],
    ),
    py_modules=["django_static_ionicons"],
    install_requires=requires,
    zip_safe=False,
    include_package_data=True,
)
