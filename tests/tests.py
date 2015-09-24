#!/usr/bin/env python3

# author : renpeng
# github : https://github.com/laodifang
# description : MediaInfo test
# date : 2015-09-24

import unittest
from MediaInfo import MediaInfo

class TestSimple(unittest.TestCase):
    def test_nonFileNameParameter(self):
        info     = MediaInfo()
        infoData = info.getInfo()

        self.assertEqual(infoData, None)

    def test_haveCmdParameter(self):
        info     = MediaInfo(filename = '/media/test.ts', cmd = '/usr/bin/ffprobe')
        infoData = info.getInfo()

        self.assertNotEqual(infoData, None)

    def test_haveDefaultCmdFfprobe(self):
        info     = MediaInfo(filename = '/media/test.ts')
        infoData = info.getInfo()

        self.assertNotEqual(infoData, None)

