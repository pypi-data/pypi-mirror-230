import sys


if __name__ == '__main__':
    from service_installer.service_installer import install_services
    install_services(sys.argv[1], sys.argv[2])
