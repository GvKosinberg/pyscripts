
import radio_t_2_http as r2h

m_cycle = r2h.cycle(delay=5)

#INIT HTTP PARAMETERS#
#http_parameters = 'http://127.0.0.1:8000'
http_parameters = 'http://kocuoneu.pythonanywhere.com'

#INIT MODBUS PARAMETERS#
mb_parameters = r2h.mbus("rtu", 'COM6', 1, 8, 'N', 9600, 1)
#mb_parameters = mbus("rtu", '/dev/ttyAMA0', 1, 8, 'N', 9600, 1)

#INIT OBJECTS#
#--HUB №1--#
hub_num_1 = r2h.Hub(1, m_cycle, mb_parameters, 1, http_parameters)
susp_1 = r2h.Susp(parent_hub=hub_num_1, susp_id=1)


m_cycle.start()
