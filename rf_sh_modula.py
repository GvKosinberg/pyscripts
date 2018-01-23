#!/usr/bin/python
# -*- coding: utf8 -*-
# Author: Antipin S.O. @RLDA

"""
    Подключение необходимых модулей
"""
import os
import sys
import gc

import rfm69
import paho.mqtt.client as mqtt

import time

# DEBUG: dev_stuff
import random
import logging


"""
    Подключение консольного логера
"""


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("rf_sh_modula")


"""
    Инициализация RFM69
    На выходе объект класса rfm69
"""


def init_rfm():
    # TEMP: faek rfm unit
    # rfm_unit = "sum_sh1et"
    #
    myconf = rfm69.RFM69Configuration()
    rfm_unit = rfm69.RFM69(
                            dio0_pin=24,
                            reset_pin=22,
                            spi_channel=0,
                            config=myconf)
    # setting RSSI treshold
    rfm_unit.set_rssi_threshold(-114)
    return rfm_unit


"""
    Инициализация клента mqtt-брокера
"""


def mqtt_on_connect(client, userdata, flags, rc):
    '''
        При подключении к порту брокера
    '''
    log.info("Connected to MQTT with rc: %s" % rc)


def mqtt_on_message(client, userdata, msg):
    '''
        При поступлении сообщения
    '''


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
    # mqtt_client.on_message = mqtt_on_message
    mqtt_client.on_disconnect = mqtt_on_disconnect

    mqtt_client.connect("localhost", 1883, 60)
    log.debug("start loop")
    mqtt_client.loop_start()
    return mqtt_client


"""
    Класс исполнительных устройств
    d_type - тип устройства в формате __types_devices (string)
    name - собственное имя устройства (или номер) (string)
    rfm - экземпляр RFM69
    mqtt_c - экземпляр paho.mqtt.Client
"""


class Device:
    '''
        Инициализация объекта
    '''
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
            # топик в mqtt-брокере
            self.topic = "oh/"+__types_devices[d_type]+name
            # подписка на топик
            self.mqtt_c.subscribe(self.topic)
            # Создание event в случае поступления сообщения в топик
            # NOTE: работает даже в time.sleep, rfm.wait_for_packet
            self.mqtt_c.message_callback_add(self.topic, self.write2device)
        else:
            log.error("Invalid device type: %s" % d_type)

    '''
        Функция отправки команды на конечное устройство
    '''
    def write2device(self, clnt, usrdt, msg):
        log.debug("SENT from: %s NUDES: %s" % (msg.topic, msg.payload))
        if self.d_type == 'RELAY':
            log.debug("AMA RELAY: %s, VAL: %s" % (self.name, msg.payload))
        else:
            log.debug("AMA: %s:%s, VAL: %s" % (
                self.d_type, self.name, msg.payload))


"""
    Класс исполнительных устройств
    d_type - тип устройства в формате __types_devices (string)
    name - собственное имя устройства (или номер) (string)
    rfm - экземпляр RFM69
    mqtt_c - экземпляр paho.mqtt.Client
    timeout - время таймаута
"""


class Sencor:
    '''
        Инициализация объекта
    '''
    def __init__(self, d_type, name, rfm, mqtt_c, timeout):
        __types_sncs = {
                        'SNC_T_AIR': "oh/sncs/temp/air/",
                        'SNC_T_WATER': "oh/sncs/temp/water/",
                        'SNC_T_HEATER': "oh/sncs/temp/heater/",
                        'SNC_HUMI': "oh/sncs/humi/",
                        'SNC_LUMI': "oh/sncs/lumi/",
                        'SNC_DOOR': "oh/sncs/doors/",
                        'WARN_LEAK': "oh/warn/leak/",
                        'WARN_SMOKE': "oh/warn/smoke/",
                        'WARN_FLAME': "oh/warn/flame/",
                        'PRES_PRES': "oh/pres/pres/",
                        'PRES_MOT': "oh/pres/motion/",
                        'CNTR': "oh/cntrs/"
        }
        if d_type in __types_sncs:
            self.rfm = rfm
            self.mqtt_c = mqtt_c
            self.d_type = d_type
            self.name = name
            # топик в mqtt-брокере
            self.topic = __types_sncs[d_type]+name
            # таймаут ответа
            self.d_timeout = timeout
            # время последнего ответа (*nix-style)
            self.last_responce = time.time()
        else:
            log.error("Invalid device type: %s" % d_type)

    '''
        Метод проверки timeout'а ответа
        если ответа не было дольше, чем timout сек,
        то устанавливает data = "-" (на странице в openhab'е - "ОШИБКА")
    '''

    def check_timeout(self):
        razn = time.time() - self.last_responce
        if razn > self.d_timeout:
            self.data = "-"
        log.debug("Sencor: %s: time between responces: %s" % (
            (self.d_type+":"+self.name),
            razn))

    '''
        Метод записи полученного значения датчика в брокер
    '''

    def write2mqtt(self):
        mqtt_topic = self.topic

        self.check_timeout()

        # TEMP: random data
        if (self.d_type!='SNC_T_AIR' and self.d_type!='SNC_LUMI'):
            self.data = self.get_random_state()

        mqtt_val = self.data
        self.mqtt_c.publish(mqtt_topic, mqtt_val)

        log.debug('SNC: %s: VAL: %s ' % (mqtt_topic, mqtt_val))
        # print('Last responce: %s' %str(self.last_responce))

    # TEMP: random generator for tests
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
        if self.d_type in __definitions:
            state = random.randint(0, 1)
            out = __definitions[self.d_type][state]
        elif self.d_type in __val_float_limits:
            out = random.uniform(
                __val_float_limits[self.d_type][0],
                __val_float_limits[self.d_type][1])
        elif self.d_type in __val_int_limits:
            out = random.randint(
                __val_int_limits[self.d_type][0],
                __val_int_limits[self.d_type][1])

        self.last_responce = time.time()
        return out


