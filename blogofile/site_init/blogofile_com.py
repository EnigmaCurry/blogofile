import subprocess
from subprocess import PIPE

def do_init(args): #pragma: no cover
    "Download the blogofile.com sources from github. Requires git."

    try:
        p=subprocess.Popen("git init",shell=True)
        p.wait()
    except OSError:
        print "Cannot find git executable on the system PATH"
        return
    p=subprocess.Popen(
            "git remote add origin "
            "git://github.com/EnigmaCurry/blogofile.com.git", shell=True)
    p.wait()
    p=subprocess.Popen("git pull origin master", shell=True)
    p.wait()
    
