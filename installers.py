import platform
import subprocess
import os
import StringIO
import urllib2
import zipfile

def chromedriver():
    # Get ChromeDriver if it's not in the path...
    # https://code.google.com/p/chromedriver/downloads/list
    chromedriver_bin = None

    if platform.system() == "Linux":
        chromedriver_bin = "chromedriver"
        if platform.processor() == "x86_64":
            # 64 bit binary needed
            chromedriver_url = "https://chromedriver.googlecode.com/files/chromedriver2_linux64_0.6.zip"  # noqa
        else:
            # 32 bit binary needed
            chromedriver_url = "https://chromedriver.googlecode.com/files/chromedriver_linux32_26.0.1383.0.zip"  # noqa

    elif platform.system() == "mac" or platform.system() == 'Darwin':
        chromedriver_url = "https://chromedriver.googlecode.com/files/chromedriver2_mac32_0.7.zip"  # noqa
        chromedriver_bin = "chromedriver"
    elif platform.system() == "win32":
        chromedriver_bin = "https://chromedriver.googlecode.com/files/chromedriver2_win32_0.7.zip"  # noqa
        chromedriver_url = "chromedriver.exe"

    try:
        print chromedriver_bin
        if subprocess.call(chromedriver_bin) != 0:
            raise OSError("Return code?")
    except OSError:
        chromedriver_local = os.path.join("tools", chromedriver_bin)

        if not os.path.exists(chromedriver_local):
            datafile = StringIO.StringIO(
                urllib2.urlopen(chromedriver_url).read())
            contents = zipfile.ZipFile(datafile, 'r')
            contents.extract(chromedriver_bin, "tools")

        chromedriver = os.path.realpath(chromedriver_local)
        os.chmod(chromedriver, 0755)
    else:
        chromedriver = "chromedriver"

if raw_input('Install Chromedriver? y or n\t') == 'y':
    chromedriver()