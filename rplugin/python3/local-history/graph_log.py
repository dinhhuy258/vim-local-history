import time
from collections import OrderedDict


def build_graph_log(changes: OrderedDict) -> list:
    lines = []
    for index, change in changes.items():
        line = 'o  [%d] %-10s' % (index, _calculate_age(change.timestamp))
        if (len(lines) >= 1):
            lines.append('|')
        lines.append(line)

    lines.reverse()
    return lines


def _calculate_age(timestamp: float) -> str:

    def format(t, c):
        return "%d %s" % (int(c), t if c == 1 else t + "s")

    delta = max(1, int(time.time() - int(timestamp)))
    if delta > 3600 * 24:
        return time.strftime('%d-%m-%Y %H:%M', time.gmtime(float(timestamp)))

    h = delta // 3600  # 1 hour = 3600 seconds
    if h >= 1:
        m = (delta % 3600) // 60
        return '%s%s ago' % (format('hour', h), '' if m == 0 else ' ' + format('minute', m))

    m = delta // 60  # 1 minute = 60 seconds
    if m >= 2:
        return '%s ago' % format('minute', m)

    return '< 1 min ago'
