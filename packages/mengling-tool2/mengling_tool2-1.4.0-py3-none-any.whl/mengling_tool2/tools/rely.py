import subprocess
import easygui


def sync_req(*models):
    depdt = {}
    for txt in subprocess.run(['pip', 'freeze'], capture_output=True, text=True).stdout.split('\n'):
        ls = txt.split('==')
        if len(ls) == 2:
            depdt[ls[0]] = ls[1]
    notes = []
    for model in models:
        v = depdt.get(model)
        if v:
            notes.append(f'{model}=={v}')
        else:
            print(model, '没有对应版本,默认最新版')
            notes.append(f'{model}')
    with open(easygui.filesavebox(default='requirements.txt'), mode='w+') as file:
        file.write('\n'.join(notes))