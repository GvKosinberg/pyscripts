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
    rfm_unit.config.packet_config_1.variable_length = False
    return rfm_unit

def write_true():
    pack = [210, 4, 0, 14, 0, 0b01]
    # pack[0] = 210
    # pack[1] =
    rfm.send_packet(pack)


if __name__ == '__main__':
    rfm = init_rfm()
    try:
        write_true()
    except KeyboardInterrupt:
        print("That's all, folks")
