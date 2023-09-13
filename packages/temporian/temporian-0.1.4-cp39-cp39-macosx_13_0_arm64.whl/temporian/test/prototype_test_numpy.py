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
import pandas as pd
from absl.testing import absltest
import temporian as tp


class PrototypeTest(absltest.TestCase):
    def setUp(self) -> None:
        # store ids
        TRYOLABS_SHOP = 42
        GOOGLE_SHOP = 101
        # product ids
        MATE_ID = 1
        BOOK_ID = 2
        PIXEL_ID = 3

        self.evset_1 = tp.from_pandas(
            pd.DataFrame(
                data=[
                    [TRYOLABS_SHOP, MATE_ID, 0.0, 14],
                    [TRYOLABS_SHOP, MATE_ID, 1.0, 15],
                    [TRYOLABS_SHOP, MATE_ID, 2.0, 16],
                    [TRYOLABS_SHOP, BOOK_ID, 1.0, 10],
                    [GOOGLE_SHOP, BOOK_ID, 1.0, 7],
                    [GOOGLE_SHOP, BOOK_ID, 2.0, 8],
                    [GOOGLE_SHOP, PIXEL_ID, 0.0, 3],
                    [GOOGLE_SHOP, PIXEL_ID, 1.0, 4],
                ],
                columns=["store_id", "product_id", "timestamp", "sales"],
            ),
            indexes=["store_id", "product_id"],
        )

        self.evset_2 = tp.from_pandas(
            pd.DataFrame(
                data=[
                    [TRYOLABS_SHOP, MATE_ID, 0.0, -14],
                    [TRYOLABS_SHOP, MATE_ID, 1.0, -15],
                    [TRYOLABS_SHOP, MATE_ID, 2.0, -16],
                    [TRYOLABS_SHOP, BOOK_ID, 1.0, -10],
                    [GOOGLE_SHOP, BOOK_ID, 1.0, -7],
                    [GOOGLE_SHOP, BOOK_ID, 2.0, -8],
                    [GOOGLE_SHOP, PIXEL_ID, 0.0, -3],
                    [GOOGLE_SHOP, PIXEL_ID, 1.0, -4],
                ],
                columns=["store_id", "product_id", "timestamp", "costs"],
            ),
            indexes=["store_id", "product_id"],
            same_sampling_as=self.evset_1,
        )

        # TODO: Remove the following line when "from_pandas" support creating
        # event set with shared sampling. Note that "evset_1" and
        # "evset_2" should have the same sampling in this tests.

        self.node_1 = self.evset_1.node()
        self.node_2 = self.evset_2.node()

        self.expected_evset = tp.from_pandas(
            pd.DataFrame(
                data=[
                    [TRYOLABS_SHOP, MATE_ID, 0.0, 14, -14, 0, -14],
                    [TRYOLABS_SHOP, MATE_ID, 1.0, 15, -15, 14, -15],
                    [TRYOLABS_SHOP, MATE_ID, 2.0, 16, -16, 15, -16],
                    [TRYOLABS_SHOP, BOOK_ID, 1.0, 10, -10, 0, -10],
                    [GOOGLE_SHOP, BOOK_ID, 1.0, 7, -7, 0, -7],
                    [GOOGLE_SHOP, BOOK_ID, 2.0, 8, -8, 7, -8],
                    [GOOGLE_SHOP, PIXEL_ID, 0.0, 3, -3, 0, -3],
                    [GOOGLE_SHOP, PIXEL_ID, 1.0, 4, -4, 3, -4],
                ],
                columns=[
                    "store_id",
                    "product_id",
                    "timestamp",
                    "sales",
                    "costs",
                    "lag[1s]_sales",
                    "negated_sales",
                ],
            ),
            indexes=["store_id", "product_id"],
        )

    def test_prototype(self) -> None:
        a = tp.glue(self.node_1, self.node_2)
        # create and glue sum feature
        # TODO: Restore when arithmetic operator is fixed.
        # b = tp.glue(a, self.node_1 + self.node_2)
        c = self.node_1.lag(duration=1).prefix("lag[1s]_")
        d = tp.glue(a, c.resample(a))
        sub_sales = (-self.node_1["sales"]).prefix("negated_")
        e = tp.glue(d, sub_sales)
        output_node = e

        output_evset = tp.run(
            output_node,
            input={
                self.node_1: self.evset_1,
                self.node_2: self.evset_2,
            },
            check_execution=True,
            verbose=2,
        )
        self.assertEqual(self.expected_evset, output_evset)


if __name__ == "__main__":
    absltest.main()
