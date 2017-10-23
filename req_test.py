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
import unittest
from _req import req, ARGS, KWARGS
from _arg import Arg


# `req` decorator test syntax:
# req(*args_to_req)(func)(*args_to_func, **kwargs_to_func)
def req_as_decorator(req_output, *args, **kwargs):
    """Runs req as decorator for a dummy function."""
    return req_output(dummy_func)(*args, **kwargs)


def dummy_func(*args, **kwargs):
    """Dummy function that takes m args and n kwargs."""
    pass


class TestIndices(unittest.TestCase):
    def test_single_index(self):
        req_as_decorator(
            req(
                (1, Arg(length=2))  # Validate index 1 length
            ), 0, ['A', 'B']
        )
        with self.assertRaises(ValueError):
            req_as_decorator(
                req(
                    (1, Arg(length=2))  # Validate index 1 length
                ), 0, ['A', 'B', 'C']
            )

    def test_indices(self):
        req_as_decorator(
            req(
                ((0, 1), Arg(types=(int, float,)))  # Validate types for indices
            ), 0, 1.1
        )
        with self.assertRaises(ValueError):
            req_as_decorator(
                req(
                    (1, Arg(length=2))  # Validate types for indices
                ), 2.2, 'A'
            )


class TestNames(unittest.TestCase):
    def test_single_name(self):
        req_as_decorator(
            req(
                ('pid', Arg(types=int))  # Validate kwarg pid type
            ), 123, pid=1, two=2
        )
        with self.assertRaises(TypeError):
            req_as_decorator(
                req(
                    ('pid', Arg(types=int))  # Validate kwarg pid type
                ), pid=1.1
            )

    def test_names(self):
        req_as_decorator(
            req(
                (('first', 'second'), Arg(regex=r'[a-z]+'))  # Validate regex for kwargs
            ), first='first', second='second'
        )
        with self.assertRaises(ValueError):
            req_as_decorator(
                req(
                    (('first', 'second'), Arg(regex=r'[a-z]+'))  # Validate regex for kwargs
                ), first='first', second='SECOND'
            )


"""class TestSpecial(unittest.TestCase):
    def test_args_special_case(self):

    def test_kwargs_special_case(self):


class TestMixed(unittest.TestCase):
    def test_mixed_args_special_case(self):

    def test_mixed_kwargs_special_case(self):"""

if __name__ == '__main__':
    unittest.main()
