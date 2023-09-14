from setuptools import setup

def custom_install_code():
    # Este código se ejecutará durante la instalación
    print("Ejecutando código personalizado durante la instalación.")

setup()

# Ejecuta el código personalizado durante la instalación
custom_install_code()