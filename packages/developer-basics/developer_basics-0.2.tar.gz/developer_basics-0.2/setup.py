from distutils.core import setup
# https://medium.com/@joel.barmettler/how-to-upload-your-python-package-to-pypi-65edc5fe9c56
setup(
  name = 'developer_basics',         # How you named your package folder (MyLib)
  packages = ['developer_basics'],   # Chose the same as "name"
  version = '0.2',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Contains basic developer helper functions',   # Give a short description about your library
  author = 'Tyler Hirsch',                   # Type in your name
  author_email = 'tylerhirschbiz@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/tylerhirsch62/developer-basics',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/tylerhirsch62/developer-basics/archive/refs/tags/v_0.2.tar.gz',    # I explain this later on
  keywords = ['developer', 'basics', 'developer_basics'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
  ],
)