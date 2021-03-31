import time
import inspect
from sys import version_info

version = version_info.major * 10 + version_info.minor

if version >= 36:
    class timeit:
        def __init__(self, name=""):
            self.st_time = 0
            self.display_name = f'[{name}] ' if name != '' else f'[line {inspect.stack()[1].lineno}] '

        def __enter__(self):
            self.st_time = time.time()
            return self

        def __exit__(self,exc_type,exc_val,exc_tb):
            print(f"{self.display_name}time cost: {time.time() - self.st_time}")
            if exc_val:
                raise exc_val
else:
    class timeit:
        def __init__(self, name=""):
            self.st_time = 0
            self.display_name = '[{}] '.format(name) if name != '' else '[line {}] '.format(inspect.stack()[1].lineno)

        def __enter__(self):
            self.st_time = time.time()
            return self

        def __exit__(self,exc_type,exc_val,exc_tb):
            print("{}time cost: {}".format(self.display_name, time.time() - self.st_time))
            if exc_val:
                raise exc_val
 
