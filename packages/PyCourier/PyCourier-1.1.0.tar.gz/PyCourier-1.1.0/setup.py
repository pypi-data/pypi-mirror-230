from distutils.core import setup

setup(
    name='PyCourier',
    packages=['PyCourier'],
    version='1.1.0',
    license='GNU GPLv3',
    description='PyCourier: A simple, reliable and fast email package for python',
    author='Mayank Vats',
    author_email='dev-theorist.e5xna@simplelogin.com',
    url='https://github.com/Theorist-Git/PyCourier',
    download_url='https://github.com/Theorist-Git/PyCourier/archive/refs/tags/v1.1.0.tar.gz',
    keywords=['EMAIL', 'SMTP', 'ENCRYPTION'],
    install_requires=[
        'pyzipper',
        'PyPDF2',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        # "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.9',
    ],
)
