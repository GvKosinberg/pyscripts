def read_real(fake_inc):
    # коды типов устройств и соответствующие им ключи
    __types = {
                '0': "SNC_T_AIR",
                '3': "SNC_LUMI",
                '3378': "ENCLAVE"
    }
    __errors = {
                'SNC_T_AIR': [0x7FF, 0x00,],
                'SNC_LUMI': [0xFFFF, 0x00,],
    }
    r_type = "-"
    r_name = "-"
    d_rssi = 0
    d_bat = 0
    d_packid = 0
    # Итоговые данные
    data_sum = 0

    # TEMP: flag
    flag_inc = False

    # Ожидание сообщения
    inc_data = fake_inc

    # Проверка данных (если данные не пришли type(inc_data!=None))
    # если ответ пришел, данные записываются в кортеж
    if type(inc_data) == tuple:
        try:
            # адрес устройства
            d_addr = inc_data[0][1]
            # код типа устройства
            d_type = str(inc_data[0][2])
            # Уровень сигнала
            d_rssi = inc_data[1]
            # Номер пакета
            d_packid = inc_data[0][3]
            # Уровень батареи
            d_bat = inc_data[0][4]

            # Младший байт данных
            data_lb = inc_data[0][5]
            # Старший байт данных
            data_sb = inc_data[0][6] << 8
        except:
            log.error("Bad pack received: %s" % inc_data)
        # Проверка на наличие кода типа в списке
        # TODO: убрать адрес левого датчика
        if (d_type in __types) and (d_addr != 0xcd):
            # Присвоение ключа по коду
            r_type = __types[d_type]
            # Присвоение имени (string)
            r_name = str(d_addr)
            # TEMP: flagg
            flag_inc = True

            if (data_lb | data_sb) in __errors[r_type]:
                data_sum = "Ошибка датчика"
            else:
                # Преобразования данных для различных типов датчиков
                if (r_type == "SNC_T_AIR"):
                    d_s = (data_lb | data_sb) & 0xFFF
                    data_sum = str(d_s/10.00) + " °C"
                elif (r_type == "SNC_LUMI"):
                    data_sum = str(data_lb | data_sb) + " люкс"

    return data_sum
