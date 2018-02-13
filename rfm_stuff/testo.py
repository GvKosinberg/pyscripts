import rfm69
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("testo")

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
    cnt_min = 0
    rfm = init_rfm()
    try:
        while(True):
            cnt_min += 1
            print("Iter #: %s" % cnt_min)
            income = rfm.wait_for_packet(10)
            if type(income) == tuple:
                num_pack = income[0][3]
                log.info("///////////======================///////////")
                log.info("Pack: %s VS It: %s" %(num_pack, cnt_min))
    except KeyboardInterrupt:
        print("That's all, folks")
