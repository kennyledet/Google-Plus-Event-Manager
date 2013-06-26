from easyprocess import EasyProcess
from pyvirtualdisplay.smartdisplay import SmartDisplay
with SmartDisplay(visible=0, bgcolor='black') as disp:
    EasyProcess('python gplus_event.py create --title "test" --description description.txt --date "2012-06-09 10PM"').call()
