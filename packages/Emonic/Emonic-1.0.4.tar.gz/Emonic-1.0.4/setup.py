from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

with open('LICENSE', 'r', encoding='utf-8') as f:
    license_text = f.read()

setup(
    name='Emonic',
    version='1.0.4',
    description="Discover a user-friendly Python web framework designed to empower developers in building both standard and high-level applications. Crafted with simplicity in mind, this framework provides an intuitive environment for creating web applications that adhere to industry standards. Whether you're embarking on a straightforward project or aiming for a sophisticated application, our framework streamlines the development process, offering flexibility and tools to match your goals.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Pawan kumar',
    author_email='embrakeproject@gmail.com',
    url='https://github.com/embrake/emonic/',
    packages=find_packages(),
    keywords='web framework Python web development user-friendly high-level',
    license='MIT',
    install_requires=['werkzeug', 'jinja2', 'cryptography', 'bcrypt', 'colorama', 'itsdangerous', 'uuid', 'qrcode'],  
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
    entry_points={
        'console_scripts': [
            'emonic-admin = emonic.admin:main',
        ],
    },
)
