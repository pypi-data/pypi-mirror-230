import setuptools

PACKAGE_NAME = "storage-remote"
package_dir = PACKAGE_NAME.replace("-", "_")

with open('README.md') as f:
    readme = f.read()

setuptools.setup(
    name=PACKAGE_NAME,  # https://pypi.org/project/queue-worker-local
    version='0.0.7',
    author="Circles",
    author_email="info@circles.life",
    url=f"https://github.com/circles-zone/storage-remote-graphql-python-package",
    packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    long_description=readme,
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "python-dotenv>=1.0.0",
        "mysql-connector>=2.2.9",
        "pymysql>=1.1.0",
        "pytest>=7.4.0",

        "logger-local>=0.0.61",
        "database-without-orm-local>=0.0.90",
        "url-local>=0.0.28"
    ]
)
