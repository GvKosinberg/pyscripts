#!/usr/bin/python
# -*- coding: utf8 -*-
# Author: Antipin S.O. @RLDA

import rfm69
import paho.mqtt.client as mqtt
import logging
import time

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("test_500")

def init_rfm():
    myconf = rfm69.RFM69Configuration()
    rfm_unit = rfm69.RFM69(
                            dio0_pin=24,
                            reset_pin=22,
                            spi_channel=0,
                            config=myconf)
    # setting RSSI treshold
    rfm_unit.set_rssi_threshold(-114)
    return rfm_unit

def mqtt_on_connect(client, userdata, flags, rc):
    '''
        При подключении к порту брокера
    '''
    log.info("Connected to MQTT with rc: %s" % rc)

def mqtt_on_disconnect(client, userdata, rc):
    '''
        При отключении от брокера
    '''
    if rc != 0:
        log.warn("Unexpected disconnection")
    else:
        log.info("Expected disconnection")

def init_mqtt():
    """
        Функция инициализации клиента mqtt
        на выходе - объект класса mqtt.client
    """
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = mqtt_on_connect
    mqtt_client.on_disconnect = mqtt_on_disconnect

    mqtt_client.connect("localhost", 1883, 60)
    mqtt_client.loop_start()
    return mqtt_client


if __name__ == '__main__':
    packs_received = 0
    rfm = init_rfm()
    mqtt = init_mqtt()
    t_start = time.time()
    t_duration = 600
    t_finish = t_start + t_duration
    try:
        while(time.time() != t_finish):
            income = rfm.wait_for_packet()
            if type(income) != None:
                packs_received += 1
    except KeyboardInterrupt:
        log.info("That's all, folks")
    except Exception as e:
        log.critical(e)
    finally:
        log.info("Script finished. Num of packs: %s" % packs_received)
