import rfm69
import logging
import time

logging.basicConfig(level=logging.DEBUG)

myconf = rfm69.RFM69Configuration()

#XXX
#bitrate
myconf.bitrate_msb = 0x1A#
myconf.bitrate_lsb = 0x0B

#freq dev
myconf.fdev_msb = 0x00#
myconf.fdev_lsb = 0x52

#BW filter
myconf.rx_bw = 0x55#

#LNA
myconf.lna = 0x88#

#PA_LVL
myconf.pa_level = (0x40 | (28))

#DIO
myconf.dio_mapping_1 = 0x12
myconf.dio_mapping_2 = 0x47

#Sync
myconf.sync_config = 0x88
myconf.sync_value_1 = (0x0101 >> 8)
myconf.sync_value_2 = 0x0101

#Packet config #WWWW#
myconf.packet_config_2 = 0x02

#FIFO trsh
myconf.fifo_treshhold = 0x8F

#DAGC
myconf.test_dagc = 0x30

#FREQ
myconf.frf_msb = 0x6C
myconf.frf_mid = 0x48
myconf.frf_lsb = 0x0F
#XXX

tt = rfm69.RFM69(dio0_pin=24, reset_pin=22, spi_channel = 0, config = myconf)

#setting RSSI treshold
tt.set_rssi_threshold(-114)
#SET NODE AND BRDCAST
tt.spi_write(0x39, 0x01)
tt.spi_write(0x3A, 0xFF)
#SET PACKCONF1
tt.spi_write(0x37, 0x94)
#set AFC BW
tt.spi_write(0x1a, 0x8B)
#tt.spi_write(0x00, 0x00)

print(tt.read_temperature())
#print(tt.get_rssi())
for reg in tt.config.get_registers():
    print(hex(reg), hex(tt.spi_read(reg)))

print(hex(tt.spi_read(0x1a)))
dat = "test"
tt.send_packet(dat)

#tt.calibrate_rssi_threshold()

#print("fifo:", tt.spi_read(0x00))
#print(tt.wait_for_packet(timeout=20))
#time.sleep(1)
