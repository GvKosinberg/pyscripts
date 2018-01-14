#!/usr/bin/python
# -*- coding: utf8 -*-
#Author: Antipin S.O. @RLDA

"""
    Подключение необходимых модулей
"""
import os, sys

#TODO: uncomment 4 realz
#import rfm69
#import paho.mqtt.publish as mqpb

import time

#DEBUG: dev_stuff
import random

"""
    Подключение консольного логера
"""
import logging
logging.basicConfig(level=logging.DEBUG)

"""
	Инициализация RFM69
	На выходе объект класса rfm69
"""
def init_rfm():
    #TEMP: faek rfm unit
    rfm_unit = "sum_sh1et"
    ##_____##
	# myconf = rfm69.RFM69Configuration()
	# rfm_unit = rfm69.RFM69(dio0_pin=24, reset_pin=22, spi_channel = 0, config = myconf)
	# #setting RSSI treshold
	# rfm_unit.set_rssi_threshold(-114)
    return rfm_unit

"""
    Класс управляемых устройств и сенсоров
"""
class Device:
    def __init__(self, d_type, name, rfm, d_timeout):
        #Тип устройства (датчик/исполнитель) (str)
        __types = [#-------------------------------------------#
                    "SNC_T_AIR", "SNC_T_WAT", "SNC_T_HTR", "SNC_LUM", "SNC_HUM",
                    "SNC_DOOR",  "SNC_WARN_LEAK", "SNC_WARN_FLAME",
                    "SNC_WARN_SMOKE", "SNC_PRES_PRES", "SNC_PRES_MOT", "FAKE",
                    #------------------------------------------#
                    "CNTR",
                    #------------------------------------------#
                    "CNTRL_RELAY", "CNRL_DIM"]

        try:
            if (__types.index(d_type) != None):
                self.d_type = d_type
        except Exception as e:
            print("Invalid device type")
        #Идентификатор группы устройств (str)
        # self.id = id_grp
        #Имя (str)
        self.name = name
        #Экземпляр класса rfm69 (rfm69)
        self.rfm = rfm
        #Данные
        self.data = "-"
        #Время последнего полученного ответа
        self.last_responce = time.time()
        #Таймаут получения ответа (в секундах)
        self.d_timeout = d_timeout
        #TODO: Dobavit' identificator v list proverki rfm'a
        #Счетчик ошибок
        self.error_cnt = 0

    #TEMP: place for rand fux
    def sumfunc(self):
        pass

    """
        Метод проверки timeout'а ответа
    """
    def check_timeout(self):
        razn = time.time() - self.last_responce
        if razn > self.d_timeout:
            self.data = "-"
        print(razn)

    """
        Метод записи полученного значения датчика в брокер
    """
    def write2mqtt(self):
        #mqtt_topic = "oh" + self.d_type + self.name
        self.data = self.get_random_state()
        mqtt_val = self.data
        #mqtt_val = self.data
        #pbl.single(mqtt_topic, mqtt_val, hostname="localhost", port=1883)
        print('Obj: %s ' %(self.d_type +"/"+ self.name))
        #print('Last responce: %s' %str(self.last_responce))

        print(mqtt_val)

    """
        Метод отправки значения на исполнительное устройство
    """
    def write2control(self):
        pass

    #TEMP: random generator for tests
    def get_random_state(self):
        __val_limits = {"SNC_T_AIR": [19.00, 25.00],
                        "SNC_T_WAT": [5.00, 22.00],
                        "SNC_T_HTR": [50.00, 100.00],
                        "SNC_LUM": [150.00, 300.00],
                        "SNC_HUM": [0, 100],
                        "FAKE": [0, 3378]
                    }
        __defas = {"SNC_DOOR": ["OPEN", "CLOSED"],
                 "SNC_PRES_MOT": ["ON", "OFF"],
                 "SNC_PRES_PRES": ["ON", "OFF"],
                 "SNC_WARN_LEAK": ["HIGH", "LOW"],
                 "SNC_WARN_FLAME": ["HIGH", "LOW"],
                 "SNC_WARN_SMOKE": ["HIGH", "LOW"]}
        if __defas.get(self.d_type) != None:
            state = random.randint(0,1)
            out = __defas[self.d_type][state]
        else:
            out = random.uniform(__val_limits[self.d_type][0],
                                __val_limits[self.d_type][1])
        self.last_responce = time.time()
        return out

#DEBUG: just 4 tests
if __name__ == "__main__":
    rfm = init_rfm()
    try:
        fake_snc_1 = Device("SNC_T_AIR", "1", rfm)
        fake_snc_2 = Device("FAKE", "2", rfm)
        fake_snc_3 = Device("SNC_PRES_PRES", "1", rfm)
    except Exception as e:
        print("Init fux")
        raise(e)

    try:
        while(True):
            fake_snc_1.write2mqtt()
            fake_snc_2.write2mqtt()
            fake_snc_3.write2mqtt()
            time.sleep(5)
            fake_snc_3.check_timeout()
    except KeyboardInterrupt:
        print("That's all, folks")