"""
    Функция чтения занчений с rfm
    если ничего не поступило, функция записи в mqtt все равно будет вызвана,
    т.к. там есть метод проверки таймаута ответа
"""


def read_real(rfm, snc_list):
    # коды типов устройств и соответствующие им ключи
    __types = {
                '0': "TEMP_AIR",
                '3': "SNC_LUMI",
                '3378': "ENCLAVE"
    }
    r_type = "-"
    r_name = "-"

    # Ожидание сообщения
    inc_data = rfm.wait_for_packet(60)

    # Проверка данных (если данные не пришли type(inc_data!=None))
    # если ответ пришел, данные записываются в кортеж
    if type(inc_data) == tuple:
        # адрес устройства
        d_addr = inc_data[0][1]
        # код типа устройства
        d_type = inc_data[0][2]
        # Старший байт данных
        data_sb = inc_data[0][6] << 8
        # Младший байт данных
        data_lb = inc_data[0][5]
        # Итоговые данные
        data_sum = 0

        # XXX
        log.info("d_adr: %s || d_type: %s" %(d_adr, d_type))

        # Проверка на наличие кода типа в списке
        if d_type in __types:
            # Присвоение ключа по коду
            r_type = __types[d_type]
            # Присвоение имени (string)
            r_name = str(d_addr)

            log.info("r_type: %s || r_name: %s" %(r_type, r_name))

            if (r_type=="TEMP_AIR" and d_addr!=0xcd):
                data_sum = ((lb | sb)&0xfff)/(16*1.0)
                log.warn("hhir is tempa")
                log.warn("datka = %s" % data_sum)
            elif (r_type=="SNC_LUMI"):
                data_sum = lb | sb
                log.warn("hhir is lumma")
                log.warn("datka = %s" % data_sum)
        time.sleep(5)

    # Проход списка объектов класса Sencor
    for obj in snc_list:
        # Если имя и тип совпали с прочитанными на rfm
        if obj.d_type == r_type and obj.name == "1":
            obj.data = data_sum
        # Вызов метода публикаци данных в брокере
        obj.write2mqtt()


"""
    Функция составления списка всех объектов класса Sencor
    на выходе - list[Sencor]
"""


def get_snc_list():
    snc_list = []
    for obj in gc.get_objects():
        if isinstance(obj, Sencor):
            snc_list.append(obj)
    return snc_list


# DEBUG: just 4 tests
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

    fake_relay = Device("RELAY", "1", rfm, mqtt_client)
    fake_crane = Device("DIM_CRANE", "1", rfm, mqtt_client)
    fake_curt = Device("DIM_CURT", "1", rfm, mqtt_client)
    fake_step = Device("DIM_STEP", "1", rfm, mqtt_client)
    fake_trmrl = Device("DIM_TRMRL", "1", rfm, mqtt_client)

    # except Exception as e:
    #     log.error("Init fux")
    #     raise(e)

    snc_list = get_snc_list()
    try:
        log.info("Enter the cycle")
        while(True):
            read_real(rfm, snc_list)
            log.debug("//===========//")
    except KeyboardInterrupt:
        log.info("That's all, folks")
