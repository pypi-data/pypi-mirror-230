from setuptools import setup

with open("readme.md") as file:
    read_me_description = file.read()

setup(
    name='template_service_installer',
    version='0.1.3',
    description='Library for automating the installation of systemd services',
    long_description=read_me_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Fox-sys/service_installer",
    packages=['service_installer'],
    author_email='berestovborisasz@gmail.com',
    zip_safe=False
)
