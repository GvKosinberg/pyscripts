#!/usr/bin/python
# -*- coding: utf8 -*-
#Author: Antipin S.O. @RLDA
import os, sys
import rfm69
import logging
import time
import random
import paho.mqtt.publish as pbl

"""
	Инициализация логгера, RFM69
	На выходе объект класса rfm69
"""
def init():

	logging.basicConfig(level=logging.DEBUG)

	myconf = rfm69.RFM69Configuration()

	tt = rfm69.RFM69(dio0_pin=24, reset_pin=22, spi_channel = 0, config = myconf)

	#setting RSSI treshold
	tt.set_rssi_threshold(-114)
	return tt

"""
	Записать данные dt в топик tpc
"""
def write(tpc, dt):
	pbl.single(tpc, dt, hostname="localhost", port=1883)

"""
	Считать данные (реальные)
"""
def read_real(rfm):
	# 	inc_data = rfm.wait_for_packet(15)
	#
	# 	if type(inc_data) == tuple :
	#
	# 		num_of_sncs = inc_data[0][4]
	# 		num_of_sncs_top = "sumnum/nss"
	# 		pbl.single(num_of_sncs_top, num_of_sncs, hostname="localhost", port=1883)
	#
	# 		print("num uv sncrs:", num_of_sncs)
	# 		for i in range(6, (6+(2*num_of_sncs)), 2):
	# 			sb = inc_data[0][i]<<8
	# 			lb = inc_data[0][i-1]
	# 			temp_snc_val = ((lb | sb)&0x3ff)/(4*1.0)
	# 			temp_snc_num = "sumnum/sncs/"+str((i-6)/2)
	# #			print(temp_snc_num)
	# 			pbl.single(temp_snc_num, temp_snc_val, hostname="localhost", port=1883)
	pass

"""
	Привести формат данных от датчиков к удобоваримому для openhab
"""
def get_random_state(fmt):
    state = random.randint(0,1)
    defas = {"OC": ["OPEN", "CLOSED"],
             "OO": ["ON", "OFF"],
             "HL": ["HIGH", "LOW"]}
    out = defas[fmt][state]
    return out


"""
	Считать данные (рандом для тестов)
"""
def read_fake(rfm):
	"""
		*_val - значение
		*_top - адрес топика в брокере
		write - функция записи в броекер
	"""

	#Температура из регистра чипа rfm69
	temp_rfm_val = rfm.read_temperature()
	temp_rfm_top = "oh/trf"
	write(temp_rfm_top, temp_rfm_val)

	#Температуры воздуха, воды, отопления соответственно
	snc_temp_air_val = random.uniform(19.00, 25.00)
	snc_temp_air_top = "oh/sncs/temp/air"
	write(snc_temp_air_top, snc_temp_air_val)
	snc_temp_water_val = random.uniform(5.00, 22.00)
	snc_temp_water_top = "oh/sncs/temp/water"
	write(snc_temp_water_top, snc_temp_water_val)
	snc_temp_heater_val = random.uniform(50.00, 100.00)
	snc_temp_heater_top = "oh/sncs/temp/heater"
	write(snc_temp_heater_top, snc_temp_heater_val)

	#Освещенность в люксах
	snc_lumi_val = random.uniform(150.00, 300.00)
	snc_lumi_top = "oh/sncs/lumi/1"
	write(snc_lumi_top, snc_lumi_val)

	#Влажность в процентах
	snc_humi_val = random.randint(0, 100)
	snc_humi_top = "oh/sncs/humi/1"
	write(snc_humi_top, snc_humi_val)

	#Двери (откр/закр)
	door_val = get_random_state("OC")
	door_top = "oh/sncs/doors/1"
	write(door_top, door_val)

	#Счетчики
	counter_val = random.randint(100, 500)
	counter_top = "oh/cntrs/1"
	write(counter_top, counter_val)

	#Датчики утечки, дыма и огня соответственно
	snc_leak_val = get_random_state("HL")
	snc_leak_top = "oh/warn/leak"
	write(snc_leak_top, snc_leak_val)

	snc_smoke_val = get_random_state("HL")
	snc_smoke_top = "oh/warn/smoke"
	write(snc_smoke_top, snc_smoke_val)

	snc_flame_val = get_random_state("HL")
	snc_flame_top = "oh/warn/flame"
	write(snc_flame_top, snc_flame_val)

	#Датчики присутствия и движения соответственно
	pres_pres_val = get_random_state("HL")
	pres_pres_top = "oh/pres/pres"
	write(pres_pres_top, pres_pres_val)

	pres_motion_val = get_random_state("HL")
	pres_motion_top = "oh/pres/motion"
	write(pres_motion_top, pres_motion_val)

	#Вывод в консольпо завершению итерации цикла чтения/записи
	print("Done")

if __name__ == "__main__":
	int cntr = 0;
	rfm = init()
	try:
		while True:
			read_fake(rfm)
			time.sleep(10)
			print(cntr)
			cntr++
	except KeyboardInterrupt:
		print("That's all, folks!")
		
