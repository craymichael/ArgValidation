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
import six  # TODO(Docs and Pip?) Required package
import re
from functools import wraps

# Special case constants
ARGS
KWARGS


class Arg(object):  # TODO(Docs) include blurb about extending this class
    """"""

    def __init__(self,
                 types=None,
                 choices=None,  # TODO(Docs) note about including kwarg default value
                 length=None,
                 regex=None,  # TODO(Docs) warn to use raw strings? is that a thing? r'test\\' => 'test\\\\'
                 func=None,  # TODO(Docs) warn about mutation
                 err_msg=None):  # TODO(Docs) warn about case, ask for suggestions
        """Stores validation parameters.

        Args:
            types: The type or tuple of types to expect. `None` results in no type checking.
            choices: Allowed values. Must have `__contains__` method implemented, e.g. `set` or `tuple`. Python `set` is
                recommended as they have an efficient __contains__ method (hashing).
            length: The length or tuple of lengths to expect to expect. `None` results in no length checking.
            regex: A regex pattern to validate the input with. A ValueError is raised if no match is found `None`
                results in no regex matching.
            func: A callable function or tuple of callable functions that takes in one parameter (the function input).
                This function is expected to either raise its own exception, or return True if the input is valid and
                False otherwise. Specifying `None` results in no validation by function(s).
            err_msg: An optional string error message to print when an error is raised. `None` results in a default
                error. Alternatively, a dictionary can be provided with a param as the key and message as the
                value. Example:
                    err_msg={
                        'types': 'The specified type was not expected.'
                        'length': 'The provided length was not long enough.'
                    }
        """
        # Store validation parameters
        self._types = types
        self._choices = choices
        self._length = length
        self._regex = regex
        self._func = func
        self._err_msg = err_msg
        # Whether err_msg is a dict. Calculated now to save time during validation.
        self._err_msg_is_dict = isinstance(self._err_msg, dict)

    def validate(self, arg, name=None, index=None):
        """"""
        arg_format = 'kwarg `{}`'.format(name) if name else 'arg at index {}'.format(index)
        # Validate arg type
        if self._types is not None:
            if not isinstance(arg, self._types):
                raise TypeError(self._get_err_msg('types') or
                                'Specified {} is not an instance of the type(s): {}.'.format(arg_format, self._types))
        # Validate arg choices
        if self._choices is not None:
            if arg not in self._choices:
                raise ValueError(self._get_err_msg('choices') or
                                 'Specified {} is not a valid choice. Choices: {}'.format(arg_format, self._choices))

        # Validate arg length
        if self._length is not None:
            # Ensure arg has `__len__` attribute
            if not hasattr(arg, '__len__'):
                raise AttributeError(
                    self._get_err_msg('length') or
                    'Specified {} is required to have a length (`__len__` attribute).'.format(arg_format))

            def check_length(_length):
                """Validates length of arg with specified `_length`."""
                if len(arg) != _length:
                    raise ValueError(self._get_err_msg('length') or  # TODO WHY ARE THESE "SELF"S NOT FUCKING PURPLE
                                     'Specified {} is required to have length of {}.'.format(arg_format, self._length))

            if isinstance(self._length, tuple):
                # Check multiple lengths
                for length in self._length:
                    check_length(length)
            else:
                # Check single length
                check_length(self._length)

        if self._regex is not None:
            # Match regex
            if re.match(self._regex, arg) is None:
                raise ValueError(self._get_err_msg('regex') or
                                 'Specified {} did not match the following regex: {}'.format(arg_format, self._regex))

        if self._func is not None:
            def eval_func(_func):
                """Evaluates a callable function. Raises ValueError is function returns False."""
                func_output = _func(arg)
                if func_output is False:
                    raise ValueError(self._get_err_msg('func') or
                                     'Specified {} did not meet requirements of function {}.'.format(arg_format, _func))

            if isinstance(self._func, tuple):
                # Evaluate multiple functions
                for func in self._func:
                    eval_func(func)
            else:
                # Evaluate single function
                eval_func(self._func)

    def _get_err_msg(self, err_name):
        """Returns the error message specified if exists. If `self._err_msg` is a dict, the error message
        corresponding to `err_name` will be used (if `err_name` specified in dict). Otherwise, either a specified
        string error messages for all errors or None is returned.

        Args:
            err_name: Error message key

        Returns:
            String error message or None
        """
        if self._err_msg_is_dict:
            return self._err_msg.get(err_name)
        else:
            return self._err_msg


def req(*args):
    """
    @req(
        (3, Arg()),  # Single index
        ((1, 2), Arg()),  # Multiple indices
        (ARGS, Arg()),  # Rest of *args (ARGS special case)
        ((4, 'slug'), Arg()),  # Mix kwargs and args. Also, order of arg input doesn't matter
        ('test', Arg()),  # Single name
        (('spec', 'num_trees'), Arg()),  # Multiple names
        (KWARGS, Arg())  # Rest of **kwargs (KWARGS special case)
    )

    Args:
        *args:

    Returns:

    """

    def validate_decorator(func):
        """"""

        @wraps(func)
        def func_wrapper(*func_args, **func_kwargs):
            """"""
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

            def _validate_arg(_index_or_name, arg_instance):
                """"""
                # Define var scope
                global args_special_case, kwargs_special_case
                # Check ARGS/KWARGS special cases
                if _index_or_name is ARGS:
                    if args_special_case is not None:
                        raise ValueError('`ARGS` specified multiple times in input.')
                    args_special_case = arg_instance
                    # Break function; ARGS handled at end
                    return
                elif _index_or_name is KWARGS:
                    if kwargs_special_case is not None:
                        raise ValueError('`KWARGS` specified multiple times in input.')
                    kwargs_special_case = arg_instance
                    # Break function; KWARGS handled at end
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
                    arg_instance.validate(func_args[_index_or_name], index=_index_or_name)
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
                    arg_instance.validate(func_kwargs[_index_or_name], name=_index_or_name)

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
            return func_wrapper
        return validate_decorator
