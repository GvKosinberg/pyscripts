#!/usr/bin/python
# -*- coding: utf8 -*-
#Author: Antipin S.O. @RLDA

"""
    Подключение необходимых модулей
"""
import os, sys

#TODO: uncomment 4 realz
import rfm69
import paho.mqtt.publish as mqpb

import time

#DEBUG: dev_stuff
import random

"""
    Подключение консольного логера
"""
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("rf_sh_modula")

"""
	Инициализация RFM69
	На выходе объект класса rfm69
"""
def init_rfm():
    #TEMP: faek rfm unit
    #rfm_unit = "sum_sh1et"
    ##_____#
    myconf = rfm69.RFM69Configuration()
    rfm_unit = rfm69.RFM69(dio0_pin=24, reset_pin=22, spi_channel = 0, config = myconf)
	#setting RSSI treshold
    rfm_unit.set_rssi_threshold(-114)
    return rfm_unit

"""
    Класс управляемых устройств и сенсоров
    d_type - тип устройства для записи в формате топика mqtt (string)
    name - собственное имя устройства (или номер) (string)
    rfm - объект RFM69 (rfm)
    d_timeout - таймаут ответа от устройства в секундах (int)
"""
class Device:
    def __init__(self, d_type, name, rfm, d_timeout):
        #Тип устройства (датчик/исполнитель) (str)
        __types = [#-------------------------------------------#
                    "sncs/temp/air", "sncs/temp/water", "sncs/temp/heater",
                    "sncs/lumi", "sncs/humi", "sncs/doors",
                    "warn/leak", "warn/smoke", "warn/flame",
                    "pres/pres", "pres/motion", "FAKE",
                    #------------------------------------------#
                    "cntrs",
                    #------------------------------------------#
                    "devices/relays", "devices/dimmers"]

        try:
            if (__types.index(d_type) != None):
                self.d_type = d_type
        except Exception as e:
            log.warn("Invalid device type")
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
        log.info("Device: %s: last responce: %s"
                % ((self.d_type+"/"+self.name), razn))

    """
        Метод записи полученного значения датчика в брокер
    """
    def write2mqtt(self):
        mqtt_topic = "oh/" + self.d_type + "/" + self.name

        self.check_timeout()

        #TEMP: random data
        self.data = self.get_random_state()

        mqtt_val = self.data
        mqpb.single(mqtt_topic, mqtt_val, hostname="localhost", port=1883)

        log.info('Obj: %s ' %mqtt_topic)
        #.print('Last responce: %s' %str(self.last_responce))

        log.info(mqtt_val)

    """
        Метод отправки значения на исполнительное устройство
    """
    def write2control(self):
        pass

    #TEMP: random generator for tests
    def get_random_state(self):
        __val_float_limits = {
                        "sncs/temp/air": [19.00, 25.00],
                        "sncs/temp/water": [5.00, 22.00],
                        "sncs/temp/heater": [50.00, 100.00],
                        "sncs/lumi": [150.00, 300.00],
                    }
        __val_int_limits = {
                        "cntrs": [100, 500],
                        "sncs/humi": [0, 100],
                        "FAKE": [0, 3378],
        }
        __defas = {
                        "sncs/doors": ["OPEN", "CLOSED"],
                         "pres/pres": ["HIGH", "LOW"],
                         "pres/motion": ["HIGH", "LOW"],
                         "warn/leak": ["HIGH", "LOW"],
                         "warn/smoke": ["HIGH", "LOW"],
                         "warn/flame": ["HIGH", "LOW"]
                 }
        if __defas.get(self.d_type) != None:
            state = random.randint(0,1)
            out = __defas[self.d_type][state]
        elif __val_float_limits.get(self.d_type) != None:
            out = random.uniform(__val_float_limits[self.d_type][0],
                                __val_float_limits[self.d_type][1])
        elif __val_int_limits.get(self.d_type) != None:
            out = random.randint(__val_int_limits[self.d_type][0],
                                __val_int_limits[self.d_type][1])

        self.last_responce = time.time()
        return out

#DEBUG: just 4 tests
if __name__ == "__main__":
    rfm = init_rfm()
    try:
        fake_t_air = Device("sncs/temp/air", "1", rfm, 5)
        fake_t_wat = Device("sncs/temp/water", "1", rfm, 5)
        fake_t_heat = Device("sncs/temp/heater", "1", rfm, 5)

        fake_humi = Device("sncs/humi", "1", rfm, 5)
        fake_lumi = Device("sncs/lumi", "1", rfm, 5)

        fake_door = Device("sncs/doors", "1", rfm, 5)

        fake_leak = Device("warn/leak", "1", rfm, 5)
        fake_smoke = Device("warn/smoke", "1", rfm, 5)
        fake_flame = Device("warn/flame", "1", rfm, 5)

        fake_pres = Device("pres/pres", "1", rfm, 5)
        fake_mot = Device("pres/motion", "1", rfm, 5)

        fake_cntr = Device("cntrs", "1", rfm, 5)
    except Exception as e:
        log.warn("Init fux")
        raise(e)

    try:
        while(True):
            fake_t_air.write2mqtt()
            fake_t_wat.write2mqtt()
            fake_t_heat.write2mqtt()

            fake_humi.write2mqtt()
            fake_lumi.write2mqtt()

            fake_door.write2mqtt()

            fake_leak.write2mqtt()
            fake_smoke.write2mqtt()
            fake_flame.write2mqtt()

            fake_pres.write2mqtt()
            fake_mot.write2mqtt()

            fake_cntr.write2mqtt()
            time.sleep(5)
    except KeyboardInterrupt:
        log.info("That's all, folks")
