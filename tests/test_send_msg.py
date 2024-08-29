"""
        gg-transfer - a tool to transfer files encoded in audio via FSK modulation
        Copyright (C) 2024 Matteo Tenca

        This program is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import unittest
import ggtransfer


class MyTestCase(unittest.TestCase):

    @unittest.skip("skipping test_send...")
    def test_send(self) -> None:
        s = ggtransfer.Sender(protocol=2)
        s.send("1234567890" * 15)
        # s.send()
        self.assertEqual(True, True)  # add assertion here

    @unittest.skip("skipping test_wrong_args...")
    def test_wrong_args(self) -> None:
        # noinspection PyTypeChecker
        s = ggtransfer.Sender(args="ciao", protocol=2)
        s.send("Ciao!" * 40)
        self.assertEqual(True, True)  # add assertion here

    @unittest.skip("skipping test_receive...")
    def test_receive(self) -> None:
        r = ggtransfer.Receiver(file_transfer=False)
        rr = r.receive()
        self.assertIsInstance(rr, str)
        print("-" * 30)
        print(rr)
        print("-" * 30)


if __name__ == '__main__':
    unittest.main(defaultTest="MyTestCase")
