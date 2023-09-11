"""任务形式规则

整体两个字段
>>> metainfo:
       > name: filename:/s21，filename表示数据将存储于filename.hdf5中，s21为实验名字，以:/分隔
       > user: 实验者代号。默认为usr。
       > priority: 优先级，任务同时提交时，优先级数值小的先执行。默认为0。
       > other: 其他参数，如shots、signal等
>>> taskinfo:
       > STEP：大写，保留关键字，描述任务执行的变量（即for循环变量）与执行步骤（即for循环体）
       > CIRQ：大写，保留关键字，描述任务线路，长度等于STEP中for循环变量长度。可为空。
       > INIT：大写，保留关键字，任务初始化设置。可为空。
       > RULE：大写，保留关键字，变量关系列表，可为表达式或空，如[f'<gate.rfUnitary.{q}.params.frequency>=<freq.{q}>']。可为空。
       > LOOP：大写，保留关键字，定义循环执行所用变量，与STEP中main的值对应，STEP中main所用变量为LOOP的子集
"""

import numpy as np

from qos_tools.experiment.libs.tools import generate_spanlist
from vios.collection import s

filename = 'testtask' # an hdf5 file named testtask.hdf5 will be created
priority = 0
trigger = s.query('station.triggercmds')[0]

power = np.linspace(-30, 10, 46)
s21_power2d_na = {
    'metainfo': {'name': f'{filename}:/s21_power2d', 'priority': 0,
                 'other': {}
                 },
    'taskinfo': {'STEP': {'main': ['write', ('POWER', )],
                          'READ': ['read', 'READ']},
                 'RULE': ['<NA.CH1.Power>=<POWER.power>'],
                 'LOOP': {'POWER': [('power', power, 'dBm')],
                          'READ': ['NA.CH1.Trace']},
                 }
}


# %% S21
qubits = ['Q0102', 'Q0204']
points = 21
freq = [s.query(f'gate.Measure.{q}.params.frequency') + np.linspace(-0.5, 0.5, points)*1e6 for q in qubits]

s21 = {'metainfo': {'name': f'{filename}:/s21', 'priority': priority, 'user': 'yltest',
                    'other': {'shots': 1024, 'signal': 'remote_iq_avg'}},
       'taskinfo': {'STEP': {'main': ['WRITE', ('freq',)],
                             'trigger': ['WRITE', 'trig'],
                             'READ': ['READ', 'read'],
                             },
                    'CIRQ': [[(('Measure', i), q) for i, q in enumerate(qubits)]]*points,
                    'RULE': [f'<gate.Measure.{q}.params.frequency>=<freq.{q}>' for q in qubits],
                    'LOOP': {'freq': [(f'{q}', freq[i], 'Hz') for i, q in enumerate(qubits)],
                             'trig': [(trigger, 0, 'any')]
                             }
                    },
       }


# %% Scatter
qubits = ['Q0102', 'Q0204']
repeat = 3

scatter = {'metainfo': {'name': f'{filename}:/Scatter', 'priority': priority, 'user': 'yltest',
                        'other': {'shots': 1024, 'signal': 'iq'}},
           'taskinfo': {'STEP': {'main': ['WRITE', ('repeat',)],
                                 'trigger': ['WRITE', 'trig'],
                                 'READ': ['READ', 'read'],
                                 },
                        'CIRQ': [[*[(g, q) for q in qubits],
                                  ('Barrier', tuple(qubits)),
                                  *[(('Measure', i), q) for i, q in enumerate(qubits)]
                                  ] for g in ['I', 'X']*repeat],
                        'LOOP': {'repeat': [('repeat', np.arange(repeat*2), '1')],
                                 'trig': [(trigger, 0, 'any')]
                                 }
                        },
           }
# s0, s1 = np.concatenate(result[::2,...],0),np.concatenate(result[1::2,...],0)



# %% CloudCircuit
repeat = 3
cc = []
cloud = {'metainfo': {'name': f'{filename}:/CloudCircuit', 'priority': priority, 'user': 'yltest',
                      'other': {'shots': 1024, 'signal': 'count'}},
         'taskinfo': {'STEP': {'main': ['WRITE', ('repeat',)],
                               'trigger': ['WRITE', 'trig'],
                               'READ': ['READ', 'read'],
                               },
                      'CIRQ': [cc]*repeat,
                      'LOOP': {'repeat': [('repeat', np.arange(repeat), '1')],
                               'trig': [(trigger, 0, 'any')]
                               }
                      },
         }


# %% Spectrum
qubits = ['Q0102','Q0204']
points = 101
freq = [s.query(f'gate.rfUnitary.{q}.params.frequency') + np.linspace(-50, 50, 101)*1e6 for q in qubits]
wop = [('param:duration',[[0,0.5],[1e-6,1e-6]]),
       ('param:amp',[[0,0.5],[0,0.2]]),
       ('param:delta',0),
       ]

spectrum = {'metainfo': {'name': f'{filename}:/Spectrum', 'priority': priority, 'user': 'yltest',
                         'other': {'shots': 1024, 'signal': 'remote_population'}
                         },
            'taskinfo': {'STEP': {'main': ['WRITE', ('freq',)],
                                  'tigger': ['WRITE', 'trig'],
                                  'READ': ['READ', 'read'],
                                  'wait': ['WAIT', 0.5]
                                  },
                         'CIRQ': [[*[(('rfUnitary', np.pi/2, 0, ('with', *wop)), q) for q in qubits],
                                   ('Barrier', tuple(qubits)),
                                   *[(('Measure', i), q) for i, q in enumerate(qubits)]
                                   ]
                                  ]*points,
                         'RULE': [f'<gate.rfUnitary.{q}.params.frequency>=<freq.{q}>' for q in qubits],
                         'LOOP': {'freq': [(f'{q}', freq[i], 'Hz') for i, q in enumerate(qubits)],
                                  'trig': [(trigger, 0, 'any')]
                                  }
                         },
            }

