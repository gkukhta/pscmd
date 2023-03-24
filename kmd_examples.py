import json

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
                'cmd': ['/usr/bin/dd', 'if=/dev/zero', 'of=/dev/null']
            },
            {
                'cmd': ['/usr/bin/pss', '-ax'],
                'env': {
                    'LD_LIBRARY_PATH': '/opt/mylib',
                    'SOME_PARAMETER': 'value-x'
                },
                'cwd': '/tmp'
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

if __name__ == '__main__':
    for kmd in kmd_examples:
        json.dump(kmd_examples[kmd],
                    open(kmd + '.json', 'w'),
                    ensure_ascii=False,
                    indent=4)