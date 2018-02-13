import rfm69
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("testo")


s = 0
def init_rfm():
    myconf = rfm69.RFM69Configuration()
    rfm_unit = rfm69.RFM69(
                            dio0_pin=24,
                            reset_pin=22,
                            spi_channel=0,
                            config=myconf)
    # setting RSSI treshold
    rfm_unit.set_rssi_threshold(-114)
    #rfm_unit.config.packet_config_1.variable_length = False
    return rfm_unit

def write_true(i):
    pack = [210, 0, 14, 0]
    pack[4] = i
    # pack[0] = 210
    # pack[1] =
    rfm.send_packet(pack)


if __name__ == '__main__':
    rfm = init_rfm()
    msg = 0
    try:
        while True:
            msg = 1 if msg == 0 else 0
            write_true(msg)

            time.sleep(10)
    except KeyboardInterrupt:
        print("That's all, folks")
