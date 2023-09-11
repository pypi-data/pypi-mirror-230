from pprint import pprint

import pandas as pd

try:
    from vios.collection import s
except Exception as e:
    print(e)
    raise e

from qos_tools.experiment.scanner2 import Scanner
from waveforms.scan_iter import scan_iters

# Task模板，由用户自行生成
TEMPLATE = {
    'name': 'S21', # 任务名
    'signal': 'iq',
    'shots': 1024,

    'loops': [('bias',), ('freq1', 'freq2'), ('delay',)], # 循环变量
    "steps": [
        {'pos': (0, i), # 变量位置
         'kwds': {'bias': 0.1*i, 'freq1': 5e9, 'freq2': 6e9, 'delay': 0},  # 每个Step的参数

         'setting': {'Q1.setting.LO': 5e9, 'Q2.setting.LO': 5e9}, # 每个Step的设置
         'circuit': [('X', 'Q1'), (('Delay', 0), 'Q1'), (('Measure', 0), 'Q1')],# 每个Step的线路
         'measure':{'S21': 'NA.CH1.S'}, # 每个Step的读取
         'libs': ['std'] # 线路所用库
         } for i in range(3)
    ]
}


def extract(app: Scanner):
    task = {'name': app.name,
            'shots': app.shots,
            'signal': app.signal,
            'steps': []
            }
    cmds = list(scan_iters(**app.scan_range()))

    task['loops'] = [tuple(app.sweep_setting)[0]]
    for cmd in cmds:
        task['steps'].append(dict(pos=cmd.pos,
                                  kwds={k: v for k, v in cmd.kwds.items()
                                        if k.startswith('Q')},
                                  circuit=cmd.kwds['circuit']))
    return task



def transform(task: dict|Scanner):
    """将用户输出任务转为固定格式

    Args:
        task (dict): 用户输入的任务

    Returns:
        _type_: 固定格式的任务
    
    >>> pprint(transform(TEMPLATE))
    """
    
    task = extract(task) if isinstance(task, Scanner) else task
    
    qrt = {'metainfo': {}, 'taskinfo': {}}
    qrt['metainfo']['name'] = task.get('name','NameNotFound')
    qrt['metainfo']['other'] = {'signal': task.get('signal','iq_avg'),
                                'shots': task.get('shots',1024),}

    # [(('Measure',0,('with',('param:frequency', 'cfg:tmp.var1'))),'Q0')]
    
    loop, setting, circuit = expand(task)
    qrt['taskinfo']['CIRQ'] = circuit  # list
    qrt['taskinfo']['STEP'] = {'main': ['WRITE', {tuple(loop): setting}],
                               'step2': ['WRITE', 'trig'],  # 触发
                               'step3': ['WAIT', 0.0101],
                               'READ': ['READ', 'read'],
                               'step5': ['WAIT', 0.002]}
    qrt['taskinfo']['LOOP'] = loop | {'trig': [('Trigger.CHAB.TRIG', 0, 'any')]}

    return qrt


def expand(info: dict):
    # for i, step in enumerate(scan_iters(**info)):
    circuit = []
    setting = []
    for i, step in enumerate(info['steps']):
        circuit.append(step['circuit'])

        _ss = []
        for k,v in step.get('setting',{}).items():
            _ss.append((k, v, 'au'))
        setting.append(_ss)

        if i == 0:
            df = pd.DataFrame(step['kwds'], index=[0])
        else:
            df.loc[i] = step['kwds']

    loop = {}
    for k in info['loops']:
        if isinstance(k, tuple):
            # df[list(k)].values
            loop['|'.join(k)] = [(sk, df[sk].values, 'au') for sk in k]
        else:
            loop[k] = [(k, df[k].values, 'au')]

    return loop, setting, circuit


# %%
if __name__ == "__main__":
    import doctest
    doctest.testmod()