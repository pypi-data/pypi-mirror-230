from typing import Callable, Any
import traceback
import sys


def make_verbose(func: Callable) -> Callable:
    def warp(*args: Any, **kwargs: Any) -> Any:
        args_str = str(args)
        kwargs_str = str(kwargs)
        if len(args_str) > 30:
            args_str = args_str[:10] + '...' + args_str[-10:]
        if len(kwargs_str) > 30:
            kwargs_str = kwargs_str[:10] + '...' + kwargs_str[-10:]
        print(
            f'[{func.__name__}]',
            f'START with input -- args: {args_str}; kwargs: {kwargs_str}')
        try:
            result = func(*args, **kwargs)
            print(f'END [{func.__name__}]')
        except BaseException as e:
            traceback.print_exc(file=sys.stdout)
            raise e
        return result
    return warp
