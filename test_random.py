import radio_t_2_http as r2h

m_cycle = r2h.cycle(delay=5)

#INIT HTTP PARAMETERS#
#http_parameters = 'http://127.0.0.1:8000'
#http_parameters = 'http://kocuoneu.pythonanywhere.com'
http_parameters = 'http://trm.grein.ru'

#INIT MODBUS PARAMETERS#
mb_parameters = r2h.mbus("rtu", 'COM6', 1, 8, 'N', 9600, 1)
#mb_parameters = mbus("rtu", '/dev/ttyAMA0', 1, 8, 'N', 9600, 1)

#INIT OBJECTS#
#--HUB №1--#
hub_num_1 = r2h.Hub(1, m_cycle, mb_parameters, 1, http_parameters)
susp_1 = r2h.Susp(parent_hub=hub_num_1, susp_id=1)
susp_2 = r2h.Susp(parent_hub=hub_num_1, susp_id=2)
susp_3 = r2h.Susp(parent_hub=hub_num_1, susp_id=3)
susp_4 = r2h.Susp(parent_hub=hub_num_1, susp_id=4)
susp_5 = r2h.Susp(parent_hub=hub_num_1, susp_id=5)
#--HUB №2--#
hub_num_2 = r2h.Hub(2, m_cycle, mb_parameters, 1, http_parameters)
susp_6 = r2h.Susp(parent_hub=hub_num_2, susp_id=6)
susp_7 = r2h.Susp(parent_hub=hub_num_2, susp_id=7)
susp_8 = r2h.Susp(parent_hub=hub_num_2, susp_id=8)
#--HUB №3--#
hub_num_3 = r2h.Hub(3, m_cycle, mb_parameters, 1, http_parameters)
susp_9 = r2h.Susp(parent_hub=hub_num_3, susp_id=9)

m_cycle.start()
