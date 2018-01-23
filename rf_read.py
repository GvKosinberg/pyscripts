import rfm69
import logging

# logging.basicConfig(level=logging.DEBUG)
# log = logging.getLogger("rf_read")

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
            income = rfm.wait_for_packet(60)
            if type(income) == tuple:
                print(income)
                sb = income[0][6]<<8
                lb = income[0][5]
                if (income[0][2]==0):
                    if (income[0][1]==0xCD):
                        print("ur not supposed 2 b here. LEVELORD")
                    else:
                        temp = ((lb | sb)&0xfff)/(16*1.0)
                        print("Temp = %s" % temp)
                elif (income[0][2]==3):
                    lum = lb | sb
                    print("Lum = %s")
    except KeyboardInterrupt:
        print("That's all, folks")
