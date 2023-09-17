from setuptools import setup

setup(name='d64',
      description='Read and write Commodore disk images',
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      use_scm_version=True,
      setup_requires=['setuptools_scm'],
      packages=['d64', 'd64/scripts'],
      entry_points={
        'console_scripts': [
          'd64-edit = d64.scripts.d64_edit:main [edit]',
          'd64-format = d64.scripts.d64_format:main',
          'd64-fsck = d64.scripts.d64_fsck:main'
          ]
        },
      install_requires = ['petscii-codecs'],
      extras_require = {
          'edit': ['cmd2']
      },
      author='Simon Rowe',
      author_email='srowe@mose.org.uk',
      url='https://eden.mose.org.uk/gitweb/?p=python-d64.git',
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ]
      )
