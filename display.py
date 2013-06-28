from pyvirtualdisplay.smartdisplay import SmartDisplay
import atexit

try:
    disp = SmartDisplay(visible=0, bgcolor='black').start()
    atexit.register(disp.stop)
except:
    if disp:
        disp.stop()
    raise