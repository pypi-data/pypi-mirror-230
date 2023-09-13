# Copyright 2021 Google LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from unittest.mock import patch
from absl.testing import absltest
import math

import numpy as np
from numpy.testing import assert_array_equal
import pandas as pd

from temporian.core.operators.window.simple_moving_average import (
    SimpleMovingAverageOperator,
)
from temporian.implementation.numpy.operators.window.simple_moving_average import (
    SimpleMovingAverageNumpyImplementation,
    operators_cc,
)
from temporian.core.data import duration, node as node_lib
from temporian.io.pandas import from_pandas


def _f64(l):
    return np.array(l, np.float64)


def _f32(l):
    return np.array(l, np.float32)


nan = math.nan
cc_sma = operators_cc.simple_moving_average


class SimpleMovingAverageOperatorTest(absltest.TestCase):
    def test_cc_empty(self):
        a_f64 = _f64([])
        a_f32 = _f32([])
        assert_array_equal(cc_sma(a_f64, a_f32, 5.0), a_f32)
        assert_array_equal(cc_sma(a_f64, a_f64, 5.0), a_f64)
        assert_array_equal(
            cc_sma(a_f64, a_f32, a_f64, 5.0),
            a_f32,
        )
        assert_array_equal(
            cc_sma(a_f64, a_f64, a_f64, 5.0),
            a_f64,
        )

    def test_cc_wo_sampling(self):
        assert_array_equal(
            cc_sma(
                _f64([1, 2, 3, 5, 20]),
                _f32([10, 11, 12, 13, 14]),
                5.0,
            ),
            _f32([10.0, 10.5, 11.0, 11.5, 14.0]),
        )

    def test_cc_w_sampling(self):
        assert_array_equal(
            cc_sma(
                _f64([1, 2, 3, 5, 6]),
                _f32([10, 11, 12, 13, 14]),
                _f64([-1.0, 1.0, 1.1, 3.0, 3.5, 6.0, 10.0]),
                3.0,
            ),
            _f32([nan, 10.0, 10.0, 11.0, 11.0, 13.5, nan]),
        )

    def test_cc_w_nan_wo_sampling(self):
        assert_array_equal(
            cc_sma(
                _f64([1, 1.5, 2, 5, 20]),
                _f32([10, nan, nan, 13, 14]),
                1.0,
            ),
            _f32([10.0, 10.0, nan, 13.0, 14.0]),
        )

    def test_cc_w_nan_w_sampling(self):
        assert_array_equal(
            cc_sma(
                _f64([1, 2, 3, 5, 6]),
                _f32([nan, 11, nan, 13, 14]),
                _f64([1.0, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0]),
                1.0,
            ),
            _f32([nan, 11.0, 11.0, nan, nan, nan, 13.0, 14]),
        )

    def test_cc_wo_sampling_w_variable_winlen(self):
        assert_array_equal(
            cc_sma(
                evset_timestamps=_f64([0, 1, 2, 3, 5, 20]),
                evset_values=_f32([nan, 10, 11, 12, 13, 14]),
                window_length=_f64([1, 1, 1.5, 0.5, 3.5, 20]),
            ),
            _f32([nan, 10, 10.5, 12, 12, 12]),
        )

    def test_cc_w_sampling_w_variable_winlen(self):
        assert_array_equal(
            cc_sma(
                evset_timestamps=_f64([0, 1, 2, 3, 5, 20]),
                evset_values=_f64([nan, 10, 11, 12, 13, 14]),
                sampling_timestamps=_f64([-1, 1, 4, 19, 20, 20]),
                window_length=_f64([10, 0.5, 2.5, 19, 16, np.inf]),
            ),
            _f64([nan, 10, 11.5, 11.5, 13.5, 12]),
        )

    def test_cc_variable_winlen_repeated_ts(self):
        assert_array_equal(
            cc_sma(
                evset_timestamps=_f64([0, 1, 2, 3, 5, 20]),
                evset_values=_f64([nan, 10, 11, 12, 13, 14]),
                sampling_timestamps=_f64([20, 20, 20, 20, 20, 20]),
                window_length=_f64([16, 0.001, np.inf, 0, 1, 19]),
            ),
            _f64([13.5, 14, 12, nan, 14, 12.5]),
        )

    def test_cc_variable_winlen_shortest_duration(self):
        assert_array_equal(
            cc_sma(
                evset_timestamps=_f64([1.999999, 2]),
                evset_values=_f64([10, 11]),
                sampling_timestamps=_f64([2, 2, 2, 2]),
                window_length=_f64([1, 0.001, duration.shortest, 0]),
            ),
            _f64([10.5, 10.5, 11, nan]),
        )

    def test_cc_wo_sampling_w_variable_winlen_invalid_values(self):
        assert_array_equal(
            cc_sma(
                evset_timestamps=_f64([0, 1, 2, 3, 5, 6, 20]),
                evset_values=_f64([nan, 10, 11, 12, 13, 14, 15]),
                window_length=_f64([1, -20, 3, 0, 10, nan, 19]),
            ),
            _f64([nan, nan, 10.5, nan, 11.5, nan, 13]),
        )

    def test_cc_w_sampling_variable_winlen_invalid_values(self):
        assert_array_equal(
            cc_sma(
                evset_timestamps=_f64([0, 1, 2, 3, 5, 20]),
                evset_values=_f64([nan, 10, 11, 12, 13, 14]),
                sampling_timestamps=_f64([2, 2, 5, 5, 20, 20]),
                window_length=_f64([1, -10, 3, 0, nan, 19]),
            ),
            _f64([11, nan, 12.5, nan, nan, 12.5]),
        )

    def test_cc_wo_sampling_repeated_ts(self):
        assert_array_equal(
            cc_sma(
                evset_timestamps=_f64([0, 2, 2, 2, 2, 5]),
                evset_values=_f64([10, 11, 12, 13, 14, 15]),
                window_length=_f64([1, 3, 0.5, np.inf, -1, 5]),
            ),
            _f64([10, 12, 12.5, 12, nan, 13]),
        )

    def test_variable_winlen_duped_ts_same_winlength(self):
        assert_array_equal(
            cc_sma(
                evset_timestamps=_f64([2, 2, 2, 2]),
                evset_values=_f64([10, 11, 12, 13]),
                window_length=_f64([0, 1, 1, 2]),
            ),
            _f64([nan, 11.5, 11.5, 11.5]),
        )
        assert_array_equal(
            cc_sma(
                evset_timestamps=_f64([0, 1, 2, 3]),
                evset_values=_f64([10, 11, 12, 13]),
                sampling_timestamps=_f64([2, 2, 2, 2]),
                window_length=_f64([0, 1, 1, 2]),
            ),
            _f64([nan, 12, 12, 11.5]),
        )

    def test_variable_winlen_empty_arrays(self):
        assert_array_equal(
            cc_sma(
                evset_timestamps=_f64([1]),
                evset_values=_f64([10]),
                sampling_timestamps=_f64([]),
                window_length=_f64([]),
            ),
            _f64([]),
        )
        assert_array_equal(
            cc_sma(
                evset_timestamps=_f64([]),
                evset_values=_f64([]),
                window_length=_f64([]),
            ),
            _f64([]),
        )

    def test_flat(self):
        """A simple event set."""

        evset = from_pandas(
            pd.DataFrame(
                [
                    [10.0, 20.0, 1],
                    [11.0, 21.0, 2],
                    [12.0, 22.0, 3],
                    [13.0, 23.0, 5],
                    [14.0, 24.0, 20],
                ],
                columns=["a", "b", "timestamp"],
            )
        )

        op = SimpleMovingAverageOperator(
            input=evset.node(),
            window_length=5.0,
            sampling=None,
        )
        op.outputs["output"].check_same_sampling(evset.node())

        self.assertEqual(op.list_matching_io_samplings(), [("input", "output")])
        instance = SimpleMovingAverageNumpyImplementation(op)
        output = instance.call(input=evset)

        expected_output = from_pandas(
            pd.DataFrame(
                [
                    [10.0, 20.0, 1],
                    [10.5, 20.5, 2],
                    [11.0, 21.0, 3],
                    [11.5, 21.5, 5],
                    [14.0, 24.0, 20],
                ],
                columns=["a", "b", "timestamp"],
            )
        )

        self.assertEqual(repr(output), repr({"output": expected_output}))

    def test_with_index(self):
        """Indexed Event sets."""

        evset = from_pandas(
            pd.DataFrame(
                [
                    ["X1", "Y1", 10.0, 1],
                    ["X1", "Y1", 11.0, 2],
                    ["X1", "Y1", 12.0, 3],
                    ["X2", "Y1", 13.0, 1.1],
                    ["X2", "Y1", 14.0, 2.1],
                    ["X2", "Y1", 15.0, 3.1],
                    ["X2", "Y2", 16.0, 1.2],
                    ["X2", "Y2", 17.0, 2.2],
                    ["X2", "Y2", 18.0, 3.2],
                ],
                columns=["x", "y", "a", "timestamp"],
            ),
            indexes=["x", "y"],
        )

        op = SimpleMovingAverageOperator(
            input=evset.node(),
            window_length=5.0,
            sampling=None,
        )
        self.assertEqual(op.list_matching_io_samplings(), [("input", "output")])
        instance = SimpleMovingAverageNumpyImplementation(op)

        output = instance.call(input=evset)
        expected_output = from_pandas(
            pd.DataFrame(
                [
                    ["X1", "Y1", 10.0, 1],
                    ["X1", "Y1", 10.5, 2],
                    ["X1", "Y1", 11.0, 3],
                    ["X2", "Y1", 13.0, 1.1],
                    ["X2", "Y1", 13.5, 2.1],
                    ["X2", "Y1", 14.0, 3.1],
                    ["X2", "Y2", 16.0, 1.2],
                    ["X2", "Y2", 16.5, 2.2],
                    ["X2", "Y2", 17.0, 3.2],
                ],
                columns=["x", "y", "a", "timestamp"],
            ),
            indexes=["x", "y"],
        )

        self.assertEqual(output["output"], expected_output)

    def test_with_sampling(self):
        """Event sets with user provided sampling."""

        evset = from_pandas(
            pd.DataFrame(
                [[10.0, 1], [11.0, 2], [12.0, 3], [13.0, 5], [14.0, 6]],
                columns=["a", "timestamp"],
            )
        )

        sampling_node = node_lib.input_node([])
        op = SimpleMovingAverageOperator(
            input=evset.node(),
            window_length=3.0,
            sampling=sampling_node,
        )
        op.outputs["output"].check_same_sampling(sampling_node)

        self.assertEqual(
            op.list_matching_io_samplings(), [("sampling", "output")]
        )
        instance = SimpleMovingAverageNumpyImplementation(op)

        sampling_data = from_pandas(
            pd.DataFrame(
                [[-1.0], [1.0], [1.1], [3.0], [3.5], [6.0], [10.0]],
                columns=["timestamp"],
            )
        )

        output = instance.call(input=evset, sampling=sampling_data)
        expected_output = from_pandas(
            pd.DataFrame(
                [
                    [nan, -1.0],
                    [10.0, 1.0],
                    [10.0, 1.1],
                    [11.0, 3.0],
                    [11.0, 3.5],
                    [13.5, 6.0],
                    [nan, 10.0],
                ],
                columns=["a", "timestamp"],
            )
        )

        self.assertEqual(output["output"], expected_output)

    def test_with_nan(self):
        """The input features contains nan values."""

        evset = from_pandas(
            pd.DataFrame(
                [[nan, 1], [11.0, 2], [nan, 3], [13.0, 5], [14.0, 6]],
                columns=["a", "timestamp"],
            )
        )

        op = SimpleMovingAverageOperator(
            input=evset.node(),
            window_length=1.0,
            sampling=node_lib.input_node([]),
        )
        instance = SimpleMovingAverageNumpyImplementation(op)

        sampling_data = from_pandas(
            pd.DataFrame(
                [[1], [2], [2.5], [3], [3.5], [4], [5], [6]],
                columns=["timestamp"],
            )
        )

        output = instance.call(input=evset, sampling=sampling_data)
        expected_output = from_pandas(
            pd.DataFrame(
                [
                    [nan, 1],
                    [11.0, 2],
                    [11.0, 2.5],
                    [nan, 3],
                    [nan, 3.5],
                    [nan, 4],
                    [13.0, 5],
                    [14.0, 6],
                ],
                columns=["a", "timestamp"],
            )
        )

        self.assertEqual(output["output"], expected_output)

    # TODO: move to a separate file that tests the base class
    @patch("temporian.implementation.numpy.operators.window.base.logging")
    def test_invalid_window_length_warning(self, logging_mock):
        """Tests that warning is shown when receiving non strictly positive
        values in window_length."""
        evset = from_pandas(
            pd.DataFrame([[0, 1]], columns=["a", "timestamp"], dtype=np.float64)
        )
        window_length = from_pandas(
            pd.DataFrame(
                [[1, 1], [2, -1]], columns=["timestamp", "b"], dtype=np.float64
            ),
        )

        op = SimpleMovingAverageOperator(
            input=evset.node(),
            window_length=window_length.node(),
        )
        instance = SimpleMovingAverageNumpyImplementation(op)

        instance.call(input=evset, window_length=window_length)
        logging_mock.warning.assert_called_with(
            "`window_length`'s values should be strictly positive. 0, NaN and"
            " negative window lengths will output missing values."
        )

    # TODO: move to a separate file that tests the base class
    def test_variable_window_length_invalid(self):
        evset = from_pandas(pd.DataFrame([[0, 1]], columns=["a", "timestamp"]))

        window_length = from_pandas(
            pd.DataFrame([[1], [2]], columns=["timestamp"])
        )
        with self.assertRaisesRegex(
            ValueError, "`window_length` must have exactly one float64 feature"
        ):
            SimpleMovingAverageOperator(
                input=evset.node(),
                window_length=window_length.node(),
            )

        window_length = from_pandas(
            pd.DataFrame(
                [[1, 1, 1], [2, 2, 2]], columns=["timestamp", "b", "c"]
            ),
        )
        with self.assertRaisesRegex(
            ValueError, "`window_length` must have exactly one float64 feature"
        ):
            SimpleMovingAverageOperator(
                input=evset.node(),
                window_length=window_length.node(),
            )

        window_length = from_pandas(
            pd.DataFrame(
                [[1, 1, 1], [2, 2, 2]],
                columns=["timestamp", "b", "c"],
                dtype=np.float32,
            ),
        )
        with self.assertRaisesRegex(
            ValueError, "`window_length` must have exactly one float64 feature"
        ):
            SimpleMovingAverageOperator(
                input=evset.node(),
                window_length=window_length.node(),
            )


if __name__ == "__main__":
    absltest.main()
