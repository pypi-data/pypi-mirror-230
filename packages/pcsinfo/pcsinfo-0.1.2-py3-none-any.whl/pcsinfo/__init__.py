from pcsinfo.Computer import Computer
from pcsinfo.User import User
try:
    import GPUtil
    import cpuinfo
except ModuleNotFoundError:
    os.system("pip install GPUtil")
    os.system("pip install cpuinfo")
    import GPUtil
    import cpuinfo