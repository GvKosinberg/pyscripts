#!/usr/bin/python
# -*- coding: utf8 -*-
# Author: Antipin S.O. @RLDA

import unittest
import tested_fns as tf

class rf_sh_Test(unittest.TestCase):
    def test_normal_t(self):
        inc = ([0, 1, 0, 74, 163, 50, 13], "sumfux")
        msg = "337.8 °C"
        self.assertEqual(tf.read_real(inc), msg)

    def test_normal_l(self):
        inc = ([0, 9, 3, 74, 163, 50, 13], "sumfux")
        msg = "3378 люкс"
        self.assertEqual(tf.read_real(inc), msg)

    def test_err_t(self):
        inc = ([0, 1, 0, 74, 163, 0xFF, 0x7], "sumfux")
        msg = "Ошибка датчика"
        self.assertEqual(tf.read_real(inc), msg)

    def test_err_l(self):
        inc = ([0, 9, 3, 74, 163, 0xFF, 0xFF], "sumfux")
        msg = "Ошибка датчика"
        self.assertEqual(tf.read_real(inc), msg)

'''
    jjj
'''
if __name__ == '__main__':
    unittest.main()
