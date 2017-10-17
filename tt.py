import serial
from pymodbus.pdu import ModbusRequest
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.transaction import ModbusRtuFramer

import logging
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

client = ModbusClient(method='rtu', port='COM6', timeout=0.5, baudrate=9600)

client.connect()


addr = 0x01FF
rr = client.read_holding_registers(addr, count=1, unit=1)
res = rr.getRegister(0)
print(str(rr))
print(res)
addr = 0x0101
r_sncs = client.read_holding_registers(addr, count=res, unit=1)
dd = {}
for num in range(0, res):
    __single_r_data = str(r_sncs.getRegister(num))
    __single_r = str(__single_r_data)
    __temporary_dict = {'snc_'+str(num): __single_r}
    dd.update(__temporary_dict)
print(dd)

client.close()


##XXX: dumps
    # #TEMP: test fn
    # def testo_rd(self):
    #     self.set_connection()
    #     addr = 0x0000
    #     _trans_data= {}
    #     q = 0
    #
    #     #__single_r_data = self.client.read_coils(0x0001, count=1, unit=1)
    #     _i_data = self.client.read_input_registers(addr, count=1, unit=1)
    #
    #     print(_i_data)
    #     try:
    #         q = round(_i_data.getRegister(0)/1640, 3)
    #     except Exception as e:
    #         q="NONE"
    #         print(e)
    #
    #     _trans_data = {'Input_0': q}
    #     #for num in range (0, 8):
    #     #    __single_r_data = str(_r_data.getBit(num))
    #     #    __single_r = str(__single_r_data)
    #     #    __temporary_dict = {'r_'+str(num): __single_r}
    #     #    _trans_data.update(__temporary_dict)
    #     self.disconnect()
    #     print(_trans_data)
    #     return _trans_data
