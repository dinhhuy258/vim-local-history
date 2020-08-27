import time
from collections import OrderedDict

_AGE_SCALES = [("yr", 3600 * 24 * 365), ("mon", 3600 * 24 * 30),
               ("wk", 3600 * 24 * 7), ("dy", 3600 * 24), ("hr", 3600),
               ("min", 60)]


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
    def plural(t, c):
        if c == 1:
            return t
        return t + "s"

    def format(t, c):
        return "%d %s" % (int(c), plural(t, c))

    delta = max(1, int(time.time() - int(timestamp)))
    if delta > _AGE_SCALES[0][1] * 2:
        return time.strftime('%Y-%m-%d', time.gmtime(float(timestamp)))

    for t, s in _AGE_SCALES:
        n = delta // s
        if n >= 2 or s == 1:
            return '%s ago' % format(t, n)

    return "<1 min ago"
