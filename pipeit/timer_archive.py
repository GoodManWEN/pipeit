import time
import array
import inspect
import struct
import dis
import random
import functools
from numbers import Number
from types import CodeType, FunctionType
from typing import Generator

try:
    _array_to_bytes = array.array.tobytes
except AttributeError:
    _array_to_bytes = array.array.tostring

class _Bytecode:
    def __init__(self):
        code = (lambda x,y: x if x else y).__code__.co_code
        opcode, oparg = struct.unpack_from('BB', code, 2)
        # Starting with Python 3.6, the bytecode format has changed, using
        # 16-bit words (8-bit opcode + 8-bit argument) for each instruction,
        # as opposed to previously 24 bit (8-bit opcode + 16-bit argument)
        # for instructions that expect an argument and otherwise 8 bit.
        # https://bugs.python.org/issue26647
        if dis.opname[opcode] == 'POP_JUMP_IF_FALSE':
            self.argument = struct.Struct('B')
            self.have_argument = 0
            # As of Python 3.6, jump targets are still addressed by their
            # byte unit. This is matter to change, so that jump targets,
            # in the future might refer to code units (address in bytes / 2).
            # https://bugs.python.org/issue26647
            self.jump_unit = 8 // oparg
        else:
            self.argument = struct.Struct('<H')
            self.have_argument = dis.HAVE_ARGUMENT
            self.jump_unit = 1

        self.has_loop_blocks = 'SETUP_LOOP' in dis.opmap

    @property
    def argument_bits(self):
        return self.argument.size * 8

_BYTECODE = _Bytecode()

