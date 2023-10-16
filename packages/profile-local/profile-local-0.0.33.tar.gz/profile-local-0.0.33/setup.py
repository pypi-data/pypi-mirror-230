import setuptools

PACKAGE_NAME = "profile-local"
package_dir = PACKAGE_NAME.replace("-", "_")

setuptools.setup(
    name=PACKAGE_NAME,  
    version='0.0.33',   #https://pypi.org/project/profile-local/
    author="Circles",
    author_email="info@circles.life",
    url=f"https://github.com/circles-zone/{PACKAGE_NAME}-python-package",
    packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    description="This is a package for sharing common crud operation to profile schema in the db",
    long_description="This is a package for sharing common profile functions used in different repositories",
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=["boto3>=1.28.44",
                    "location_profile_local>=0.0.18",
                    "operational-hours-local>=0.0.19",
                    "database-infrastructure-local>=0.0.12",
                    "person-local>=0.0.18",
                    "gender-local>=0.0.4",
                    "location-local>=0.0.40",
                    "reaction-local>=0.0.2",
                    "profile-reaction-local>=0.0.7",
                    "user-context-remote>=0.0.18",
                    "storage-local>=0.1.13",
                    "opencage>=2.3.0"]
 )
