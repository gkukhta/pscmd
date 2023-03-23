"""
Запуск и остановка процессов
"""
from queue import Queue
import json
import threading
import time
import psutil

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
                    ('LD_LIBRARY_PATH', '/opt/mylib')
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

kmd_examples['cmd_test'] = {
    'do': 'test',
    'id': 'daf8-5f27'
}


def glavnaya():
    cmd_queue = Queue()
    reply_queue = Queue()
    finish_queue = Queue() # Если засунуть в очередь True - то перезагрузка, если False - то выход из программы
    obrab_komand_thread = threading.Thread(target=obrab_komand, kwargs={
                                           'in_q': cmd_queue, 'out_q': reply_queue, 'fin_q': finish_queue})
    obrab_komand_thread.start()
    cmd_queue.put(kmd_examples['cmd_start'])
    obrab_komand_thread.join()


def obrab_komand(in_q: Queue, out_q: Queue, fin_q: Queue) -> None:

    def cmd_kill():
        try:
            ps_list = cmd['ps']
            for psname in ps_list:
                ls = []
                for p in psutil.process_iter(['name']):
                    if p.info['name'] == psname:
                        ls.append(p)
                for p in ls:                
                    p.terminate()
        except KeyError as ke:
            put_error('Несуществующее поле: ' + ke.args[0])
        except psutil.AccessDenied as ad:
            put_error('Недостаточно полномочий для завершения процесса ' + ad.name)
        except psutil.Error as err:
            put_error(err.msg)

    def cmd_start():
        pass

    def cmd_reboot():
        fin_q.put(True)
        reply_msg['result'] = True

    def cmd_exit():
        fin_q.put(False)
        reply_msg['result'] = True

    def cmd_test():
        reply_msg['result'] = True

    def put_error(msg):
        reply_msg['result'] = False
        reply_msg['text'] = msg

    selector = {
        'cmd_kill': cmd_kill,
        'cmd_start': cmd_start,
        'cmd_reboot': cmd_reboot,
        'cmd_exit': cmd_exit,
        'cmd_test': cmd_test
    }
    
    while True:
        cmd = in_q.get()
        reply_msg = {}

        try:
            reply_msg['id'] = cmd['id']
            action = cmd['do']
        except KeyError as ke:
            put_error('Несуществующее поле: ' + ke.args[0])
        else:
            selector[action]()
        finally:
            out_q.put(reply_msg)        

        if not fin_q.empty:
            break


if __name__ == '__main__':
    if DEBUG:
        for kmd in kmd_examples:
            try:
                json.dump(kmd_examples[kmd],
                          open(kmd + '.json', 'w'),
                          ensure_ascii=False,
                          indent=4)
            except KeyError as ke:
                print('KeyError args: ' + ke.args)
                raise
    glavnaya()
