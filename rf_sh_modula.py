#!/usr/bin/python
# -*- coding: utf8 -*-
#Author: Antipin S.O. @RLDA

"""
    Подключение необходимых модулей
"""
import os, sys
import rfm69
import time
import paho.mqtt.publish as mqpb

#DEBUG: dev_stuff
import random

"""
    Подключение консольного логера
"""
import logging
logging.basicConfig(level=logging.DEBUG)

"""
	Инициализация логгера, RFM69
	На выходе объект класса rfm69
"""
def init_rfm():
	myconf = rfm69.RFM69Configuration()
	rfm_unit = rfm69.RFM69(dio0_pin=24, reset_pin=22, spi_channel = 0, config = myconf)
	#setting RSSI treshold
	rfm_unit.set_rssi_threshold(-114)
	return rfm_unit


"""
    Класс управляемых устройств и сенсоров
"""
class Device:
    def __init__(self, d_type, id_grp, name, data=0, rfm):
        #Тип устройства (датчик/исполнитель) (str)
        self.d_type = d_type
        #Идентификатор группы устройств (str)
        self.id = id_grp
        #Имя (str)
        self.name = name
        #TODO: zasun' suda parametri, debil
        self.data = data
        #Экземпляр класса rfm69 (rfm69)
        self.rfm = rfm
        #Время последнего полученного ответа
        self.last_responce = time.clock()
        #TODO: Dobavit' identificator v list proverki rfm'a

    #TEMP: place for rand fux
    def sumfunc(self):
        pass

    """
        Метод записи полученного значения датчика в брокер
    """
    def write2mqtt(self):
        topic = self.id_grp + self.name
        val = str(data)
        pass

    """
        Метод отправки значения на исполнительное устройство
    """
    def write2control(self):
        pass

#TEMP: random generator for tests
def get_rand():
    pass

#DEBUG: just 4 tests
if __name__ == "__main__":
    rfm = init_rfm()
