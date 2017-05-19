from unittest import TestCase
from unittest import main

from sentinel import SentinelAddress


class TestSentinelAddress(TestCase):
    def test_constructor(self):
        latitude = 55.752486
        longitude = 37.623199

        s = SentinelAddress(latitude, longitude)

        pass

    def test_retrieveDirectories(self):
        latitude = 55.752486
        longitude = 37.623199

        s = SentinelAddress(latitude, longitude)
        dirs = s.retrieveDirectories()

        pass



if __name__ == '__main__':
    main()


