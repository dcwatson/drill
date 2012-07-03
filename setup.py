from distutils.core import setup
import drill

setup(
    name='drill',
    version=drill.__version__,
    description='A small python library for quickly traversing XML data.',
    author='Dan Watson',
    author_email='dcwatson@gmail.com',
    url='https://github.com/dcwatson/drill',
    license='BSD',
    py_modules=['drill'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        "Programming Language :: Python :: 3",
        'Topic :: Text Processing :: Markup',
    ]
)
