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

def read(rfm):
	a_val = random.randint(0, 100)
	a_topic = "sumnum/a"
	pbl.single(a_topic, a_val, hostname="localhost", port=1883)

	temp_rfm_val = rfm.read_temperature()
	temp_rfm_top = "sumnum/trf"
	pbl.single(temp_rfm_top, temp_rfm_val, hostname="localhost", port=1883)

	inc_data = rfm.wait_for_packet(15)

	if type(inc_data) == tuple :

		num_of_sncs = inc_data[0][4]
		num_of_sncs_top = "sumnum/nss"
		pbl.single(num_of_sncs_top, num_of_sncs, hostname="localhost", port=1883)

		print("num uv sncrs:", num_of_sncs)
		for i in range(6, (6+(2*num_of_sncs)), 2):
			sb = inc_data[0][i]<<8
			lb = inc_data[0][i-1]
			temp_snc_val = ((lb | sb)&0x3ff)/(4*1.0)
			temp_snc_num = "sumnum/sncs/"+str((i-6)/2)
#			print(temp_snc_num)
			pbl.single(temp_snc_num, temp_snc_val, hostname="localhost", port=1883)

def write():
	pass

if __name__ == "__main__":
	rfm = init()
	while True:
		read(rfm)
		time.sleep(5)
	print("That's all, folks!")
