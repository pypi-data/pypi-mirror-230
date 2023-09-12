
import psutil

def process_list(keyword=None):
    processlist = []

    if keyword is None:
        for process in psutil.process_iter():
            if process.status() == 'running':
                processlist.append(process)
    else:
        for process in psutil.process_iter():
            if process.status() == 'running' and keyword.lower() in process.name().lower():
                processlist.append(process)

    return processlist


class xPsUtil:
    def __init__(self):
        pass


if __name__ == "__main__":
    pList = process_list("notepad")
    for p in pList:
        cl = p.cmdline()
        print(cl)
    pass
