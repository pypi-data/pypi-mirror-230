from setuptools import setup, find_packages
setup(
    name='easy_chromium_controller',
    version='1.0.9',
    packages=find_packages(),
    install_requires=[
        # Control del navegador
        'selenium==4.12.0',
        # Edicion de imagen
        'Pillow==10.0.0',
        # Control de procesos ?
        'psutil==5.9.5',
        # Descargar archivos
        'wget==3.2',
        # Procesar texto
        'regex==2023.8.8'
    ],
)