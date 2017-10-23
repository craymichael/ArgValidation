# ArgValidation
A small library for a `req` function that wraps any function generically for the purpose of argument checking. It's flexible
in that you can specify your own checking functions and error messages in addition to the variety of common cases provided.
This is foreseeably useful for APIs. 

    Basic req Examples:
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
