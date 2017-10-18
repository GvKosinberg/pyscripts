import requests
import serial
from pymodbus.pdu import ModbusRequest
from pymodbus.exceptions import ModbusIOException
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.transaction import ModbusRtuFramer
import json
import time
import sys

import logging
from logging.handlers import RotatingFileHandler

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')

logFile = 'log.txt'

my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024,
                                 backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.DEBUG)

app_log = logging.getLogger('root')
app_log.setLevel(logging.DEBUG)

app_log.addHandler(my_handler)


#MODBUS Parameters Class
class mbus:
    def __init__(self, mth, prt, stpb, btsz, par, bdrt, tmt):
        #method ("RTU", "TCP")
        self.mth = mth
        #port ('COM6' (windows), '/dev/ttyAMA0' (linux))
        self.prt = prt
        #stopbits (int)
        self.stpb = stpb
        #bytesize (int)
        self.btsz = btsz
        #parity ('N'-none)
        self.par  = par
        #baudrate (int)
        self.bdrt = bdrt
        #timeout
        self.tmt = tmt

#--------------------------------------------------------------#
#Hub class
class Hub:
    def __init__(self, h_id, cyc, mb_params, slv_adr, http_params):
        #Hub id (int)
        self.h_id = h_id
        #Modbus parameters (mbus object)
        self.mb_params = mb_params
        #Modbus slave address
        self.slv_adr = slv_adr
        #Root http of server
        self.http_params = http_params
        #XXX
        cyc.add_hub_to_list(self)
        #TODO: ss
        self.susps = []

    #void fn: Add suspension object to hub's list of suspensions
    def add_susp_to_list(self, susp_2_list):
        self.susps.append(susp_2_list)

    #boolean fn: Mbus init & open port
    def set_connection(self):
        #Modbus client inicialization with mbus parameters
        self.client= ModbusClient(method = self.mb_params.mth,
                                    port=self.mb_params.prt,
                                    stopbits = self.mb_params.stpb,
                                    bytesize = self.mb_params.btsz,
                                    parity = self.mb_params.par,
                                    baudrate = self.mb_params.bdrt,
                                    timeout = self.mb_params.tmt)
        #Open port
        self.connection = self.client.connect()
        return self.connection

    #void fn: Close port
    def disconnect(self):
        self.connection = self.client.close()

    #boolean fn: reads all params and convert them to dict w/ json
    def get_trans(self, susp):
        if self.set_connection():
            #read num of sncs
            __snc_cnt = susp.read_snc_cnt()

            #TODO: read temperatures
            __temps = json.dumps(susp.read_temps(__snc_cnt), sort_keys=True)

            #read charge level
            __charge = susp.read_charge()



            #pack data to transmission dict
            self.trans_data = {
                                'charge_level': __charge,
                                'num_of_sncs': __snc_cnt,
                                "temps": __temps
                                }

            self.disconnect()
            print("Transmission data:")
            print(self.trans_data)
            return True
        else:
            print("Can't connect to port")
            return False

    #void fn: gets transmission data & do a POST request to srever
    #(to h_id hub page)
    def post_http(self):
        #get transmission data
        for susp in self.susps:
            if self.get_trans(susp):
                #do a POST request
                try:
                    self.req = requests.post(self.http_params+'/hub/'
                                            +str(self.h_id)+'/susp/'
                                            +str(susp.susp_id)+'/',
                                            self.trans_data)
                    print("HTTP error code:", self.req.status_code)
                    #print("Responce:", self.req.text)
                except Exception as e:
                    print ("Can't reach host HTTP")
                    #print(e)
            else:
                print("Can't get transmission data")

