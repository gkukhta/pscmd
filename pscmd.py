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
import sys
import argparse
import kmd_examples as kmds


def obrab_komand(in_q: Queue, out_q: Queue, fin_q: Queue) -> None:

    def put_error(msg):
        reply_msg['result'] = False
        reply_msg['text'] = msg

    def kill_list(pslist, msg):
        for p in pslist:
            p.terminate()
        put_error(msg)

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


def send_replies(out_q: Queue, fin_q: Queue, broker: mqtt.Client, topic):
    while True:
        broker.publish(topic, json.dumps(
            out_q.get(), ensure_ascii=False, indent=4))
        if not fin_q.empty():
            break


def getArgs():
    parser = argparse.ArgumentParser(
        description='Запуск и остановка процессов')
    parser.add_argument('-s', '--server',
                        type=str,
                        default='localhost',
                        help='Адрес MQTT сервера',
                        required=False)
    parser.add_argument('-i', '--inbox',
                        type=str,
                        default='cabincmd/in',
                        help='Ящик для входящих команд',
                        required=False)
    parser.add_argument('-o', '--outbox',
                        type=str,
                        default='cabincmd/out',
                        help='Ящик для исходящих ответов',
                        required=False)
    args = parser.parse_args()
    return args.server, args.inbox, args.outbox


def glavnaya():
    cmd_queue = Queue()
    reply_queue = Queue()

    # Если засунуть в finish_queue True - то перезагрузка,
    # если False - то выход из программы
    finish_queue = Queue()
    broker, inbox, outbox = getArgs()

    def on_connect(client, userdata, flags, rc):
        client.subscribe(inbox)

    def on_message(client, userdata, msg):
        try:
            cmd_queue.put(json.loads(msg.payload))
        except json.JSONDecodeError as err:
            reply = {}
            reply['result'] = False
            reply['text'] = 'Ошибка чтения JSON: '+err.msg + \
                ' Строка:' + str(err.lineno) + ' столбец:'+str(err.colno)
            reply['source'] = msg.payload.decode('utf-8')
            reply_queue.put(reply)
    
    def on_connect_fail():
        print('Не могу подключиться к MQTT брокеру ' + broker, file=sys.stderr)
        cmd_queue.put(kmds.kmd_examples['cmd_exit'])

    def on_disconnect(client, userdata, rc):
        print('Произошло отключение от MQTT брокера ' + broker, file=sys.stderr)
        while True:
            try:
                client.connect()
            except ConnectionRefusedError or OSError:
                print('Пытаюсь переподключиться к MQTT брокеру ' + broker, file=sys.stderr)
                time.sleep(1)
            else:
                break
        
    mqttc = mqtt.Client()
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.on_connect_fail = on_connect_fail
    try:
        mqttc.connect(broker)
    except OSError as cr:
        print('Не могу подключиться к MQTT брокеру ' + broker + ' ' + cr.strerror, file=sys.stderr)
        cmd_queue.put(kmds.kmd_examples['cmd_exit'])
    obrab_komand_thread = threading.Thread(target=obrab_komand, kwargs={
                                           'in_q': cmd_queue,
                                           'out_q': reply_queue,
                                           'fin_q': finish_queue})
    obrab_komand_thread.start()
    send_replies_thread = threading.Thread(target=send_replies, kwargs={
                                           'out_q': reply_queue,
                                           'fin_q': finish_queue,
                                           'broker': mqttc,
                                           'topic': outbox})
    send_replies_thread.start()
    mqttc.loop_start()
    obrab_komand_thread.join()
    send_replies_thread.join()
    time.sleep(1)
    mqttc.loop_stop()
    mqttc.disconnect()
    if (finish_queue.get()):
        subprocess.run(['/usr/bin/systemctl', 'reboot', '-i'])


if __name__ == '__main__':
    if sys.version_info[0] == 3 and sys.version_info[1] > 9:
        glavnaya()
    else:
        print('Требуется версия Python > 3.9. Текущая версия: ' +
              sys.version, file=sys.stderr)
        sys.exit(1)