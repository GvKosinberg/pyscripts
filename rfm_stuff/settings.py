#!/usr/bin/python
# -*- coding: utf8 -*-
# Author: Antipin S.O. @RLDA

air_stngs = {
    "snc_type": "SNC_T_AIR",
    "topic": "oh/sncs/temp/air/",
    "limits": [19.00, 25.00],
}

water_stngs = {
    "snc_type": "SNC_T_WATER",
    "topic": "oh/sncs/temp/water/",
    "limits": [5.00, 22.00],
}

heater_stngs = {
    "snc_type": "SNC_T_HEATER",
    "topic": "oh/sncs/temp/heater/",
    "limits": [50.00, 100.00],
}

lumi_stngs = {
    "snc_type": "SNC_LUMI",
    "topic": "oh/sncs/lumi/",
    "limits": [150.00, 300.00],
}


class sencor_settings(object):
    def __init__(self):

##############################################
