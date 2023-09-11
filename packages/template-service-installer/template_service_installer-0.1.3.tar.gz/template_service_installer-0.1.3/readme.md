# Service installer

### Library for automated installing services to /etc/systemd/system folder

## It will be useful if:
- You have a lot of servers where you want to deploy your project
- Your project consists of a large number of services, and you are not going to use docker
- Each of your servers has different working directories for services

## Usage
- You can run this library as a standalone app using 

```sh
 python -m service_install (template_dir) (working_dir)
```
- You can import this library to your project and use it there

```python
from service_installer import install_services

install_services('/foo/bar', 'foo/bar2/')
```