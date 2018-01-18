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
class Device:
    def __init__(self, d_type, name, rfm, mqtt_c):
        __types_devices = {
                        'RELAY': "devices/relays/",
                        'DIM_CRANE': "devices/dimmers/crane/",
                        'DIM_CURT': "devices/dimmers/curt/",
                        'DIM_STEP': "devices/dimmers/stepper/",
                        'DIM_TRMRL': "devices/dimmers/trmrl/",
        }
        if d_type in __types_devices:
            self.rfm = rfm
            self.mqtt_c = mqtt_c
            self.d_type = d_type
            self.name = name
            self.topic = "oh/"+__types_devices[d_type]+name
            self.mqtt_c.subscribe(self.topic)
            self.mqtt_c.message_callback_add(self.topic, self.write2device)
        else:
            log.error("Invalid device type: %s" %d_type)

    #TEMP: place for rand fux
    def write2device(self, clnt, usrdt, msg):
        log.debug("SENT from: %s NUDES: %s" %(msg.topic, msg.payload))
        if self.d_type=='RELAY':
            log.debug("AMA RELAY: %s, VAL: %s" %(self.name, msg.payload))
        else:
            log.debug("AMA: %s, VAL: %s" %(self.d_type, msg.payload))

class Sencor:
    def __init__(self, d_type, name, rfm, mqtt_c, timeout):
        __types_sncs = {
                        'SNC_T_AIR': "oh/sncs/temp/air/",
                        'SNC_T_WATER': "oh/sncs/temp/water/",
                        'SNC_T_HEATER': "oh/sncs/temp/heater/",
                        'SNC_HUMI': "oh/sncs/humi/",
                        'SNC_LUMI': "oh/sncs/lumi/",
                        'SNC_DOOR': "oh/sncs/doors",
                        'WARN_LEAK': "oh/warn/leak/",
                        'WARN_SMOKE': "oh/warn/smoke/",
                        'WARN_FLAME': "oh/warn/flame/",
                        'PRES_PRES': "oh/pres/pres/",
                        'PRES_MOT': "oh/pres/motion/",
                        'CNTR': "oh/cntrs/"
        }
        if d_type in __types_sencors:
            self.rfm = rfm
            self.mqtt_c = mqtt_c
            self.d_type = d_type
            self.name = name
            self.topic = __types_sencors[d_type]+name
            self.timeout = timeout
        else:
            log.error("Invalid device type: %s" %d_type)

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
                        "SNC_T_AIR": [19.00, 25.00],
                        "SNC_T_WATER": [5.00, 22.00],
                        "SNC_T_HEATER": [50.00, 100.00],
                        "SNC_LUMI": [150.00, 300.00],
                    }
        __val_int_limits = {
                        "CNTR": [100, 500],
                        "SNC_HUMI": [0, 100],
        }
        __definitions = {
                        "SNC_DOOR": ["OPEN", "CLOSED"],
                         "PRES_PRES": ["HIGH", "LOW"],
                         "PRES_MOT": ["HIGH", "LOW"],
                         "WARN_LEAK": ["HIGH", "LOW"],
                         "WARN_SMOKE": ["HIGH", "LOW"],
                         "WARN_FLAME": ["HIGH", "LOW"]
                 }
        if d_type in __definitions:
            state = random.randint(0,1)
            out = __definitions[self.d_type][state]
        elif d_type in __val_float_limits:
            out = random.uniform(__val_float_limits[self.d_type][0],
                                __val_float_limits[self.d_type][1])
        elif d_type in __val_int_limits:
            out = random.randint(__val_int_limits[self.d_type][0],
                                __val_int_limits[self.d_type][1])

        self.last_responce = time.time()
        return out

#DEBUG: just 4 tests
if __name__ == "__main__":
    rfm = init_rfm()
    mqtt_client = mqtt_init()
    # try:
    log.info("Init of devices")
    fake_t_air = Sencor("SNC_T_AIR", "1", rfm, mqtt_client, 60)
    fake_t_wat = Sencor("SNC_T_WATER", "1", rfm, mqtt_client, 60)
    fake_t_heat = Sencor("SNC_T_HEATER", "1", rfm, mqtt_client, 60)

    fake_humi = Sencor("SNC_HUMI", "1", rfm, mqtt_client, 60)
    fake_lumi = Sencor("SNC_LUMI", "1", rfm, mqtt_client, 60)

    fake_door = Sencor("SNC_DOOR", "1", rfm, mqtt_client, 60)

    fake_leak = Sencor("WARN_LEAK", "1", rfm, mqtt_client, 60)
    fake_smoke = Sencor("WARN_SMOKE", "1", rfm, mqtt_client, 60)
    fake_flame = Sencor("WARN_FLAME", "1", rfm, mqtt_client, 60)

    fake_pres = Sencor("PRES_PRES", "1", rfm, mqtt_client, 60)
    fake_mot = Sencor("PRES_MOT", "1", rfm, mqtt_client, 60)

    fake_cntr = Sencor("CNTR", "1", rfm, mqtt_client, 60)

    fake_relay = Device("RELAY", "1", rfm, mqtt_client, 60)
    fake_crane = Device("DIM_CRANE", "1", rfm, mqtt_client, 60)
    fake_curt = Device("DIM_CURT", "1", rfm, mqtt_client, 60)
    fake_step = Device("DIM_STEP", "1", rfm, mqtt_client, 60)
    fake_trmrl = Device("DIM_TRMRL", "1", rfm, mqtt_client, 60)

    # except Exception as e:
    #     log.error("Init fux")
    #     raise(e)

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
