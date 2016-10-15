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


class Arg(object):
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
            regex: A regex pattern to validate the input with. A ValueError is raised if no match is found `None`
                results in no regex matching.
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


def req(*args):
    """
    @req(
        (3, Arg()),
        ((1, 2), Arg()),
        (ARGS, Arg()),  # Rest of *args
        ('test', Arg()),
        (('spec', 'num_trees'), Arg()),
        (KWARGS, Arg())  # Rest of **kwargs, must be last kwarg specified to req
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
                # Establish var scope
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
                            'Specified kwarg was already handled by another `Arg` instance: {}'.format(index_or_name))
                    # Store name
                    visited_kwargs.add(_index_or_name)
                    # Validate kwarg
                    arg_instance.validate(func_args[index_or_name])
                else:  # Assume `index_or_name` is int index (arg)
                    # Store index as positive/actual value
                    if _index_or_name < 0:
                        _index_or_name += num_func_args
                    # Ensure index hasn't been handled
                    if _index_or_name in visited_kwargs:
                        raise ValueError(
                            'Specified arg was already handled by another `Arg` instance: {}'.format(index_or_name))
                    # Store index
                    visited_args.add(index_or_name)
                    # Validate arg
                    arg_instance.validate(func_kwargs[index_or_name])

            # Loop through args to validate
            for indices_or_names, arg in args:
                # TODO validate (bass class method?)
                if isinstance(indices_or_names, tuple):
                    for index_or_name in indices_or_names:
                        _validate_arg(index_or_name, arg)
                else:
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

            return validate_decorator
