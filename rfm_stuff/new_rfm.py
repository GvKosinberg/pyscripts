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
# path = "pylog/pylog.log"
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

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

class RPI_hub(object):
    """
        Класс центрального хаба для устройств, в сущности просто объединение
        объектов rfm, mqtt_client. Включает в себя список инициализированных
        датчиков, для прохода и обновления данных в брокере.
    """
    def __init__(self, ip="192.168.0.56"):
        self.rfm = self.init_rfm()
        self.ip = ip
        self.mqtt_client = self.init_mqtt()
        self.snc_list = []

    def add_snc(self, snc):
        """
            Добавить объект класса Sencor в список
        """
        self.snc_list.append(snc)

    def init_rfm(self):
        """
            Инициализация RFM69
            На выходе объект класса rfm69
        """
        rfm_unit = "RFM zaglushka"
        myconf = rfm69.RFM69Configuration()
        rfm_unit = rfm69.RFM69(
                                dio0_pin=24,
                                reset_pin=22,
                                spi_channel=0,
                                config=myconf)
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

    def init_mqtt(self):
        """
            Функция инициализации клиента mqtt
            на выходе - объект класса mqtt.client
        """
        mqtt_client = mqtt.Client()
        mqtt_client.on_connect = self.mqtt_on_connect
        mqtt_client.on_disconnect = self.mqtt_on_disconnect

        mqtt_client.connect(self.ip, 1883, 60)
        mqtt_client.loop_start()
        return mqtt_client

    def loop(self):
        """
            Бесконечный цикл опроса
        """
        try:
            while True:
                self.read_real()
                self.snc_passage()
        except Exception as e:
            log.critical("Critical exc in loop")
            log.critical(str(e))
        except KeyboardInterrupt:
            log.info("That's all, folks")

    def read_real(self):
        """
            Метод чтения данных с rfm
        """
        log.debug("##=======New iter=========##")
        # Ожидание сообщения
        inc_data = self.rfm.wait_for_packet(59)

        # Проверка данных (если данные не пришли type(inc_data!=None))
        # если ответ пришел, данные записываются в кортеж
        if type(inc_data) == tuple:
            # TEMP: Тестовая хренотень
            self.send_raw_data(inc_data)
            self.update_snc(inc_data)
        time.sleep(20)

    def send_raw_data(self, income):
        ''' Тестовая штука для отправки сырых данных в топики debug/ '''
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
            log.warn("Bad packet received: %s" % e)
            log.warn("Packet: %s" % income[0])

    def snc_passage(self):
        """
            Проход по списку датчиков и перезапись значений в брокер
        """
        for snc in self.snc_list:
            if snc.is_fake:
                snc.data = snc.get_random_state()
            else:
                snc.check_timeout()
            snc.write2mqtt()

    def update_snc(self, income):
        try:
            __types_sncs = {
                    '0': "SNC_T_AIR",
                    '3': "SNC_LUMI",
                    '6': 'CNTR',
                    '7': "SNC_DOOR",
                    '14': "DEV_RELAY",
                    '3378': "ENCLAVE"
            }
            addr_r = str(income[0][1])
            type_r = __types_sncs[str(income[0][2])]
            for snc in self.snc_list:
                if snc.snc_type == type_r:
                    snc.convert_data(income[0])
                    snc.write2mqtt()
        except Exception as e:
            log.warn("Bad packet received: %s" % e)
            log.warn("Packet: %s" % str(income[0]))


rpi_hub = RPI_hub()

class Sencor(object):
    def __init__(self, rpi_hub=rpi_hub):
        # Инициализация хаба из глобаьной области и
        self.rpi_hub = rpi_hub
        self.mqtt_c = self.rpi_hub.mqtt_client

        # таймаут ответа

        # время последнего ответа (*nix-style)
        self.last_responce = time.time()
        self.last_data = "-"

        # Полезные данные
        self.data = "Инициализация"
        self.rssi = 0
        self.bat_lvl = 0
        self.pack_id = 0

        self.topic_val = self.topic_com + "/val"
        self.topic_rssi = self.topic_com + "/rssi"
        self.topic_lstrsp = self.topic_com + "/lr"
        self.topic_bat = self.topic_com + "/bat"
        self.topic_packid = self.topic_com + "/packid"

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
                    (str(type(self))+":"+self.addr), __t_diff))

    def write2mqtt(self):
        # Для отображения в OH2
        self.mqtt_c.publish(self.topic_val, self.data)

        # DEBUG: Для разработки
        self.mqtt_c.publish(self.topic_rssi, self.rssi)
        self.mqtt_c.publish(self.topic_bat, self.bat_lvl)
        self.mqtt_c.publish(self.topic_lstrsp, self.last_responce)
        self.mqtt_c.publish(self.topic_packid, self.pack_id)

class Lumi_snc(Sencor):
    ''' Класс датчиков освещенности '''
    def __init__(self, addr, timeout=1080, is_fake=True):
        lumi_dict = {
        "snc_type": "SNC_LUMI",
        "topic": "oh/sncs/lumi",
        "limits": [150.00, 300.00],
        }


class Temp_snc(Sencor):
    ''' Класс датчиков температуры '''
    def __init__(self, addr, s_type, timeout=1080, is_fake=True):

        air_dict = {
        "snc_type": "SNC_T_AIR",
        "topic": "oh/sncs/temp/air/",
        "limits": [19.00, 25.00],
        }

        water_dict = {
        "snc_type": "SNC_T_WATER",
        "topic": "oh/sncs/temp/water/",
        "limits": [5.00, 22.00],
        }

        heater_dict = {
        "snc_type": "SNC_T_HEATER",
        "topic": "oh/sncs/temp/heater/",
        "limits": [50.00, 100.00],
        }

        __types = {
        "air": air_dict,
        "water": water_dict,
        "heater": heater_dict,
        }

        self.snc_type = __types[s_type]["snc_type"]
        log.debug("type in init: %s" % self.snc_type)

        self.addr = str(addr)
        self.topic_com = __types[s_type]["topic"] + self.addr
        self.d_timeout = timeout
        super(Temp_snc, self).__init__()


        self.is_fake = is_fake
        self.type_id = 0
        self.data_err = 0x7FF
        self.rpi_hub.add_snc(self)

    def convert_data(self, data):
        self.last_responce = time.time()

        log.debug("Testing data conversion")

        __data_lb = data[5]
        __data_sb = data[6] << 8

        __data_sum = (__data_lb | __data_sb) & 0xFFF

        log.debug("__data_sb = %s, __data_lb = %s, __data_sum = %s" % (__data_sb, __data_lb, __data_sum))
        if __data_sum == self.data_err:
            self.data = "Ошибка датчика"
        else:
            self.data = str(__data_sum/10.00) + " °C"
            log.debug("Air snc data after conversion: %s" % self.data)

    def get_random_state(self):
        ''' Генератор псевдослучайных значений '''
        __limits = __types[s_type]["limits"]
        random_data = random.uniform(__limits[0], __limits[1])
        return random_data


if __name__ == '__main__':
    log.info("Entered main")
    real_air_snc_1 = Temp_snc(addr = 1, s_type="air", is_fake=False)
    fake_water_snc_2 = Temp_snc(addr = 2, s_type="water")
    fake_water_snc_3 = Temp_snc(addr = 3, s_type="heater")

    rpi_hub.loop()
