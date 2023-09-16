from setuptools import setup
import sys

if __name__ == '__main__':

    try:
        import sphinx
    except ImportError:
        sphinxInstalled=False
    else:
        sphinxInstalled=True
    #endTry

    if not sphinxInstalled:
        sys.stderr.write(f"> Warning, Sphinx is not installed ; I'll try it.\n")
    #endIf

    setup()

#endIf
