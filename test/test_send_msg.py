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
