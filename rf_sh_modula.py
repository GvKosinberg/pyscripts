#!/usr/bin/python
# -*- coding: utf8 -*-
#Author: Antipin S.O. @RLDA

"""
    Подключение необходимых модулей
"""
import os, sys

#TODO: uncomment 4 realz
import rfm69
import paho.mqtt.client as mqtt

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
    rfm_unit = rfm69.RFM69(dio0_pin=24, reset_pin=22, spi_channel = 0,
                            config = myconf)
	#setting RSSI treshold
    rfm_unit.set_rssi_threshold(-114)
    return rfm_unit

"""
    Инициализация клента mqtt-брокера
"""
def mqtt_on_connect(client, userdata, flags, rc):
    '''
        При подключении к порту брокера
    '''
    log.info("Connected to MQTT with rc: %s" %rc)

def mqtt_on_message(client, userdata, msg):
    '''
        При поступлении сообщения
    '''
    #log.debug("Message recived. Topic: %s, Msg: %s" %(msg.topic, msg.payload))

def mqtt_on_disconnect(client, userdata, rc):
    '''
        При отключении от брокера
    '''
    if rc != 0:
        log.warn("Unexpected disconnection")
    else:
        log.info("Expected disconnection")

"""
    Функция инициализации клиента mqtt
    на выходе - объект класса mqtt.client
"""
def mqtt_init():
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = mqtt_on_connect
    #mqtt_client.on_message = mqtt_on_message
    mqtt_client.on_disconnect = mqtt_on_disconnect

    mqtt_client.connect("localhost", 1883, 60)
    log.debug("start loop")
    mqtt_client.loop_start()
    return mqtt_client

"""
    Класс сенсоров/исполнительных устройств
    d_type - тип устройства для записи в формате топика mqtt (string)
    name - собственное имя устройства (или номер) (string)
    rfm - объект RFM69 (rfm)
    d_timeout - таймаут ответа от устройства в секундах (int)
"""
class Remote:
    def __init__(self, d_type, name, rfm, mqtt_c, d_timeout):
        #Тип устройства (датчик/исполнитель) (str)
        log.debug("enter the init")
        __types_sncs = [
                    "sncs/temp/air", "sncs/temp/water", "sncs/temp/heater",
                    "sncs/lumi", "sncs/humi", "sncs/doors",
                    "warn/leak", "warn/smoke", "warn/flame",
                    "pres/pres", "pres/motion", "FAKE"
                    ]
        __types_cntrs = [
                    "cntrs"
                    ]
        __types_devices = [
                    "devices/relays", "devices/dimmers/crane",
                    "devices/dimmers/curt", "devices/dimmers/stepper",
                    "devices/dimmers/trmrl"
                    ]
        try:
            log.debug("entered to try")
            if ((__types_sncs.index(d_type) != None) or
                (__types_cntrs.index(d_type) != None) or
                (__types_devices.index(d_type) != None)):
                self.d_type = d_type
                log.debug("it is a device")
        except Exception as e:
            log.warn("Invalid device type: %s", %self.d_type)
        #Имя (str)
        self.name = name
        #Название топика
        self.topic = "oh/"+self.d_type+"/"+self.name
        #Экземпляр класса rfm69 (rfm69)
        self.rfm = rfm
        #Экземпляр клиента mqtt
        self.mqtt_c = mqtt_c
        # if (__types_devices.index(d_type) != None):
        #     self.mqtt_c.subscribe(self.topic)
        #     self.mqtt_c.on_message=self.write2device

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
    def write2device(self, clnt, usrdt, msg):
        log.debug("SENT from: %s NUDES: %s" %(msg.topic, msg.payload))
        if self.d_type == "devices/relays":
            log.debug("SENDING %s to relay" %msg.payload)
        elif self.d_type == "devices/dimmers/crane":
            log.debug("SENDING %s to crane" %msg.payload)


    """
        Метод проверки timeout'а ответа
    """
    def check_timeout(self):
        razn = time.time() - self.last_responce
        if razn > self.d_timeout:
            self.data = "-"
        log.info("Device: %s: time between responces: %s"
                % ((self.d_type+"/"+self.name), razn))

    """
        Метод записи полученного значения датчика в брокер
    """
    def write2mqtt(self):
        mqtt_topic = self.topic

        self.check_timeout()

        #TEMP: random data
        self.data = self.get_random_state()

        mqtt_val = self.data
        self.mqtt_c.publish(mqtt_topic, mqtt_val)

        log.debug('Obj: %s: val: %s ' %(mqtt_topic, mqtt_val))
        #.print('Last responce: %s' %str(self.last_responce))


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
        __definitions = {
                        "sncs/doors": ["OPEN", "CLOSED"],
                         "pres/pres": ["HIGH", "LOW"],
                         "pres/motion": ["HIGH", "LOW"],
                         "warn/leak": ["HIGH", "LOW"],
                         "warn/smoke": ["HIGH", "LOW"],
                         "warn/flame": ["HIGH", "LOW"]
                 }
        if __definitions.get(self.d_type) != None:
            state = random.randint(0,1)
            out = __definitions[self.d_type][state]
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
    mqtt_client = mqtt_init()
    try:
        log.info("Init of devices")
        fake_t_air = Remote("sncs/temp/air", "1", rfm, mqtt_client, 60)
        fake_t_wat = Remote("sncs/temp/water", "1", rfm, mqtt_client, 60)
        fake_t_heat = Remote("sncs/temp/heater", "1", rfm, mqtt_client, 60)

        fake_humi = Remote("sncs/humi", "1", rfm, mqtt_client, 60)
        fake_lumi = Remote("sncs/lumi", "1", rfm, mqtt_client, 60)

        fake_door = Remote("sncs/doors", "1", rfm, mqtt_client, 60)

        fake_leak = Remote("warn/leak", "1", rfm, mqtt_client, 60)
        fake_smoke = Remote("warn/smoke", "1", rfm, mqtt_client, 60)
        fake_flame = Remote("warn/flame", "1", rfm, mqtt_client, 60)

        fake_pres = Remote("pres/pres", "1", rfm, mqtt_client, 60)
        fake_mot = Remote("pres/motion", "1", rfm, mqtt_client, 60)

        fake_cntr = Remote("cntrs", "1", rfm, mqtt_client, 60)

        fake_relay = Remote("devices/relays", "1", rfm, mqtt_client, 60)
        fake_trm_relay = Remote("devices/dimmers/trmrl", "1", rfm, mqtt_client, 60)
        fake_crane = Remote("devices/dimmers/crane", "1", rfm, mqtt_client, 60)
    except Exception as e:
        log.error("Init fux")
        raise(e)

    try:
        log.info("Enter the cycle")
        while(True):
            log.info("Current time: %s" %time.ctime())

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

            log.info("#=========================#")
            time.sleep(5)

    except KeyboardInterrupt:
        log.info("That's all, folks")
