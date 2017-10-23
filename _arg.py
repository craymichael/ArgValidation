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
import abc
import re


class _Arg(object):
    """Abstract base class. Structure is what is expected from `req`."""
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def validate(self, arg, name=None, index=None):
        """Validates the provided `arg`.

        Args:
            arg: The argument value to validate
            name: The name of a kwarg
            index: The index of an arg

        Raises:
            Appropriate errors.
        """
        raise NotImplementedError


class Arg(_Arg):  # TODO(Docs) include blurb about extending this class
    """Validation argument container."""

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
                recommended as they have an efficient `__contains__` method (hashing).
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
                See `validate` for information of possible `err_msg` keys and associated exceptions.
        """
        # Store validation parameters
        self._types = types
        self._choices = choices
        self._length = length
        self._regex = regex
        self._func = func
        self._err_msg = err_msg
        # Whether err_msg is a dict. Computed now to save time during validation.
        self._err_msg_is_dict = isinstance(self._err_msg, dict)

    def validate(self, arg, name=None, index=None):
        """Validates an argument using specified params to `__init__`.

        Args:
            arg: The argument value to validate
            name: The name of a kwarg
            index: The index of an arg

        Raises:
            TypeError:
                'types': Arg wasn't an instance of any `types` if specified.
            ValueError:
                'choices': Arg wasn't in `choices` if specified.
                'length': Arg wasn't an allowed `length` if specified.
                'regex': Arg didn't match regex if specified.
                'func': `func` returned False when arg passed to it if `func` specified.
            AttributeError:
                'no_length': Arg doesn't have `__len__` attribute if `length` specified.
        """
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
                    self._get_err_msg('no_length') or
                    'Specified {} is required to have a length (`__len__` attribute).'.format(arg_format))

            # Calculate arg length
            arg_length = len(arg)

            def _raise_bad_length():
                """Raises ValueError for bad length."""
                raise ValueError(self._get_err_msg('length') or
                                 'Specified {} with length {} is required to have length of {}.'.format(arg_format,
                                                                                                        arg_length,
                                                                                                        self._length))

            if isinstance(self._length, tuple):
                # Check multiple lengths
                if arg_length not in self._length:
                    _raise_bad_length()
            else:
                # Check single length
                if arg_length != self._length:
                    _raise_bad_length()

        if self._regex is not None:
            # Match regex
            if re.match(self._regex, arg) is None:
                raise ValueError(self._get_err_msg('regex') or
                                 'Specified {} did not match the following regex: {}'.format(arg_format, self._regex))

        if self._func is not None:
            def _eval_func(_func):
                """Evaluates a callable function. Raises ValueError is function returns False."""
                func_output = _func(arg)
                if func_output is False:
                    raise ValueError(self._get_err_msg('func') or
                                     'Specified {} did not meet requirements of function {}.'.format(arg_format, _func))

            if isinstance(self._func, tuple):
                # Evaluate multiple functions
                for func in self._func:
                    _eval_func(func)
            else:
                # Evaluate single function
                _eval_func(self._func)

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
