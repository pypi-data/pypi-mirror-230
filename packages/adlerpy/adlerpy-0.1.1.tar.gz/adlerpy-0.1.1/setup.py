from setuptools import setup

setup(
    name='adlerpy',
    version='0.1.1',    
    description='A code to compute the Adler function',
    url='https://github.com/rodofer2020/adlerpy.git',
    author='Rodolfo F',
    author_email='rferro@he-uni.mainz.de',
    license='BSD 2-clause',
    packages=['adlerpy'],
    install_requires=['numpy',                     
                      'rundec', 
                      'mpmath'],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)