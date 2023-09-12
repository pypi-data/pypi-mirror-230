# Author: kk.Fang(fkfkbill@gmail.com)

import setuptools

with open("./README.md", "r", encoding="utf-8") as f:
    long_desc = f.read()

with open("./VERSION", "r", encoding="utf-8") as f:
    version = f.read()

setuptools.setup(
    name="golive-django-openapi",
    version=version,
    author="fk",
    author_email="fkfkbill@gmail.com",
    description="青橄榄Django OpenAPI框架",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://jh-golive-gitlab.goliveplus.cn/golive-project-manage/golive-django-openapi",
    include_package_data=True,
    packages=setuptools.find_packages(),
    install_requires=[
        "pydantic<2",
        "fastapi<2",
        "django",
        "django-comment-migrate==0.1.5",
        "loguru",
        "apscheduler",
        "schema"
    ],
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.11",
)
