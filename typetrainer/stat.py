import os.path
from datetime import datetime
from hashlib import md5

class FileStatistic(object):
    def __init__(self, root):
        self.root = root

    def get_filename(self, name):
        return os.path.join(self.root, md5(name).hexdigest())

    def log(self, name, cpm, accuracy, dt=None):
        dt = dt or datetime.now()

        fname = self.get_filename(name)
        existed_before = os.path.exists(fname)
        f = open(fname, 'a')

        if not existed_before:
            f.write(name + '\n')

        f.write("{0} {1} {2}\n".format(dt.strftime('%Y-%d-%m %H:%M'), cpm, accuracy))
        f.close()