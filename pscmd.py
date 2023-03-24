#!/usr/bin/env python
"""
Запуск и остановка процессов
"""
from queue import Queue
import json
import threading
import time
import psutil
import subprocess
import os
import paho.mqtt.client as mqtt
import kmd_examples as samples

DEBUG = True

def obrab_komand(in_q: Queue, out_q: Queue, fin_q: Queue) -> None:

    def put_error(msg):
        reply_msg['result'] = False
        reply_msg['text'] = msg

    def kill_list(pslist, msg):
        for p in pslist:
            p.terminate()
        put_error(msg)
    
    if DEBUG:
        print('Поток обработки команд: ' + threading.current_thread().name)

    while True:
        cmd = in_q.get()
        reply_msg = {}
        try:
            reply_msg['id'] = cmd['id']
            match cmd['do']:
                case 'kill':
                    try:
                        for psname in cmd['ps']:
                            for p in psutil.process_iter(['name']):
                                if p.info['name'] == psname:
                                    p.terminate()
                    except psutil.AccessDenied as ad:
                        put_error(
                            'Недостаточно полномочий для завершения процесса ' + ad.name)
                    except psutil.Error as err:
                        put_error(err.msg)
                    else:
                        reply_msg['result'] = True
                case 'start':
                    pslist = []
                    try:
                        for p in cmd['ps']:
                            env = os.environ.copy()
                            try:
                                my_env = p['env']
                            except KeyError:
                                pass
                            else:
                                for key in my_env:
                                    env[key] = my_env[key]
                            try:
                                cwd = p['cwd']
                            except KeyError:
                                cwd = None
                            pslist.append(subprocess.Popen(
                                p['cmd'], env=env, cwd=cwd))
                    except KeyError as ke:
                        kill_list(pslist,
                                  'Ошибка при запуске процесса. Несуществующее поле: ' + ke.args[0])
                    except OSError as e:
                        kill_list(pslist, 'Ошибка при запуске процесса. ' +
                                  e.strerror+' '+e.filename)
                    except ValueError as e:
                        kill_list(pslist,
                                  'Ошибка при запуске процесса. Некорректный аргумент: ' + e.args[0])
                    else:
                        reply_msg['result'] = True
                case 'reboot':
                    fin_q.put(True)
                    reply_msg['result'] = True
                case 'exit':
                    fin_q.put(False)
                    reply_msg['result'] = True
                case 'test':
                    reply_msg['result'] = True
                case _:
                    raise KeyError(cmd['do'])
        except KeyError as ke:
            put_error('Несуществующее поле: ' + ke.args[0])
        finally:
            out_q.put(reply_msg)
        if not fin_q.empty():
            break

def getArgs():
    server = 'localhost'
    inbox = 'cabincmd/in'
    outbox = 'cabincmd/out'
    return server, inbox, outbox


def glavnaya():
    cmd_queue = Queue()
    reply_queue = Queue()

    # Если засунуть в finish_queue True - то перезагрузка, если False - то выход из программы
    finish_queue = Queue()
    obrab_komand_thread = threading.Thread(target=obrab_komand, kwargs={
                                           'in_q': cmd_queue,
                                           'out_q': reply_queue,
                                           'fin_q': finish_queue})
    obrab_komand_thread.start()
    if DEBUG:
        cmd_queue.put(samples.kmd_examples['cmd_kill'])
        cmd_queue.put(samples.kmd_examples['cmd_start'])
        cmd_queue.put(samples.kmd_examples['cmd_test'])
        cmd_queue.put(samples.kmd_examples['cmd_exit'])
        print('Главный поток: ' + threading.current_thread().name)
    obrab_komand_thread.join()
    if DEBUG:
        while not reply_queue.empty():
            print(reply_queue.get())
        while not finish_queue.empty():
            print(finish_queue.get())


if __name__ == '__main__':
    glavnaya()