class timeit:
    _count_target_prefix = ('JUMP_FORWARD', 'POP_JUMP_IF_TRUE', 'POP_JUMP_IF_FALSE', 'JUMP_IF_NOT_EXC_MATCH', 'JUMP_IF_TRUE_OR_POP', 'JUMP_IF_FALSE_OR_POP', 'JUMP_ABSOLUTE')
    
    def __init__(self, loops: Number = 1, name: str = ""):
        self._loop_num = loops
        if isinstance(self._loop_num, Number):
            self._loop_num = int(max(self._loop_num, 1))
        self._st_time = 0
        self.display_name = f'[{name}] ' if name != '' else f'[line {inspect.stack()[1].lineno}] '
    
    def __exit__(self,exc_type,exc_val,exc_tb):
        if exc_val:
            raise exc_val
        if self._loop_num <= 1:
            self._ed_time = time.time()
        else:
            self._new_func = functools.update_wrapper(
                FunctionType(
                    self._patch_code(self._codeobj, self._res_code),
                    self._new_func.__globals__,
                    self._new_func.__name__,
                    self._new_func.__defaults__,
                    self._new_func.__closure__,
                ),
                self._new_func
            )
            # dis.dis(self._new_func)
            self._st_time = self._new_func()
            self._ed_time = time.time()
        # scaller
        time_diff = self._ed_time - self._st_time
        if self._loop_num >= 1000000: 
            time_diff = time_diff * (1000000 / self._loop_num)
            unit = 'μs'
        elif self._loop_num >= 1000:
            time_diff = time_diff * (1000 / self._loop_num)
            unit = 'ms'
        else:
            unit = 's'
        # std output
        print(f"{self.display_name}time cost per loop: {time_diff}{unit}")

    def __enter__(self):
        code = inspect.currentframe().f_back.f_code
        if self._loop_num > 1:
            self._res_code, self._codeobj = self._body_customization(code)
        else:
            self._st_time = time.time()
        return self

    def _parse_instructions(self, code: CodeType) -> Generator[str, int, int]:
        
        extended_arg = 0
        extended_arg_offset = None
        pos = 0
        while pos < len(code):
            offset = pos
            if extended_arg_offset is not None:
                offset = extended_arg_offset

            opcode = struct.unpack_from('B', code, pos)[0]
            pos += 1
            oparg = None
            if opcode >= _BYTECODE.have_argument:
                oparg = extended_arg | _BYTECODE.argument.unpack_from(code, pos)[0]
                pos += _BYTECODE.argument.size

                if opcode == dis.EXTENDED_ARG:
                    extended_arg = oparg << _BYTECODE.argument_bits
                    extended_arg_offset = offset
                    continue

            extended_arg = 0
            extended_arg_offset = None
            yield dis.opname[opcode], oparg, offset
    
    def _cross_border_inspection(self, t_code: list[list]) -> list[list]:
        # Preventing large numbers from geting out of 0-255 range
        pointer = 0
        length = len(t_code)
        while pointer < length:
            target = t_code[pointer]
            if target[1] > 255:
                t_code.insert(pointer, ['EXTENDED_ARG', target[1]//256])
                target[1] = target[1]%256
                pointer -= 1
            pointer += 1
        return t_code

    def _body_customization(self, code: CodeType) -> (list[tuple[str, int, int]], CodeType):
        search_index = []
        for kw in ('pipeit', 'timeit'):
            if kw in code.co_names:
                search_index.append(code.co_names.index(kw))
        if len(search_index) <= 0:
            raise RuntimeError('No context manager named `timeit` found in the bytecode')
        # spt -> end row idx of context manager preload,
        spt = None
        parsed_gen = self._parse_instructions(code.co_code)
        parsed_head_lst, parsed_mid_lst, parsed_tail_lst = [], [], []
        with_prelod_lst, with_wrapup_lst = [], []

        # catch with preload start position
        for opcode_str, oparg, offset in parsed_gen:
            if opcode_str in ('LOAD_NAME', 'LOAD_GLOBAL') and oparg in search_index: 
                with_prelod_lst.append((opcode_str, oparg, offset)); break
            parsed_head_lst.append((opcode_str, oparg, offset))

        # catch with perload end position
        for opcode_str, oparg, offset in parsed_gen:
            with_prelod_lst.append((opcode_str, oparg, offset))
            if opcode_str == 'SETUP_WITH':
                spt, _dest = offset, oparg; break
        opcode_str, oparg, offset = parsed_gen.send(None)
        if opcode_str in ('POP_TOP', 'STORE_FAST', 'STORE_NAME'):
            # https://docs.python.org/zh-cn/3/library/dis.html?highlight=setup_with
            with_prelod_lst.append((opcode_str, oparg, offset))

        # catch code body
        for opcode_str, oparg, offset in parsed_gen:
            if opcode_str in ('LOAD_NAME', 'LOAD_GLOBAL') and oparg in search_index:
                raise RuntimeError("Nested use of timeit() is not allowed.")
            parsed_mid_lst.append((opcode_str, oparg, offset))
            if offset < max(_dest, spt):
                continue
            if opcode_str == 'WITH_EXCEPT_START':
                with_wrapup_lst.append((opcode_str, oparg, offset))
                for opcode_str, oparg, offset in parsed_gen:
                    with_wrapup_lst.append((opcode_str, oparg, offset))
                    if opcode_str == 'POP_JUMP_IF_TRUE':
                        _toffset = oparg; break
                for opcode_str, oparg, offset in parsed_gen:
                    with_wrapup_lst.append((opcode_str, oparg, offset))
                    if offset >= _toffset: break
                for opcode_str, oparg, offset in parsed_gen:
                    if opcode_str not in ('POP_TOP', 'POP_EXCEPT'): 
                        parsed_tail_lst.append((opcode_str, oparg, offset)); break
                    with_wrapup_lst.append((opcode_str, oparg, offset))
                break
        
        # catch with wrapup
        _poped = parsed_mid_lst.pop()
        while _poped:
            with_wrapup_lst.insert(0, _poped)
            if _poped[0] == 'POP_BLOCK': break
            _poped = parsed_mid_lst.pop()
        for opcode_str, oparg, offset in parsed_gen:
            parsed_tail_lst.append((opcode_str, oparg, offset))
        
        # assemble result
        res_code = []
        random_name = lambda :"_{0}".format(hex(random.randint(int(1e8), int(1e9))))
        # st_time_var_name, loop_var_name = random_name(), random_name()
        st_time_var_name, loop_var_name = '_0x3af1bfa3', '_0x1b2a6808'
        _varnames, _consts, _names = list(code.co_varnames), list(code.co_consts), list(code.co_names)
        st_time_var_index = len(_varnames)
        _varnames.append(st_time_var_name)
        loop_var_index = len(_varnames)
        _varnames.append(loop_var_name)
        loop_const_var_index = len(_consts)
        _consts.append(self._loop_num)

        if 'time' in code.co_names:
            time_var_index = code.co_names.index('time')
        else:
            time_var_index = len(_names)
            _names.append('time')
        if 'range' in code.co_names:
            range_var_index = code.co_names.index('range')
        else:
            range_var_index = len(_names)
            _names.append('range')
        code = code.replace(
            co_varnames = tuple(_varnames), 
            co_nlocals = code.co_nlocals + 2, 
            co_consts = tuple(_consts), 
            co_names = tuple(_names)
        )
        res_code.extend(parsed_head_lst)
        last_offset = (parsed_mid_lst[-1][2] if len(parsed_mid_lst) > 0 else with_wrapup_lst[0][2]) - with_prelod_lst[-1][2] + 4
        jump_offset = (with_prelod_lst[0][2] if len(with_prelod_lst) > 0 else 0) + 16
        t_code = [
            ['LOAD_GLOBAL', time_var_index],
            ['LOAD_METHOD', time_var_index],
            ['CALL_METHOD', 0],
            ['STORE_FAST', st_time_var_index],
            ['LOAD_GLOBAL', range_var_index],
            ['LOAD_CONST', loop_const_var_index],
            ['CALL_FUNCTION', 1],
            ['GET_ITER', 0],
            ['FOR_ITER', last_offset], 
            ['STORE_FAST', loop_var_index],
        ]
        t_code = self._cross_border_inspection(t_code)
        _l_addcode, _l_with_preload = len(t_code), len(with_prelod_lst)
        _l_prefix = (_l_addcode - _l_with_preload) * 2
        res_code.extend(map(lambda x: (*x[0], x[1]), zip(t_code, list(range(last_offset, last_offset + _l_addcode*2, 2)))))
        res_code.extend(map(lambda x: (x[0], x[1] + _l_prefix if x[0] in self._count_target_prefix else x[1], x[2] + _l_prefix), parsed_mid_lst))
        last_offset = with_wrapup_lst[0][2] - parsed_mid_lst[-1][2] if len(parsed_mid_lst) > 0 else with_prelod_lst[-1][2] + res_code[-1][2]
        t_code = [
            ['JUMP_ABSOLUTE', jump_offset],
            ['LOAD_FAST', st_time_var_index],
            ['RETURN_VALUE', 0],
        ]
        t_code = self._cross_border_inspection(t_code)
        res_code.extend(map(lambda x: (*x[0], x[1]), zip(t_code, list(range(last_offset, last_offset + _l_addcode*2, 2)))))
        return res_code, code

    def _make_code(self, code: CodeType, codestring: bytes) -> CodeType:
        # codestring may be in string type in python 3.6
        try:
            return code.replace(co_code=codestring)  # new in 3.8+
        except AttributeError:
            args = [
                code.co_argcount,  code.co_nlocals,     code.co_stacksize,
                code.co_flags,     codestring,          code.co_consts,
                code.co_names,     code.co_varnames,    code.co_filename,
                code.co_name,      code.co_firstlineno, code.co_lnotab,
                code.co_freevars,  code.co_cellvars
            ]
            try:
                args.insert(1, code.co_kwonlyargcount)  # PY3
            except AttributeError:
                pass
            return CodeType(*args)

    def _patch_code(self, code: CodeType, code_asm: list[tuple[str, int, int]]) -> CodeType:
        buf = array.array('B', [x for y in [[dis.opname.index(x[0]), x[1]] for x in code_asm] for x in y])
        return self._make_code(code, _array_to_bytes(buf))

    def _new_func(self):
        ...
