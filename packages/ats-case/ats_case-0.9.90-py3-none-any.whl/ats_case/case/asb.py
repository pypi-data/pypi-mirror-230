import re

from ats_base.service import mm
from ats_case.case.context import Context

NAME = 'session'

VF = {
    'result': '~result::(.+?)\'',
    'global': '~global::(.+?)\'',
    'session': '~session::(.+?)\''
}

VH = {
    'result': 'context.runtime.sos[{}]["result"]',
    'global': 'context.runtime.glo.get("{}")',
    'session': 'asb.Session.get(context, "{}")',
    'build_in': 'asb.build_in_handle(context, "{}")'
}


def V_loop(context: Context, sd):
    sd = _replace_build_in(context, sd)
    sd = _replace_context(context, sd)
    sd = _replace_common(context, sd)

    return sd


def _replace_common(context: Context, sd: str):
    for word, search_format in VF.items():
        re_list = re.findall(r"{}".format(search_format), sd)
        if len(re_list) <= 0:
            re_list = re.findall(r"{}$".format(search_format[:-1]), sd)

        for key in re_list:
            var = sd.replace('\'~{}::{}\''.format(word, key), VH[word].format(key))
            if var == sd:
                var = sd.replace('~{}::{}'.format(word, key), VH[word].format(key))
            sd = var

    return sd


def _replace_context(context: Context, sd):
    re_list = re.findall(r"#(.+?)\'", sd)
    if len(re_list) <= 0:
        re_list = re.findall(r"#(.+)", sd)

    for c in re_list:
        var = sd.replace('\'#{}\''.format(c), c)
        if var == sd:
            sd.replace('#{}'.format(c), c)
        sd = var

    return sd


def _replace_build_in(context: Context, sd):
    re_list = re.findall(r"~build_in::(.+?)::(.+?)\'", sd)
    if len(re_list) <= 0:
        re_list = re.findall(r"~build_in::(.+?)::(.+?)$", sd)

    if len(re_list) > 0:
        pd = {}
        for f in re_list:
            op = f[0]
            params = f[1]
            pa_list = params.findall(r"(\w*)=([~#.:\w]*)", sd)
            for p in pa_list:
                v = _replace_context(context, p[1])
                v = _replace_common(context, p[1])
                pd[p[0]] = v

            var = sd.replace('\'~build_in::{}::{}\''.format(op, params),
                             'build_in.handle(function="{}", data={}, debug_url=context.debug_service_url.get('
                             '"build_in")) '.format(op, str(pd)))
            if var == sd:
                var = sd.replace('~build_in::{}::{}'.format(op, params),
                                 'build_in.handle(function="{}", data={}, debug_url=context.debug_service_url.get('
                                 '"build_in")) '.format(op, str(pd)))
            sd = var

    return sd


"""
    Redis缓存
"""


class Session(object):
    NAME = 'session'

    @staticmethod
    def get(context: Context, key: str):
        session = mm.Dict.get(context.test_sn, Session.NAME)
        if isinstance(session, dict):
            return session.get(key)

        return None

    @staticmethod
    def set(context: Context, key: str, data):
        session = mm.Dict.get(context.test_sn, Session.NAME)

        kv = {key: data}
        if isinstance(session, dict):
            session.update(kv)
            mm.Dict.put(context.test_sn, Session.NAME, session)
        else:
            mm.Dict.put(context.test_sn, Session.NAME, kv)

    @staticmethod
    def delete(context: Context, key: str):
        session = mm.Dict.get(context.test_sn, Session.NAME)

        if isinstance(session, dict):
            try:
                session.pop(key)
                mm.Dict.put(context.test_sn, Session.NAME, session)
            except:
                pass


class BreakPoint(object):
    NAME = 'breakpoint'

    @staticmethod
    def get(context: Context, key: str):
        session = mm.Dict.get(context.test_sn, BreakPoint.NAME)
        if isinstance(session, dict):
            return session.get(key)

        return None

    @staticmethod
    def set(context: Context, key: str, data):
        session = mm.Dict.get(context.test_sn, BreakPoint.NAME)

        kv = {key: data}
        if isinstance(session, dict):
            session.update(kv)
            mm.Dict.put(context.test_sn, BreakPoint.NAME, session)
        else:
            mm.Dict.put(context.test_sn, BreakPoint.NAME, kv)

    @staticmethod
    def delete(context: Context, key: str):
        session = mm.Dict.get(context.test_sn, BreakPoint.NAME)

        if isinstance(session, dict):
            try:
                session.pop(key)
                mm.Dict.put(context.test_sn, BreakPoint.NAME, session)
            except:
                pass


def test_log(test_sn):
    return mm.Dict.get("test:log", test_sn)


def flush(context: Context):
    mm.delete(context.test_sn)
