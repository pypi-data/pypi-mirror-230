from setuptools import setup , find_packages

setup(
     name='Mensajes-Eclavo',
     version='5.0',
     description='un paquete para saludar y despedir',
     long_description=open('README.md').read(),
     long_description_content_type='text/markdown',#nos dice el tipo de archivo que cargamos en long descrotion , es importante sino da erropr
     author='Eddynson Clavo Chumpitaz',
     author_email='edyclavo@hotmail.com',
     url='https://www.xepi.dev',
     license_files=['LICENSE'],
     packages=find_packages(),
     scripts=[],
     test_suite='test',
     install_requires=[paquete.strip() for paquete in open("requirements.txt").readlines()], #strip sirve para borrar los espacion por delante y por detras
     classifiers=[
         'Environment :: Console',
         'Environment :: Console :: Curses',
         'Environment :: Console :: Framebuffer',
         'Environment :: Console :: Newt',
         'Environment :: Console :: svgalib',
         'Environment :: GPU',
         'Environment :: GPU :: NVIDIA CUDA',
         'Environment :: GPU :: NVIDIA CUDA :: 1.0',
         'Environment :: GPU :: NVIDIA CUDA :: 1.1',
     ],
)