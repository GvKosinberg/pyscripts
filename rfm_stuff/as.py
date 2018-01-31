class Device:
    def __init__(self, d_type, name, rfm, mqtt_c):
        __types_devices = {
                        'RELAY': "devices/relays/",
                        'DIM_CRANE': "devices/dimmers/crane/",
                        'DIM_CURT': "devices/dimmers/curt/",
                        'DIM_STEP': "devices/dimmers/stepper/",
                        'DIM_TRMRL': "devices/dimmers/trmrl/",
        }
        if d_type in __types_devices:
            self.rfm = rfm
            self.mqtt_c = mqtt_c
            self.d_type = d_type
            self.name = name
            self.topic = "oh/"+__types_devices[d_type]+name
            self.mqtt_c.subscribe(self.topic)
            self.mqtt_c.message_callback_add(self.topic, self.write2device)
        else:
            log.error("Invalid device type: %s", %d_type)

    #TEMP: place for rand fux
    def write2device(self, clnt, usrdt, msg):
        log.debug("SENT from: %s NUDES: %s" %(msg.topic, msg.payload))
        if self.d_type=='RELAY':
            log.debug("AMA RELAY: %s, VAL: %s" %(self.name, msg.payload))
        else:
            log.debug("AMA: %s, VAL: %s" %(self.d_type, msg.payload))

class Sencor:
    def __init__(self, d_type, name, rfm, mqtt_c, timeout):
        __types_sncs = {
                        'SNC_T_AIR': "oh/sncs/temp/air/",
                        'SNC_T_WATER': "oh/sncs/temp/water/",
                        'SNC_T_HEATER': "oh/sncs/temp/heater/",
                        'SNC_HUMI': "oh/sncs/humi/",
                        'SNC_LUMI': "oh/sncs/lumi/",
                        'SNC_DOOR': "oh/sncs/doors",
                        'WARN_LEAK': "oh/warn/leak/",
                        'WARN_SMOKE': "oh/warn/smoke/",
                        'WARN_FLAME': "oh/warn/flame/",
                        'PRES_PRES': "oh/pres/pres/",
                        'PRES_MOT': "oh/pres/motion/",
                        'CNTR': "oh/cntrs/"
        }
        if d_type in __types_sencors:
            self.rfm = rfm
            self.mqtt_c = mqtt_c
            self.d_type = d_type
            self.name = name
            self.topic = __types_sencors[d_type]+name
            self.timeout = timeout
        else:
            log.error("Invalid device type: %s", %d_type)

    """
        Метод проверки timeout'а ответа
    """
    def check_timeout(self):
        razn = time.time() - self.last_responce
        if razn > self.d_timeout:
            self.data = "-"
        log.info("Device: %s: time between responces: %s"
                % ((self.d_type+"/"+self.name), razn))

    """
        Метод записи полученного значения датчика в брокер
    """
    def write2mqtt(self):
        mqtt_topic = self.topic

        self.check_timeout()

        #TEMP: random data
        self.data = self.get_random_state()

        mqtt_val = self.data
        self.mqtt_c.publish(mqtt_topic, mqtt_val)

        log.debug('Obj: %s: val: %s ' %(mqtt_topic, mqtt_val))
        #.print('Last responce: %s' %str(self.last_responce))


    #TEMP: random generator for tests
    def get_random_state(self):
        __val_float_limits = {
                        "SNC_T_AIR": [19.00, 25.00],
                        "SNC_T_WATER": [5.00, 22.00],
                        "SNC_T_HEATER": [50.00, 100.00],
                        "SNC_LUMI": [150.00, 300.00],
                    }
        __val_int_limits = {
                        "CNTR": [100, 500],
                        "SNC_HUMI": [0, 100],
        }
        __definitions = {
                        "SNC_DOOR": ["OPEN", "CLOSED"],
                         "PRES_PRES": ["HIGH", "LOW"],
                         "PRES_MOT": ["HIGH", "LOW"],
                         "WARN_LEAK": ["HIGH", "LOW"],
                         "WARN_SMOKE": ["HIGH", "LOW"],
                         "WARN_FLAME": ["HIGH", "LOW"]
                 }
        if d_type in __definitions:
            state = random.randint(0,1)
            out = __definitions[self.d_type][state]
        elif d_type in __val_float_limits:
            out = random.uniform(__val_float_limits[self.d_type][0],
                                __val_float_limits[self.d_type][1])
        elif d_type in __val_int_limits:
            out = random.randint(__val_int_limits[self.d_type][0],
                                __val_int_limits[self.d_type][1])

        self.last_responce = time.time()
        return out
