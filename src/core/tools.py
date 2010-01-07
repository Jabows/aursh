# -*- coding: utf-8 -*-


import re



RX_VERSION_SEP = re.compile(r'[.-]')

def compare_versions(v1, v2):
    """Compare two versions in any format. Returns 1 if `v1` is greater than
    `v2`. 0 if they are equal. If `v2` is greater than `v1`, returns  -1.
    """
    def _prepare_version_tokens(version):
        "Return version tokens in reverse order"
        version = RX_VERSION_SEP.split(version)
        version.reverse()
        return version
    def _compare_tokens(t1, t2):
        if t1 == t2:
            return 0
        try:
            t1 = int(t1)
            t2 = int(t2)
        except ValueError:
            raise TypeError('Dono how to compare such versions!')
        if t1 > t2:
            return 1
        return -1

    if v1 == v2:
        return 0
    v1 = _prepare_version_tokens(v1)
    v2 = _prepare_version_tokens(v2)
    tokens = zip(v1, v2)
    for n, (token1, token2) in enumerate(tokens):
        result = _compare_tokens(token1, token2)
        if result == 0:
            continue
        return result
    return 0


def format_docstring(object, lmargin=20):
    "Return formatted docstring"
    doc = getattr(object, '__doc__', '')
    if not doc:
        return ''
    joiner = '\n' + (' ' * lmargin)
    doc = doc.strip()
    doc = doc.split('\n')
    return joiner.join(line.strip() for line in doc)
