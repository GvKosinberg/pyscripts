import rfm69
import logging
import time
import random
import paho.mqtt.publish as pbl

def init():

	logging.basicConfig(level=logging.DEBUG)

	myconf = rfm69.RFM69Configuration()

	tt = rfm69.RFM69(dio0_pin=24, reset_pin=22, spi_channel = 0, config = myconf)

	#setting RSSI treshold
	tt.set_rssi_threshold(-114)
	return tt

def write(toppo, datto):
	pbl.single(toppo, datto, hostname="localhost", port=1883)

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

def get_random_state(fmt):
	if fmt=="OC":
		if random.randint(0,1)==0:
			out = "CLOSED"
		else:
			out = "OPEN"
	elif fmt=="OO":
		if random.randint(0,1)==0:
			out = "OFF"
		else:
			out = "ON"
	return(out)



def read_fake(rfm):
	temp_rfm_val = rfm.read_temperature()
	temp_rfm_top = "oh/trf"
	write(temp_rfm_top, temp_rfm_val)

	snc_temp_air_val = random.uniform(19.00, 25.00)
	snc_temp_air_top = "oh/sncs/temp/air"
	write(snc_temp_air_top, snc_temp_air_val)
	snc_temp_water_val = random.uniform(5.00, 22.00)
	snc_temp_water_top = "oh/sncs/temp/water"
	write(snc_temp_water_top, snc_temp_water_val)
	snc_temp_heater_val = random.uniform(50.00, 100.00)
	snc_temp_heater_top = "oh/sncs/temp/heater"
	write(snc_temp_heater_top, snc_temp_heater_val)

	snc_lumi_val = random.uniform(150.00, 300.00)
	snc_lumi_top = "oh/sncs/lumi/1"
	write(snc_lumi_top, snc_lumi_val)

	snc_humi_val = random.randint(0, 100)
	snc_humi_top = "oh/sncs/humi/1"
	write(snc_humi_top, snc_humi_val)

	# door_val = get_random_state("OC")
	# door_top = "oh/sncs/doors/1"
	# write(door_top, door_val)
	print("Done")

if __name__ == "__main__":
	rfm = init()
	while True:
		read_fake(rfm)
		time.sleep(5)
	print("That's all, folks!")
