import os.path
from datetime import datetime
from hashlib import md5

DATE_FORMAT = '%Y-%m-%d %H:%M'

class FileStatistic(object):

    def __init__(self, root):
        self.root = root

    def get_filename(self, name):
        return os.path.join(self.root, md5(name + 'v1').hexdigest())

    def log(self, name, cpm, accuracy, dt=None):
        dt = dt or datetime.now()

        fname = self.get_filename(name)
        existed_before = os.path.exists(fname)
        f = open(fname, 'a')

        if not existed_before:
            f.write(name + '\n')

        f.write("{0} {1} {2}\n".format(dt.strftime(DATE_FORMAT), cpm, accuracy))
        f.close()

    def get(self, name, accuracy):
        result = {}

        with open(self.get_filename(name)) as f:
            skip_first = True
            for l in f:
                if skip_first:
                    skip_first = False
                    continue

                try:
                    dt, cpm, acc = l.strip().rsplit(' ', 2)
                except ValueError:
                    continue

                acc = float(acc)
                if acc < accuracy:
                    continue

                cpm = float(cpm)
                dt = datetime.strptime(dt, DATE_FORMAT).date()

                try:
                    avg, cnt = result[dt]
                except KeyError:
                    avg, cnt = 0.0, 0

                result[dt] = ( avg * cnt + cpm ) / (cnt + 1.0), cnt + 1

        return result