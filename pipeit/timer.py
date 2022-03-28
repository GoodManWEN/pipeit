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
    # The default is to use peeloff mode, which re-executes the iterator with empty body 
    # and subtracts this amount of time. This can increase the precision of the result, 
    # you can turn it off manually if you don't like it.
    '''

    instance_no = 0

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance._instance_no = cls.instance_no
        cls.instance_no += 1
        return instance

    def __init__(self, loops: Number = 1, name: str = "", peel_off: bool = True):
        self._loop_num = int(loops)
        self.display_name = f'[{name}]' if name != '' else f'[line {stack()[1].lineno}]'
        self._count = 0
        self._mode = None
        self._peel_off = peel_off
        self._poff_firstloop_flag = True

    def __iter__(self):
        self._mode = 'approximate'
        self._st_time = time.perf_counter_ns()       
        return self 

    def __next__(self):
        '''
        Python for循环本身的速度会随调用位置的不同发生变化，因为需要yeild将状态提交至上层
        而上层修改locals或globals本身就有开销。比如在__main__里调用for循环的单圈开销大概
        在30ns左右，进入函数执行后大概在20ns，而极限情况（如__next__内部）则可缩短至10ns
        另外如果手动实现__next__的话对比循环数，如果双方类型为int和float不对等的话同样
        也有几纳秒的开销（虽然这种转换在字节码中并不显式可见）。

        由于手动定义__next__带来的开销是比较惊人的，由于指针索引开销，单圈空转速度会减慢
        五到十倍。另一方面，可以使用装饰器+nonlocal闭包的方式将这种状态保存于非索引中，使用
        这种方法定义__next__的话可以显著加快手动定义函数的执行速度。但由于CPython解释器上
        的BUG（并不确定，但如果它是BUG的话），__next__本身的定义行为在__new__之前发生
        且无法被动态修改（BUG指此处行为），这导致如果使用闭包定义则必须在init前运行代码段
        这使得传入loops参数变得不可能，所以还是无法使用。最终如果我们意图少写代码的话我们还是
        要面对只能得到一个估算值的处境。

        如果需要非常严格的计算的话，还是需要在同一scope内进行手动去皮操作，并多次执行以减小
        系统负载误差，可以得到一个比较严格的比较。目前的估测值的话，对应越复杂的计算误差越小
        （因额外开销占比例减小），举例来说通常的小巧的100位列表合并误差约在2%，而对于最基础的
        常数赋值，误差则在+—50%之间。即例如计算得单步耗时8ns，实际耗时必定处于4-16ns区间。
        '''
        ret = self._count
        if ret < self._loop_num:
            self._count += 1
            return ret 
        else:
            self._ed_time = time.perf_counter_ns()
            if self._peel_off:
                if self._poff_firstloop_flag:
                    self._t_storage = self._ed_time - self._st_time
                    self._poff_firstloop_flag = False
                    self._count = 0
                    # limit max blank loop times under 1e7 for normal cpus / at py3.9 performance
                    self._amplifier = 1
                    self._ln_buffer = self._loop_num
                    if self._loop_num > 1e7:
                        self._amplifier = self._loop_num / 1e7
                        self._loop_num = int(1e7)
                    for _ in self:
                        None
                else:
                    self._poff_storage = (self._ed_time - self._st_time) * self._amplifier
                    self._loop_num = self._ln_buffer
                    raise StopIteration
            self._sout()
            raise StopIteration

    def __enter__(self):
        self._peel_off = False
        self._st_time = time.perf_counter_ns()
        self._mode = 'exact'
        return self

    def __exit__(self,exc_type,exc_val,exc_tb):
        self._ed_time = time.perf_counter_ns()
        self._sout(extra=False)
        if exc_val:
            raise exc_val

    def _sout(self, extra=True):
        if self._peel_off:
            time_diff = max(self._t_storage - self._poff_storage, 0) / 1e9
        else:
            time_diff = max((self._ed_time - self._st_time),0) / 1e9
        unit = 's'
        if extra:
            if self._loop_num >= 1000000: 
                time_diff = time_diff * (1000000 / self._loop_num)
                unit = 'μs'
            elif self._loop_num >= 1000:
                time_diff = time_diff * (1000 / self._loop_num)
                unit = 'ms'
            else:
                time_diff = time_diff / self._loop_num
        # std output
        print(f"{self.display_name}[{self._mode}] time cost{' / loop'if extra else ''}: {time_diff}{unit}{f', total time {self._t_storage/1e9}s' if extra else ''}")