#--------------------------------------------------------------#
class Susp:
    def __init__(self, parent_hub, susp_id,):
        self.parent_hub = parent_hub
        self.susp_id = susp_id
        parent_hub.add_susp_to_list(self)

    #int fn: reads num of sncs, returns (int)
    def read_snc_cnt(self):
        #address of suspension's num of sncs register
        __addr = self.susp_id<<8 | 0x00FF #a = adr_req<<8 | sncs_c
        #make a modbus request
        __snc_cnt_inc = self.parent_hub.client.read_holding_registers(
                                                __addr,
                                                count=1,
                                                unit=self.parent_hub.slv_adr)
        if isinstance(__snc_cnt_inc, ModbusIOException):
            print("Modbus register reading artifact: snc_cnt")
            time.sleep(1)
            __snc_cnt_inc = self.parent_hub.client.read_holding_registers(
                                                __addr,
                                                count=1,
                                                unit=self.parent_hub.slv_adr)

        try:
            _snc_cnt = __snc_cnt_inc.getRegister(0)
        except Exception as e:
            crit_err_cntr+=1
            print("Register reading issue")

        return _snc_cnt

    #dict fn: reads temperatures on sencors, returns dict with keys (val in str)
    #{"sncs_i": "12.3"}
    def read_temps(self, ns):
        #address of suspension's temperatures register
        __addr = self.susp_id<<8 | 0x0001
        #read num of sncs
        __num_of_sncs = ns

        __sncs_income_data = self.parent_hub.client.read_holding_registers(
                                                __addr,
                                                count=__num_of_sncs,
                                                unit=self.parent_hub.slv_adr)
        if isinstance(__sncs_income_data, ModbusIOException):
            print("Modbus register reading artifact: sncs_data")
            time.sleep(1)
            __sncs_income_data = self.parent_hub.client.read_holding_registers(
                                                __addr,
                                                count=__num_of_sncs,
                                                unit=self.parent_hub.slv_adr)

        #init dict for temps transmission
        _sncs_data = {}
        __single_temp = "0.0"

        #decomposition of responce & updating transmission dict
        for num in range (0, __num_of_sncs):
            try:
                __single_snc_data = __sncs_income_data.getRegister(num)
                #converting to string
                __single_temp = str(__single_snc_data/10)
            except Exception as e:
                crit_err_cntr+=1
                __single_snc_data="Register reading issue"
                print(e)
            _sncs_data[num] = __single_temp

        return _sncs_data

    #int fn: reads charge level, returns char("3.3")
    def read_charge(self):
        #address of suspension's charge register
        __addr = self.susp_id<<8 | 0x0000

        __inc_charge = self.parent_hub.client.read_holding_registers(
                                                __addr,
                                                count=1,
                                                unit=self.parent_hub.slv_adr)
        if isinstance(__inc_charge, ModbusIOException):
            print("Modbus register reading artifact: charge")
            time.sleep(1)
            __inc_charge = self.parent_hub.client.read_holding_registers(
                                                __addr,
                                                count=1,
                                                unit=self.parent_hub.slv_adr)

        try:
            _charge = str(__inc_charge.getRegister(0)/100)
        except Exception as e:
            crit_err_cntr+=1
            _charge="Register reading issue"
            print(e)

        #Read & convert
        #_charge = random.randint(0, 100)
        return _charge

class cycle:
    def __init__(self, delay):
        self.hubs_list = []
        self.delay = delay

    def add_hub_to_list(self, hub_2_list):
        self.hubs_list.append(hub_2_list)

    #INFINITE CYCLE#
    def start(self):
        it_cntr = 0
        crit_err_cntr = 0

        while 1:
            try:
                for hub in self.hubs_list:
                    try:
                        hub.post_http()
                    except Exception as e:
                        print(e)
                it_cntr += 1
                print("Iterations: ", it_cntr)
                print("Crit errors: ", crit_err_cntr)
                time.sleep(self.delay)

            except KeyboardInterrupt:
                inc_msg = input("Прервать цикл? (y/n):")
                while (inc_msg != 'y' and inc_msg != 'n'):
                    print("Некорректный ввод")
                    inc_msg = input("Прервать цикл? (y/n):")
                if inc_msg=='y':
                    break
                elif inc_msg=='n':
                    continue
