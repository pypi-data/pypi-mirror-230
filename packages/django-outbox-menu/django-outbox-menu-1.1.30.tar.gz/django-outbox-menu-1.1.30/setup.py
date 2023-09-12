from setuptools import setup, find_packages
from os.path import abspath, dirname, join
import codecs
# import os.path

# Fetches the content from README.md
# This will be used for the "long_description" field.
README_MD = open(join(dirname(abspath(__file__)), "README.md")).read()

def read(rel_path):
    here = abspath(dirname(__file__))
    with codecs.open(join(here, rel_path), 'r') as fp:
        tmp =  fp.read()
        print('tmp = ', tmp)
        return tmp

def get_version(rel_path):
    for line in read(rel_path).splitlines():
        print('line = ', line)
        if line.startswith('__version__'):
            print('inside if = ', line)
            delim = line[line.find("(")+1:line.find(")")]
            print('test1', delim)

            # clear space
            i = 0
            tmp = ""
            while i<len(delim):
                tmp+=str(delim[i]).strip()
                i+=1

            print(tmp)
            # for i in delim:
            #     delim[i] = i.replace(" ", "")

            delim_split = tmp.split(',')
            print(delim_split)
            # delim = '"' if '"' in line else "'"
            # print('delim = ',delim)
            # return line.split(delim)[1]
            delim_split.pop(0)
            print('res = ', delim_split)
            
            tmp = ".".join(delim_split)
            print('result = ', tmp)
            return tmp
    else:
        raise RuntimeError("Unable to find version string.")

setup(
    # use_incremental=True,
    # setup_requires=['incremental'],
    # install_requires=['incremental'], # along with any other install dependencies

    # The name of your project that we discussed earlier.
    # This name will decide what users will type when they install your package.
    # In my case it will be:
    # pip install pydash-arnu515
    # This field is REQUIRED
    name="django-outbox-menu",

    # The version of your project.
    # Usually, it would be in the form of:
    # major.minor.patch
    # eg: 1.0.0, 1.0.1, 3.0.2, 5.0-beta, etc.
    # You CANNOT upload two versions of your package with the same version number
    # This field is REQUIRED
    # version="1.0.2",

    # update version using : python -m incremental.update menu --newversion 1.0.5
    version=get_version("menu/_version.py"),

    # The packages that constitute your project.
    # For my project, I have only one - "pydash".
    # Either you could write the name of the package, or
    # alternatively use setuptools.findpackages()
    #
    # If you only have one file, instead of a package,
    # you can instead use the py_modules field instead.
    # EITHER py_modules OR packages should be present.

    # use array for exclude for better way to exclude package
    packages=find_packages(exclude=["tests","django_menu",]),

    # dependencies
    install_requires=[
        'django-parler',        
    ],

    # agar file manifest .in dieksekusi
    include_package_data = True,

    # The description that will be shown on PyPI.
    # Keep it short and concise
    # This field is OPTIONAL
    description="DJANGO OUTBOX MENU",

    # The content that will be shown on your project page.
    # In this case, we're displaying whatever is there in our README.md file
    # This field is OPTIONAL
    long_description=README_MD,

    # Now, we'll tell PyPI what language our README file is in.
    # In my case it is in Markdown, so I'll write "text/markdown"
    # Some people use reStructuredText instead, so you should write "text/x-rst"
    # If your README is just a text file, you have to write "text/plain"
    # This field is OPTIONAL
    long_description_content_type="text/markdown",

    # The url field should contain a link to a git repository, the project's website
    # or the project's documentation. I'll leave a link to this project's Github repository.
    # This field is OPTIONAL
    url="https://github.com/PROJECT-OUTBOX/django_lib_outbox_menu.git",

    # The author name and email fields are self explanatory.
    # These fields are OPTIONAL
    # author_name="ione03",
    author_email="suratiwan03@gmail.com",

    # Classifiers help categorize your project.
    # For a complete list of classifiers, visit:
    # https://pypi.org/classifiers
    # This is OPTIONAL
    classifiers=[
        "License :: OSI Approved :: BSD License",
        # "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3 :: Only"
    ],

    # Keywords are tags that identify your project and help searching for it
    # This field is OPTIONAL
    keywords="menu, model base, environment, django",

    # For additional fields, check:
    # https://github.com/pypa/sampleproject/blob/master/setup.py    
)


# if __name__=="__main__":
#     get_version("menu/_version.py")
