import sys, os, subprocess, threading, time

def reloader_loop():
    print '*RELOADER LOOP*'
    while True:
        executable = sys.executable
        args = sys.argv
        environ = os.environ.copy()
        print 'Executable: ', executable
        print 'Args: ', args
        print '[executable] + args: ', [executable] + args
        environ['watermelon'] = 'True'
        exit_code = subprocess.call([executable] + args, env=environ)
        print 'Exit_code: ', exit_code
        if exit_code == 3:
            continue
        else:
            return exit_code

def run_with_reloader(func, *args):
    print '*RUN LOOP*'
    if os.environ.get('watermelon'):
        print 'creating threads'
        t = threading.Thread(target=func, args=args)
        t.setDaemon(True)
        t.start()
        reload_check()
    else:
        print 'ENTERING RELOADER LOOP'
        reloader_loop()


def reload_check():
    print '*RELOAD CHECKING*'
    files_by_mtime = {}
    while True:
        for module in list(sys.modules.values()):
            if hasattr(module, '__file__'):
                filename = module.__file__
                if filename[-4:] == '.pyc':
                    filename = filename[:-1]
                try:
                    mtime = os.stat(filename).st_mtime
                except OSError:
                    print 'OSError on ', filename
                    sys.exit(3)
            
                value = files_by_mtime.get(filename)
                if value:
                    if value != mtime:
                        print 'EXITING'
                        sys.exit(3)
                else:
                    files_by_mtime[filename] = mtime

