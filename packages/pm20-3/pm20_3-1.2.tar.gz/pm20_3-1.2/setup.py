from setuptools import setup

setup(
    name='pm20_3',  # How you named your package folder (MyLib)
    packages=['pm20_3'],  # Chose the same as "name"
    version='1.2',  # Start with a small number and increase it with every change you make
    license='MIT',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description='For cheating again..',  # Give a short description about your library
    author='Anatoliy Nesterov',  # Type in your name
    author_email='your.email@domain.com',  # Type in your E-Mail
    url='http://www.fa.ru/Pages/Home.aspx',  # Provide either the link to your github or to your website
    download_url='https://github.com/user/reponame/archive/v_01.tar.gz',  # I explain this later on
    keywords=['CHEATING'],  # Keywords that define your package best
    install_requires=[  # I get to this in a second
        'pillow',
        'IPython',
        'setuptools'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3',  # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    include_package_data=True
)
