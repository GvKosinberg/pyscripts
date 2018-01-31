#!/usr/bin/py
# -*- coding: utf8 -*-
# Author: Antipin S.O. @RLDA

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

#%%

x = np.linspace(0, 20, 100)
plt.plot(x, np.cos(x))
plt.show()