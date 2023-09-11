import re
import time

from ats_base.common import func
from ats_base.log.logger import logger
from ats_base.service import app, mm, db

from ats_case.case.context import Context
from ats_case.common.enum import *
from ats_case.common.error import *

METER_NO_RESPONSE_FRAME = '无响应帧'
METER_SLEEP_MESSAGE = '系统休眠{}秒, 等待电表操作完毕...'
BENCH_SLEEP_MESSAGE = '系统休眠{}秒, 等待表台调整完毕...'
JUMP_MESSAGE = '###步骤跳转[第{}次/共{}次] - 跳转并开始执行第{}步'

CODE_ERROR = '服务内部代码发生异常'

"""
    基础操作
"""


def send(context: Context, todo: dict, types=2, end=0, retry_times: int = 3):
    """
    发送操作命令 - 向测试端app
    :param context:         上下文
    :param todo:            任务
    :param types:
    :param end:
    :param retry_times:     失败重试次数（默认：3次）
    :return:
    """
    result = None

    try:
        data = {
            'type': types,
            'end': end,
            'exec_time': func.sys_current_time(),
            'test_sn': context.test_sn,
            'case_id': context.case.id,
            'meter_pos': context.meter.pos,
            'step_id': context.runtime.step,
            'todo': todo
        }

        logger.info('~ @TCC-SEND-> client:{} data:{}'.format(context.tester.api, data))
        result = app.send(context.tester.api, data)
        logger.info('~ @TCC-SEND<- result:{}'.format(result))
    # except requests.exceptions.MissingSchema as me:
    #     logger.error(str(me))
    #     raise AssertionError(str(me))
    except Exception as ae:
        logger.error(str(ae))

        retry_times -= 1
        if retry_times <= 0:
            raise APIError(context.tester.api)
        else:
            sleep(5)
            send(context, todo, types, retry_times=retry_times)

    return result


def sleep(seconds: float):
    """
    休眠
    :param seconds:     秒
    :return:
    """
    logger.info('~ @TCC-SLEEP-> {}secs'.format(seconds))
    time.sleep(seconds)


"""
    公共函数
"""


def offbench(context: Context, disabled=1):
    """
    脱表台
    :param context:
    :param disabled:     使能
    :return:
    """
    clazz = OperationClazz(context.case.steps[str(context.runtime.step)].get('type'))

    if disabled == 1:
        if clazz == OperationClazz.BENCH:
            return True

    return False


def replace_context(context: Context, data: dict):
    sd = str(data)

    re_list = re.findall(r"#(.+?)\'", sd)
    for r in re_list:
        v = eval(r)
        if type(v) is str:
            sd = sd.replace('#{}'.format(r), v)
        else:
            sd = sd.replace('\'#{}\''.format(r), str(v))

    return eval(sd)


def replace_global_result(context: Context, data):
    if data is None:
        return None
    if isinstance(data, int) or isinstance(data, float):
        return data
    if isinstance(data, str):
        sd = data
        if sd.find('~') < 0:
            return data
        else:
            index = sd.find('::')
            key = sd[index + 2:]

            if sd.find('global') >= 0:
                sd = 'context.runtime.glo.get("{}")'.format(key)
            if sd.find('result') >= 0:
                sd = 'context.runtime.sos[{}]["result"]'.format(key)
    else:
        sd = str(data)

    re_list = re.findall(r"~(.+?)\'", sd)
    for r in re_list:
        index = r.find('::')
        if index > 0:
            key = r[index + 2:]
            gl = r.find('global')
            if gl >= 0:
                sd = sd.replace('\'~{}\''.format(r), 'context.runtime.glo.get("{}")'.format(key))
            rt = r.find('result')
            if rt >= 0:
                sd = sd.replace('\'~{}\''.format(r), 'context.runtime.sos[{}]["result"]'.format(key))

    return eval(sd)


def end_step(context: Context, types):
    if types == 1:
        if context.mode == WorkMode.FORMAL:
            if context.case.end == 1 and context.meter.end == 1:
                flush_mm(context.test_sn)
                end_save(context.test_sn.split(':')[0])
                return 1
        else:  # Debug模式
            flush_mm(context.test_sn)
            return 1
    return 0


def flush_mm(test_sn: str):
    mm.delete(test_sn)


def end_save(sn: str):
    db.update('test:log', condition=func.to_dict(sn=sn), end_time=func.sys_current_time())


"""
    测试报告
"""


def build_in_result(operation, parameter, result, tag, err: str = None):
    """
    格式化结论
    :param operation:
    :param parameter:
    :param result:
    :param tag:
    :param err:
    :return:
    """
    msg = []

    if tag == 1:
        msg.append('结论: {}.'.format('合格'))
    else:
        msg.append('结论: {}.'.format(CODE_ERROR))

    msg.append('\r\n--------------------详细---------------------')

    if operation is not None:
        msg.append('\r\n内置方法: {}'.format(operation))
    if parameter is not None:
        msg.append('\r\n方法参数: {}'.format(parameter))
    if err is not None:
        msg.append('\r\n返回异常: {}'.format(err))
    else:
        if result is not None:
            msg.append('\r\n返回结果: {}'.format(result))

    return ''.join(msg) + '\r\n'


def jump_result(result, jump_times, times, step):
    """
    格式化结论
    :param result:
    :param jump_times:
    :param times:
    :param step:
    :return:
    """
    msg = []

    if isinstance(result, str) and len(result) > 0:
        msg.append(result)
        msg.append('\r\n' + JUMP_MESSAGE.format(jump_times, times, step))
    else:
        msg.append('结论: {}.'.format('合格'))
        msg.append('\r\n--------------------详细---------------------')
        msg.append('\r\n' + JUMP_MESSAGE.format(jump_times, times, step))

    return ''.join(msg) + '\r\n'


def test_report(context: Context):
    sc = fc = 0
    fs = []
    error = None
    for s, result in context.runtime.sas.items():
        if str(result).find(CODE_ERROR) >= 0:
            error = result
            break

        if str(result).find('不合格') >= 0:
            fc += 1
            fs.append(str(s))
        else:
            sc += 1

    pattern = "{0:<11}\t{1:<6}\r\n"
    if error is not None:
        msg = pattern.format('系统错误:', '用例执行第{}步时, {}'.format(context.runtime.step, error))
    else:
        msg = pattern.format('用例步骤:', '{}步'.format(len(context.case.steps)))
        msg += pattern.format('执行合格:', '{}步'.format(sc))
        msg += pattern.format('执行不合格:', '{}步 ~ {}'.format(fc, ','.join(fs)))

    return msg
