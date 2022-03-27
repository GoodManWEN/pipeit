import time
from inspect import stack
from numbers import Number

class timeit:
    '''
    Usage:

    1.
    >>> with timeit(name = 'no1'):
    >>>     for _ in range(1000000):
    >>>         # code to test
    >>>         ''.join(['1']*100)
    
    [no1][exact] time cost: 0.890207052230835s

    2. 
    # Cleaner to write, but __next__ itself has a higher overhead and will increase execute time
    >>> for _ in timeit(1e6, name = 'no2'):
    >>>     # code to test
    >>>     ''.join(['1']*100)

    [no2][approximate] time cost / loop: 1.0502512454986572μs
    '''

    instance_no = 0

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance._instance_no = cls.instance_no
        cls.instance_no += 1
        return instance

    def __init__(self, loops: Number = 1, name: str = ""):
        self._loop_num = int(loops)
        self.display_name = f'[{name}] ' if name != '' else f'[line {stack()[1].lineno}]'
        self._count = 0
        self._mode = None

    def __iter__(self):
        self._st_time = time.time()
        self._mode = 'approximate'
        return self 

    def __next__(self):
        if self._count < self._loop_num:
            ret = self._count 
            self._count += 1
            return ret 
        else:
            self._ed_time = time.time()
            self._sout()
            raise StopIteration

    def __enter__(self):
        self._st_time = time.time()
        self._mode = 'exact'
        return self

    def __exit__(self,exc_type,exc_val,exc_tb):
        self._ed_time = time.time()
        self._sout(extra=False)
        if exc_val:
            raise exc_val

    def _sout(self, extra=True):
        time_diff = self._ed_time - self._st_time
        unit = 's'
        if extra:
            if self._loop_num >= 1000000: 
                time_diff = time_diff * (1000000 / self._loop_num)
                unit = 'μs'
            elif self._loop_num >= 1000:
                time_diff = time_diff * (1000 / self._loop_num)
                unit = 'ms'
        # std output
        print(f"{self.display_name}[{self._mode}] time cost{' / loop'if extra else ''}: {time_diff}{unit}")
