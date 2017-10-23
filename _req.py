# ======================================================================================================================
# Copyright 2016 Zachariah Carmichael
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
# ======================================================================================================================
import six
from functools import wraps  # Python 2.5+


# Special case constants
class ARGS:
    """Constant to indicate a *arg special case for validation."""
    pass


class KWARGS:
    """Constant to indicate a **kwarg special case for validation."""
    pass


def req(*args):
    """Decorator for any function to validate its arguments seamlessly.

    Args:
        *args: Tuples of indices and/or names in position 0 and `Arg` instances in position 1. For docs on
               specifications for `Arg`, view the `Arg` class.

    Examples:
        Below, Arg() is used for all `Arg` instances. To specify what to validate, view the possible specifications
        to the `Arg` class.

        Some basic usage:
            @req(
                (3, Arg()),                     # Validate a single index
                ((1, 2), Arg()),                # Validate multiple indices
                (ARGS, Arg()),                  # Validate the rest of func *args (ARGS special case)
                ((4, 'slug'), Arg()),           # Validate a mixture of kwargs and args.
                ('test', Arg()),                # Validate a single name
                (('spec', 'index'), Arg()),     # Validate multiple names
                (KWARGS, Arg())                 # Validate the rest of func **kwargs (KWARGS special case)
            )
        These specifications also work:
            @req(
                ((-1, -2), Arg())               # Validate the last and second to last indices of *args
                ((2, 4, ARGS), Arg()),          # Validate indices 2 and 4, and remaining *args
                (('test', KWARGS), Arg())       # Validate name 'test' and remaining **kwargs
            )
            @req(
                ((2, 'test', ARGS), Arg()),     # Validate index 2, name 'test' and remaining *args
                (('pid', 2, 1, KWARGS), Arg())  # Validate name 'pid', indices 2 and 1, and remaining **kwargs
            )
        These specifications don't work:
            @req(
                (2, Arg()),                     # Validate index 2
                ((1, 2, 3), Arg())              # ValueError raised due to index 2 being validated prior
            )
            @req(
                ((2, -1), Arg())                # This fails if *args has length 3 (arg[2] == arg[-1])
            )

    NOTE: The order of args/kwargs/special cases doesn't matter; the order of validation is as follows:
        1. Specified indices and kwargs in the order they appear to `req`
        2. ARGS special case
        3. KWARGS special case

    Raises:
        ValueError: ARGS or KWARGS specified more than once, or an index or name specified more than once.
        Others: See the `validate` function doc under the class `Arg` for exceptions raised due to invalid user
            specification.
    """

    def validation_decorator(func):
        """Decorator for a function `func` which validates provided arguments according to the
        specifications of `req`."""

        @wraps(func)
        def func_wrapper(*func_args, **func_kwargs):
            """Wrapper for a function. Uses all provided args and kwargs."""
            # Handled (visited) args
            visited_args = set()
            # Handled (visited) kwargs
            visited_kwargs = set()
            # Number of function args, used to obtain actual index from negative indices
            num_func_args = len(func_args)
            # Placeholder for ARGS to be handled last
            args_special_case = None
            # Placeholder for KWARGS to be handled last
            kwargs_special_case = None

            def _validate_arg(_index_or_name, _arg_instance):
                """Validates an arg or kwarg using `_arg_instance` (Arg instance). `_index_or_name` should be
                `int` or `str`."""
                # Define var scope
                global args_special_case, kwargs_special_case
                # Check ARGS/KWARGS special cases
                if _index_or_name is ARGS:
                    if args_special_case is not None:
                        raise ValueError('`ARGS` specified multiple times in input.')
                    args_special_case = _arg_instance
                    # Break function; ARGS special case handled at end
                    return
                elif _index_or_name is KWARGS:
                    if kwargs_special_case is not None:
                        raise ValueError('`KWARGS` specified multiple times in input.')
                    kwargs_special_case = _arg_instance
                    # Break function; KWARGS special case handled at end
                    return
                # Not ARGS/KWARGS special cases: continue
                if isinstance(_index_or_name, six.string_types):  # Name (kwarg)
                    # Ensure name hasn't been handled
                    if _index_or_name in visited_kwargs:
                        raise ValueError(
                            'Specified kwarg was already handled by another `Arg` instance: {}'.format(_index_or_name))
                    # Store name
                    visited_kwargs.add(_index_or_name)
                    # Validate kwarg
                    _arg_instance.validate(func_kwargs[_index_or_name], index=_index_or_name)
                else:  # Assume `_index_or_name` is int index (arg)
                    # Store index as positive/actual value
                    if _index_or_name < 0:
                        _index_or_name += num_func_args
                    # Ensure index hasn't been handled
                    if _index_or_name in visited_kwargs:
                        raise ValueError(
                            'Specified arg was already handled by another `Arg` instance: {}'.format(_index_or_name))
                    # Store index
                    visited_args.add(_index_or_name)
                    # Validate arg
                    _arg_instance.validate(func_args[_index_or_name], name=_index_or_name)

            # Loop through args to validate
            for indices_or_names, arg in args:
                if isinstance(indices_or_names, tuple):  # Tuple of indices or names
                    for index_or_name in indices_or_names:
                        _validate_arg(index_or_name, arg)
                else:  # Single index or name
                    _validate_arg(indices_or_names, arg)

            # Check for special cases and handle them
            if args_special_case is not None:  # ARGS special case
                # Find remaining args
                remaining_args = set(range(num_func_args)) - visited_args
                # Validate remaining args
                for index_to_validate in remaining_args:
                    _validate_arg(index_to_validate, args_special_case)
            if kwargs_special_case is not None:  # KWARGS special case
                # Find remaining kwargs
                remaining_kwargs = set(func_kwargs) - visited_kwargs
                # Validate remaining kwargs
                for name_to_validate in remaining_kwargs:
                    _validate_arg(name_to_validate, kwargs_special_case)

            # Return function with specified args and kwargs
            return func(*func_args, **func_kwargs)

        # Return wrapper
        return func_wrapper

    # Return decorator
    return validation_decorator
