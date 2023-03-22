"""
Запуск и остановка процессов
"""
from queue import Queue
import json
import threading
import time

DEBUG = True

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


def glavnaya():
    cmd_queue = Queue()
    reply_queue = Queue()
    obrab_komand_thread = threading.Thread(target=obrab_komand, kwargs={
                                           'in_q': cmd_queue, 'out_q': reply_queue})
    obrab_komand_thread.start()
    cmd_queue.put(kmd_examples['cmd_start'])
    obrab_komand_thread.join()


def obrab_komand(in_q: Queue, out_q: Queue) -> None:
    def cmd_kill():
        pass

    def cmd_start():
        pass

    def cmd_reboot():
        pass

    def cmd_exit():
        pass

    def put_error(msq):
        pass
    selector = {
        'cmd_kill': cmd_kill,
        'cmd_start': cmd_start,
        'cmd_reboot': cmd_reboot,
        'cmd_exit': cmd_exit
    }
    can_continue = True
    while can_continue:
        cmd = in_q.get()
        try:
            selector[cmd['do']]
        except KeyError as ke:
            put_error('Несуществующая команда' + ke.args[0])

if __name__ == '__main__':
    if DEBUG:
        for kmd in kmd_examples:
            try:
                json.dump(kmd_examples[kmd],
                        open(kmd + '.json', 'w'),
                        ensure_ascii=False,
                        indent=4)
            except KeyError as ke:
                print(ke)
                raise   
    #glavnaya()
