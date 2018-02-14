#!/usr/bin/python
# -*- coding: utf8 -*-
# Author: Antipin S.O. @RLDA

"""
    Подключение необходимых модулей
"""
import os
import sys

import rfm69
import paho.mqtt.client as mqtt

import time

# DEBUG: dev_stuff
import random
import logging
from logging.handlers import TimedRotatingFileHandler

"""
    Подключение логера
"""

path = "/home/pi/pyscripts/pylog/pylog.log"
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# add a rotating handler
rfh = TimedRotatingFileHandler(
                                path,
                                when="D",
                                interval=1,
                                backupCount=5)
rfh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter(
                        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
rfh.setFormatter(formatter)

log.addHandler(ch)
log.addHandler(rfh)


class rpi_hub(object):
    def __init__(self):
        self.rfm = self.rfm_init()
        self.mqtt_client = self.mqtt_init()
        self.snc_list = []
        # коды типов устройств и соответствующие им ключи
        self.types = {
                    '0': "SNC_T_AIR",
                    '3': "SNC_LUMI",
                    '3378': "ENCLAVE"
        }
        self.errors = {
                    'SNC_T_AIR': [0x7FF, 0x00, ],
                    'SNC_LUMI': [0xFFFF, 0x00, ],
        }


    def add_snc(self, snc):
        self.snc_list.append(snc)

    def rfm_init(self):
        """
            Инициализация RFM69
            На выходе объект класса rfm69
        """
        myconf = rfm69.RFM69Configuration()
        rfm_unit = rfm69.RFM69(
                                dio0_pin=24,
                                reset_pin=22,
                                spi_channel=0,
                                config=myconf)
        # setting RSSI treshold
        rfm_unit.set_rssi_threshold(-114)
        return rfm_unit


    def mqtt_on_connect(self, client, userdata, flags, rc):
        '''
            При подключении к порту брокера
        '''
        log.info("Connected to MQTT with rc: %s" % rc)


    def mqtt_on_disconnect(self, client, userdata, rc):
        '''
            При отключении от брокера
        '''
        if rc != 0:
            log.warn("Unexpected disconnection")
        else:
            log.info("Expected disconnection")


    def mqtt_init(self):
        """
            Функция инициализации клиента mqtt
            на выходе - объект класса mqtt.client
        """
        mqtt_client = mqtt.Client()
        mqtt_client.on_connect = self.mqtt_on_connect
        mqtt_client.on_disconnect = self.mqtt_on_disconnect

        mqtt_client.connect("localhost", 1883, 60)
        mqtt_client.loop_start()
        return mqtt_client

    def loop(self):
        while True:
            try:
                self.read_real()
                self.katok()
            except Exception as e:
                log.critical("Script has fallen")
                log.critical(str(e))
            except KeyboardInterrupt:
                log.info("That's all, folks")

    def katok(self):
        log.debug("qq: %s" % self.snc_list)
        for snc in self.snc_list:
            snc.write2mqtt()

    def send_raw_data(self, income):
        """
            Тестовая штука для отсылки сырых данных в топики debug/
        """

        __types = {
                    '0': "SNC_T_AIR",
                    '3': "SNC_LUMI",
                    '6': 'CNTR',
                    '7': "SNC_DOOR",
                    '14': "DEV_RELAY",
                    '3378': "ENCLAVE"
        }
        try:
            addr_r = str(income[0][1])
            type_r = str(income[0][2])

            topic_base = "debug/" + __types[type_r] + "/" + addr_r

            topic_arr = topic_base + "/arr"
            array = income[0]
            data = ""
            for i in array:
                data += str(hex(i)) + " "
            self.mqtt_client.publish(topic_arr, data)
            log.debug("RAW Topic %s, %s" % (topic_arr, data))

            topic_rssi = topic_base + "/rssi"
            data = str(income[1])
            self.mqtt_client.publish(topic_rssi, data)
            log.debug("RAW Topic %s, %s" % (topic_rssi, data))

            log.debug("RAW DATA SENT")
        except Exception as e:
            log.warn("Bad packet received: %s", e)
            log.warn("Packet: %s" % income[0])

    def read_real(self):
        """
            Метод чтения данных с rfm
        """

        # Ожидание сообщения
        inc_data = self.rfm.wait_for_packet(59)

        # Проверка данных (если данные не пришли type(inc_data!=None))
        # если ответ пришел, данные записываются в кортеж
        if type(inc_data) == tuple:
            # TEMP: Тестовая хренотень
            self.send_raw_data(inc_data)
            self.concat_data(inc_data)

    def concat_data(self, inc_data):
        d_addr = 0
        d_type = "-"
        d_rssi = 0
        d_packid = 0
        d_bat = 0
        __data_lb = 0
        __data_sb = 0
        data_sum = 0
        try:
            # адрес устройства
            d_addr = inc_data[0][1]
            # код типа устройства
            d_type = str(inc_data[0][2])
            # Уровень сигнала
            d_rssi = inc_data[1]
            # Номер пакета
            d_packid = inc_data[0][3]
            # Уровень батареи
            d_bat = inc_data[0][4]

            # Младший байт данных
            __data_lb = inc_data[0][5]
            # Старший байт данных
            __data_sb = inc_data[0][6] << 8
        except Exception as e:
            log.error("Bad pack received: %s" % inc_data)
            log.error("Exception: %s", e)
        # Проверка на наличие кода типа в списке
        if (d_type in self.types):
            # Присвоение ключа по коду
            r_type = self.types[d_type]
            # Присвоение имени (string)
            r_name = str(d_addr)

            if (__data_lb | __data_sb) in self.errors[r_type]:
                data_sum = "Ошибка датчика"
            else:
                # Преобразования данных для различных типов датчиков
                if (r_type == "SNC_T_AIR"):
                    d_s = (__data_lb | __data_sb) & 0xFFF
                    data_sum = str(d_s/10.00) + " °C"
                elif (r_type == "SNC_LUMI"):
                    data_sum = str(__data_lb | __data_sb) + " люкс"
            self.update_data(r_type, r_name, data_sum)

    def update_data(self, r_type, r_name, data):
        for snc in self.snc_list:
            if (snc.d_type == r_type) and (snc.name == r_name):
                snc.last_responce = time.time()
                snc.data = data
                snc.write2mqtt()
                log.info("Sencor %s data updated" % (snc.d_type+":"+snc.name))



class Device(object):
    """
        Класс исполнительных устройств
        d_type - тип устройства в формате __types_devices (string)
        name - собственное имя устройства (или номер) (string)
        rfm - экземпляр RFM69
        mqtt_c - экземпляр paho.mqtt.Client
    """

    def __init__(self, d_type, name, rpi_hub):
        '''
            Инициализация объекта
        '''
        __types_devices = {
                        'RELAY': "devices/relays/",
                        'DIM_CRANE': "devices/dimmers/crane/",
                        'DIM_CURT': "devices/dimmers/curt/",
                        'DIM_STEP': "devices/dimmers/stepper/",
                        'DIM_TRMRL': "devices/dimmers/trmrl/",
        }
        if d_type in __types_devices:
            self.rpi_hub = rpi_hub
            self.rfm = rpi_hub.rfm
            self.mqtt_c = rpi_hub.mqtt_client
            self.name = name
            # топик в mqtt-брокере
            self.topic = "oh/"+__types_devices[d_type]+name+"/val"
            # подписка на топик
            self.mqtt_c.subscribe(self.topic)
            # Создание event в случае поступления сообщения в топик
            # NOTE: работает даже в time.sleep, rfm.wait_for_packet
            self.mqtt_c.message_callback_add(self.topic, self.write2device)
        else:
            log.error("Invalid device type: %s" % d_type)

    def convert_data(self, msg):
        data_pack = [0, 0, 0, 0, 0]
        # NOTE: device self id/name
        data_pack[0] = int(self.name)
        # NOTE: server/hub addr
        data_pack[1] = 0
        # TODO: device group id
        data_pack[2] = 14
        # XXX: cnt of cmd ???
        data_pack[3] = 0

        data_mqtt = msg.payload
        # DEBUG: 4 relays
        data_pack[4] = 1 if msg.payload == "ON" else 0

        return data_pack


    def write2device(self, clnt, usrdt, msg):
        '''
            Метод отправки команды на конечное устройство
        '''
        log.debug("SENT from: %s DATA: %s" % (msg.topic, msg.payload))
        data_pack = self.convert_data(msg)
        log.debug("Data 2 transmit: %s" % data_pack)



class Sencor(object):
    """
        Класс исполнительных устройств
        d_type - тип устройства в формате __types_devices (string)
        name - собственное имя устройства (или номер) (string)
        rfm - экземпляр RFM69
        mqtt_c - экземпляр paho.mqtt.Client
        timeout - время таймаута
    """

    def __init__(self, d_type, name, rpi_hub, timeout=60):
        '''
            Инициализация объекта
        '''
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
            self.rpi_hub = rpi_hub
            self.d_type = d_type
            self.name = name
            # топики в mqtt-брокере
            self.topic_com = __types_sncs[d_type]+name
            self.topic_val = self.topic_com + "/val"
            self.topic_rssi = self.topic_com + "/rssi"
            self.topic_lstrsp = self.topic_com + "/lr"
            self.topic_bat = self.topic_com + "/bat"
            self.topic_packid = self.topic_com + "/packid"

            # таймаут ответа
            self.d_timeout = timeout
            # время последнего ответа (*nix-style)
            self.last_responce = time.time()
            self.last_data = "-"
            # Полезные данные
            self.data = "Инициализация"
            self.rssi = 0
            self.bat_lvl = 0
            self.pack_id = 0
            self.rpi_hub.add_snc()
        else:
            log.error("Invalid device type: %s" % d_type)

    def check_timeout(self):
        '''
            Метод проверки timeout'а ответа
            если ответа не было дольше, чем timout сек,
            то устанавливает data = "timeout"
        '''
        __t_diff = time.time() - self.last_responce
        if __t_diff > self.d_timeout:
            self.data = "Таймаут"
            log.debug("Sencor: %s: time between responces: %s" % (
                    (self.d_type+":"+self.name), __t_diff))

    def write2mqtt(self):
        '''
            Метод записи полученного значения датчика в брокер
        '''

        self.check_timeout()

        # TEMP: random data
        __realz = [
            'SNC_T_AIR',
            'SNC_LUMI',
        ]
        if (self.d_type not in __realz):
            self.data = self.get_random_state()
            log.debug("Random SNC:%s VAL: %s" % (self.d_type, self.data))

        # Для отображения в OH2
        self.mqtt_c.publish(self.topic_val, self.data)

        # Для разработки
        self.mqtt_c.publish(self.topic_rssi, self.rssi)
        self.mqtt_c.publish(self.topic_bat, self.bat_lvl)
        self.mqtt_c.publish(self.topic_lstrsp, self.last_responce)
        self.mqtt_c.publish(self.topic_packid, self.pack_id)

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


# DEBUG: just 4 tests
if __name__ == "__main__":

    rpi_hub = rpi_hub()
    # try:
    log.info("Init of devices")
    fake_t_air = Sencor("SNC_T_AIR", "1", rpi_hub)
    fake_t_wat = Sencor("SNC_T_WATER", "1", rpi_hub)
    fake_t_heat = Sencor("SNC_T_HEATER", "1", rpi_hub)

    fake_humi = Sencor("SNC_HUMI", "1", rpi_hub)
    fake_lumi = Sencor("SNC_LUMI", "9", rpi_hub)

    fake_door = Sencor("SNC_DOOR", "1", rpi_hub)

    fake_leak = Sencor("WARN_LEAK", "1", rpi_hub)
    fake_smoke = Sencor("WARN_SMOKE", "1", rpi_hub)
    fake_flame = Sencor("WARN_FLAME", "1", rpi_hub)

    fake_pres = Sencor("PRES_PRES", "1", rpi_hub)
    fake_mot = Sencor("PRES_MOT", "1", rpi_hub)

    fake_cntr = Sencor("CNTR", "1", rpi_hub)

    fake_relay = Device("RELAY", "1", rpi_hub)
    fake_crane = Device("DIM_CRANE", "1", rpi_hub)
    fake_curt = Device("DIM_CURT", "1", rpi_hub)
    fake_step = Device("DIM_STEP", "1", rpi_hub)
    fake_trmrl = Device("DIM_TRMRL", "1", rpi_hub)

    rpi_hub.loop()
