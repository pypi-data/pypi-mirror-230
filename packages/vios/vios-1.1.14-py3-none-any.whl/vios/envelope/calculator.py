"""所有指令都会由此模块进行预处理, 如采样、失真、串扰等, 
并送入设备执行(见device模块)
"""

import numpy as np
from qlisp.kernel_utils import sample_waveform
from waveforms import Waveform, wave_eval


def calculate(step: str, target: str, cmd: list, targets: dict = {}):
    """指令的预处理

    Args:
        step (str): 步骤名, 如main/step1/...
        target (str): 设备通道, 如AWG.CH1.Offset
        cmd (list): 操作指令, 格式为(操作类型, 值, 单位, kwds). 其中
            操作类型包括WRITE/READ/WAIT, kwds见assembler.preprocess说明. 

    Returns:
        tuple: 预处理结果
    
    >>> calculate('main', 'AWG.CH1.Waveform',('WRITE',square(100e-6),'au',{'calibration':{}}))
    """
    ctype, value, unit, kwds = cmd

    line = {}

    if ctype != 'WRITE':
        return (step, target, cmd), line

    if isinstance(value, str):
        try:
            func = wave_eval(value)
        except SyntaxError as e:
            func = value
    else:
        func = value

    delay = 0

    if isinstance(func, Waveform):
        if target.startswith(tuple(kwds.get('filter', ['zzzzz']))):
            support_waveform_object = True
        else:
            support_waveform_object = False
        ch = kwds['target'].split('.')[-1]
        delay = kwds['calibration'][ch].get('delay', 0)
        cmd[1] = sample_waveform(func, kwds['calibration'][ch],
                                 sample_rate=kwds['srate'],
                                 start=0, stop=kwds['LEN'],
                                 support_waveform_object=support_waveform_object)
    else:
        cmd[1] = func

    cmd[-1] = {'sid': kwds['sid'], 'autokeep': kwds['autokeep'],
               'target': kwds['target'], 'srate': kwds['srate']}
    
    try:
        line = preview(target, cmd, targets, delay)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print('>'*30, '  failed to calculate waveform', e, type(e).__name__)

    return (step, target, cmd), line


def preview(target:str, cmd: dict, targets: dict = {}, delay: float = 0.0):
    """收集需要实时显示的波形

    Args:
        target (str): 设备.通道.属性, 波形目标地址.
        cmd (dict): 见calculator返回值.
        targets (dict, optional): 即etc.preview(为避免与preview函数同名). Defaults to {}.
        delay (float, optional): 通道延时, 扣除后即为从设备输出的波形. Defaults to 0.0.

    Returns:
        _type_: _description_
    """
    if not targets.get('filter', []):
        return {}

    if cmd[-1]['target'].split('.')[0] not in targets['filter'] or cmd[-1]['sid'] < 0:
        return {}

    if target.endswith('Waveform'):

        srate = cmd[-1]['srate']
        t1, t2 = targets['range']
        xr = slice(int(t1*srate), int(t2*srate))

        val = cmd[1]
        if isinstance(val, Waveform):
            val = val.sample()

        xt = (np.arange(len(val))/srate)[xr] - delay
        yt = val[xr]
        # val = np.random.random((1024000))

        # vals, idx = np.unique(yt > 0, return_counts=False, return_index=True)
        # start, stop = 10, -10
        # if len(idx) == 2:
        #     start, stop = idx[0]+start, idx[1]+stop
        # xx = np.hstack((xt[:start], xt[stop:]))
        # yy = np.hstack((yt[:start], yt[stop:]))

        # nz = yt.nonzero()[0]
        nz = (np.diff(yt)).nonzero()[0]
        xx = np.hstack((xt[:100], xt[nz[0]-100:nz[-1]+100], xt[-100:]))
        yy = np.hstack((yt[:100], yt[nz[0]-100:nz[-1]+100], yt[-100:]))

        return {cmd[-1]['target']: {'xdata': xx, 'ydata': yy, 'suptitle': cmd[-1]["sid"]}}
    return {}
                


if __name__ == "__main__":
    import doctest
    doctest.testmod()