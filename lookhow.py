import argparse
import subprocess


def createParser():
    APP_DESCRIPTION = '\"Look how\" is a client-server terminal application for real-time live coding.'
    SERVER_MODE_HELP = 'Run server.'
    CODER_MODE_HELP = 'Run client app in coder mode. The code that you will write will be broadcast to all connected users.'
    WATCHER_MODE_HELP = 'Run client app in watcher mode. The code that the coder writes will be broadcast to you.'
    

    parser = argparse.ArgumentParser(description=APP_DESCRIPTION)
    parser.add_argument('-s', '--server', action='store_const', const=True, default=False, help=SERVER_MODE_HELP)
    parser.add_argument('-c', '--coder', action='store_const', const=True, default=False, help=CODER_MODE_HELP)
    parser.add_argument('-w', '--watcher', action='store_const', const=True, default=False, help=WATCHER_MODE_HELP)
    return parser


if __name__ == '__main__':
    parser = createParser()
    namespace = parser.parse_args()

    args_val = namespace.__dict__
    bool_list = []
    for _, value in args_val.items():
        bool_list.append(value)
  
    if namespace.watcher or not any(bool_list):
        subprocess.call(['python', 'apps/watcher.py'], shell=True)
    elif namespace.coder:
        subprocess.call(['python', 'apps/coder.py'], shell=True)
    elif namespace.server:
        subprocess.call(['python', 'apps/server.py'], shell=True)