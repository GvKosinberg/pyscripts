import rfm69

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

def read_regs(rfm):
    for i in range(0x0, 0x70):
        reg_val = rfm.spi_read(i)
        print("REG: %s : %s" %(hex(i), hex(reg_val)))

if __name__ == '__main__':
    rfm = init_rfm()
    print(type(rfm))
    read_regs(rfm)
