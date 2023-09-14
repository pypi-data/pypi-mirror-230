
import multiprocessing
import os
import re
import subprocess
from distutils.command.build_ext import build_ext
from distutils.core import setup
from distutils.dist import Distribution
from distutils.extension import Extension


class PyChrysalide(Distribution):
    """Create a suitable distribution for a Chrysalide Python package."""

    def __init__(self, attrs=None):
        """Build one instance for the pychrysalide package."""

        super().__init__(attrs)

        self.ext_modules = [ Extension('pychrysalide', []) ]


class BuildCPackage(build_ext):
    """Implement a build_ext command."""

    def run(self):
        """Run the original build process for creating a native package."""

        prefix = '/tmp/build/lib'

        # Compile

        subprocess.run([ './autogen.sh' ], check=True)

        subprocess.run([ './configure', '--prefix=%s' % prefix, '--enable-silent-rules',
                         '--disable-gtk-support',
                         '--enable-python-package', '--disable-rpath' ], check=True)

        nproc = multiprocessing.cpu_count()

        subprocess.run([ 'make', '-j%u' % nproc ], check=True)

        subprocess.run([ 'make', 'install' ], check=True)

        # Install

        build_top_dir = os.path.join(self.build_lib, '')
        build_lib_dir = os.path.join(self.build_lib, 'chrysalide-libs', '')
        build_pg_dir = os.path.join(self.build_lib, 'chrysalide-plugins', '')

        self.mkpath(build_top_dir)
        self.mkpath(build_lib_dir)
        self.mkpath(build_pg_dir)

        self.copy_file(prefix + '/lib/libchrysacore.so', build_lib_dir + 'libchrysacore.so')

        pluginslibdir = prefix + '/lib/chrysalide-plugins/'

        for f in os.listdir(pluginslibdir):

            if not(f.endswith('.so')):
                continue

            if f == 'pychrysalide.so':

                self.copy_file(pluginslibdir + f, build_top_dir + 'pychrysalide.so')

            else:

                self.copy_file(pluginslibdir + f, build_pg_dir + os.path.basename(f))


def get_version_from_m4():
    """Read the version number from the hardcoded version."""

    version = None

    with open('gitrev.m4', 'r') as fd:
        content = fd.read()

    exp = re.compile(r'define\(\[gitrepo\], \[([0-9]*)\]\)')

    for line in content.split('\n'):

        match = exp.search(line)

        if match:
            version = match.group(1)
            break

    assert(version)

    return version


metadata = {

    'name': 'pychrysalide',
    'version': get_version_from_m4(),

    'description': 'Reverse Engineering Factory',
    'long_description': 'Chrysalide is a fast tool collection for binary analysis.' + \
                        ' It is written using the GTK+ toolkit and support several' + \
                        ' file formats and architectures. Python bindings are also available.',
    'long_description_content_type': 'text/plain',

    'url': 'https://www.chrysalide.re/',
    'author': 'Cyrille BAGARD',
    'author_email': 'nocbos' + chr(64) + 'gmail' + chr(0x2e) + 'com',

    'classifiers': [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: C',
        'Programming Language :: Python :: 3',
        'Topic :: Security',
        'Topic :: Software Development :: Debuggers',
        'Topic :: Software Development :: Disassemblers',
        'Topic :: Software Development :: Embedded Systems',
    ],

    'install_requires': [
        'pygobject',
    ],

    'keywords': 'reverse, engineering, disassembler, security',

    'python_requires': '>=3',

    'project_urls': {
        'Bug Reports': 'https://bugs.chrysalide.re/',
        'Source': 'http://git.0xdeadc0de.fr/cgi-bin/cgit.cgi/chrysalide.git/',
        'Twitter': 'https://twitter.com/chrysalide_ref',
    },

}

cmdclass = {
    'build_ext': BuildCPackage,
}

setup(distclass=PyChrysalide,
    **metadata,
    cmdclass=cmdclass,
)