# %% TimeRabi
qubits = ['Q0102', 'Q0204']
duration_times, points, signal = 5, 51, 'remote_iq_avg'
dts = [np.linspace(0, duration_times*s.query(f'gate.rfUnitary.{q}.params.duration')[1][-1], points) for q in qubits]
dts = np.asarray(dts).T
wop = []

timerabi = {'metainfo': {'name': f'{filename}:/TimeRabi', 'priority': priority, 'user': 'yltest',
                         'other': {'shots': 1024, 'signal': signal, 'autorun': True}
                         },
            'taskinfo': {'STEP': {'main': ['WRITE', ('dts',)],
                                  'tigger': ['WRITE', 'trig'],
                                  'READ': ['READ', 'read']
                                  },
                         'CIRQ': [[*[(('rfUnitary', np.pi, 0, ('with', ('param:duration', [[0, 0.5], [dt[i], dt[i]]]), *wop)), q) for i, q in enumerate(qubits)],
                                   ('Barrier', tuple(qubits)),
                                   *[(('Measure', i), q) for i, q in enumerate(qubits)]
                                   ] for dt in dts
                                  ],
                         'LOOP': {'dts': [(f'{q}', dts.T[i], 'Hz') for i, q in enumerate(qubits)],
                                  'trig': [(trigger, 0, 'any')]
                                  }
                         },
            }



# %% PowerRabi
qubits = ['Q0102','Q0204']
n, points, signal = 1, 21, 'remote_population'
scale = {q: s.query(f'gate.rfUnitary.{q}.params.amp') [-1][-1] for q in qubits}
amps = [generate_spanlist(center=scale[q], st=scale[q]*(1-1/n), ed=min(1, scale[q]*(1+1/n)), sweep_points=points, mode='log') for q in qubits]
amps = np.asarray(amps).T
wop = []

powerrabi = {'metainfo': {'name': f'{filename}:/PowerRabi', 'priority': priority, 'user': 'yltest',
                          'other': {'shots': 1024, 'signal': 'remote_population', 'autorun': True}
                         },
            'taskinfo': {'STEP': {'main': ['WRITE', ('amps',)],
                                  'tigger': ['WRITE', 'trig'],
                                  'READ': ['READ', 'read']
                                  },
                         'CIRQ': [[*[(('rfUnitary', np.pi, 0, ('with',('param:amp', [[0, 0.5], [0, amp[i]]]), *wop)), q) for i,q in enumerate(qubits)]*n,
                                   ('Barrier', tuple(qubits)),
                                   *[(('Measure', i), q) for i,q in enumerate(qubits)]
                                   ] for amp in amps
                                  ],
                         'LOOP': {'amps': [(f'{q}', amps.T[i], 'Hz') for i,q in enumerate(qubits)],
                                  'trig': [(trigger, 0, 'any')]
                                  }
                         },
            }



# %% Ramsey
qubit = ['Q0102','Q0204']
rotate, time_length, signal, name = 1e6, 10e-6, 'remote_iq_avg', 'Ramsey'
points_in_one_period = 10
times = np.linspace(0, time_length, round(time_length*rotate*points_in_one_period)+1)

ramsey = {'metainfo': {'name': f'{filename}:/Ramsey', 'priority': priority, 'user': 'yltest',
                       'other': {'shots': 1024, 'signal': signal}
                       },
          'taskinfo': {'STEP': {'main': ['WRITE', ('t',)],
                                'tigger': ['WRITE', 'trig'],
                                'reader': ['READ', 'read'],
                                },
                       'CIRQ': [[*[('X/2', q) for q in qubits],
                                 *[(('Delay', t), q) for q in qubits],
                                 *[(('rfUnitary', np.pi / 2, 2 * np.pi * rotate * t), q)
                                   for q in qubits],
                                 ('Barrier', tuple(qubits)),
                                 *[(('Measure', i), q) for i, q in enumerate(qubits)]
                                 ] for t in times
                                ],
                       'LOOP': {'t': [(f'{q}', times, 's') for q in qubits],
                                'trig': [(trigger, 0, 'any')]
                                }
                       },
          }


# %% T1
qubits = ['Q0102','Q0204']
time_length, signal = 92e-6, 'remote_population'
times = np.linspace(0, time_length, 51)

t1 = {'metainfo': {'name': f'{filename}:/T1', 'priority': priority, 'user': 'yltest',
                   'other': {'shots': 1024, 'signal': signal}
                   },
      'taskinfo': {'STEP': {'main': ['WRITE', ('t',)],
                            'tigger': ['WRITE', 'trig'],
                            'reader': ['READ', 'read'],
                            },
                   'CIRQ': [[*[(('rfUnitary', np.pi, 0), q) for q in qubits],
                             *[(('Delay', t), q) for q in qubits],
                             ('Barrier', tuple(qubits)),
                             *[(('Measure', j), q) for j, q in enumerate(qubits)],
                             ] for t in times
                            ],
                   'LOOP': {'t': [(f'{q}', times, 's') for q in qubits],
                            'trig': [(trigger, 0, 'any')],
                            'read': []
                            }
                   },
      }