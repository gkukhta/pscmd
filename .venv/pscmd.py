"""
Запуск и остановка процессов
"""
from queue import Queue
import json

DEBUG = True

cmd_queue = Queue()
reply_queue = Queue()


def obrab_komand():
    pass

kmd_examples = {}

kmd_examples['cmd_kill'] = {
    'do': 'kill',
    'ps': ['tar', 'gzip', 'dd'],
    'id': 'ab12-de13'
}

kmd_examples['cmd_start'] = {
    'do': 'start',
    'ps':
        [
            {
                'cmd': ['/usr/bin/ps', '-ax'],
                'env': [
                    ('LD_LIBRARY_PATH', '.')
                ],
                'cwd': '/tmp'
            },
            {
                'cmd': ['/usr/bin/dd', 'if=/dev/zero', 'of=/dev/null']
            }
        ],
    'id': 'de14-8822'
}

kmd_examples['cmd_reboot'] = {
    'do': 'reboot',
    'id': '236d-45f2'
}

kmd_examples['cmd_exit'] = {
    'do': 'exit',
    'id': 'daf4-5f27'
}

if __name__ == '__main__':
    if DEBUG:
        
        for kmd in kmd_examples:
            json.dump(kmd_examples[kmd], 
                    open(kmd +'.json', 'w'),
                    ensure_ascii=False, 
                    indent=4)
