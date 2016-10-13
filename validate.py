import six  # Required
import re
from functools import wraps


def validate(arg, types=None, choices=None, regex=None, name=None):
    """"""
    # Handle regex specification
    if regex is not None:
        # Ensure args are string if regex
        if types is None:
            # Set types to base string types
            types = six.string_types
        else:
            # Check specified types
            for req_type in types:
                if req_type not in six.string_types:
                    raise TypeError('Regex specified but non-string type specified in `types`: {}.'.format(req_type))
        # Ensure arg matches specified regex
        if not re.match(regex, arg):
            raise ValueError('Arg \'{}\' did not match the regex: {}'.format(arg, regex))
    # Validate types
    if types is not None and not isinstance(arg, types):
        raise TypeError('Specified arg, \'{}\', was not a valid type. Allowed: {}'.format(arg, types))
    # Validate choices
    if choices is not None and arg not in choices:
        raise ValueError('Specified arg, \'{}\', was not in allowed choices: {}'.format(arg, choices))


class _BaseArg(object):
    """"""

    def __init__(self,
                 type=None,
                 choices=None,
                 length=None,
                 regex=None,
                 func=None,
                 err_msg=None):
        """

        Args:
            type: The type or tuple of types to expect. `None` results in no type checking.
            choices: Iterable of allowed values.
            length: The length or tuple of lengths to expect to expect. `None` results in no length checking.
            regex: A regex pattern to validate the input with. A ValueError is raised if no match is found `None` results in no regex matching.
            func: A callable function or tuple of callable functions that takes in one parameter (the function input).
                This function is expected to return True if the input is valid and False otherwise. `None` results in
                no validation by function.
            err_msg: An optional string error message to print when an error is raised. `None` results in a default
                error. Alternatively, a dictionary can be provided with a param as the key and message as the
                value. Example:
                    err_msg={
                        'type': 'The specified type was not expected.'
                        'length': 'The provided length was not long enough.'
                    }

        """
        self
        # TODO Ensure input has __len__ attribute when validating
        # TODO Ensure input is string for regex


class Arg(_BaseArg):
    """"""

    def __init__(self,
                 *args,
                 index=None,
                 **kwargs):
        """

        Args:
            index: Index or tuple of indices of args to check.
        """
        self._index = index
        super(Arg, self).__init__(*args, **kwargs)


class Kwarg(_BaseArg):
    """"""

    def __init__(self,
                 name,
                 *args,
                 **kwargs):
        """

        Args:
            name: Name or tuple of names
        """
        self._name = name
        super(Kwarg, self).__init__(*args, **kwargs)


def req(*args, **kwargs):
    """
    @req(
        Arg(),
        Arg(),
        Kwarg()
    )

    Args:
        *args:
        **kwargs:

    Returns:

    """

    def validate_decorator(func):
        """"""

        @wraps(func)
        def func_wrapper(*func_args, **func_kwargs):
            """"""
            # Validate arguments
            for arg_value in args:
                validate(arg_value, **kwargs)  # TODO kwargs is a lie
            # Validate kwargs
            for kwarg_name, kwarg_params in six.iteritems(kwargs):
                kwarg_value = func_kwargs[kwarg_name]
                validate(, ** )
                return func_wrapper

            return validate_decorator
