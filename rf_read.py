import rfm69
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("rf_read")

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

if __name__ == '__main__':
    rfm = init_rfm()
    while(True):
        income = rfm.wait_for_packet(60)
        if type(income) == tuple:
            print(income)

            sb = inc_data[0][5]<<8
        	lb = inc_data[0][4]
        	temp = ((lb | sb)&0x3ff)/(4*1.0)
            print("ASas = %s" % temp)

            break
