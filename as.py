import random

def sumfux():
    __types_sncs = {
                'sncs': ["sncs/temp/air", "sncs/temp/water", "sncs/temp/heater",
                        "sncs/lumi", "sncs/humi"],
                'doors': ["sncs/doors"],
                'warns': ["warn/leak", "warn/smoke", "warn/flame"],
                'pres': ["pres/pres", "pres/motion"]
                }
    __types_cntrs = {
                'cntrs': ["cntrs"]
                }
    __types_devices = {
                'relays': ["devices/relays"],
                'dimmers': ["devices/dimmers/crane",
                "devices/dimmers/curt", "devices/dimmers/stepper",
                "devices/dimmers/trmrl"]
                }
    print(__types_sncs.values())

if __name__ == "__main__":
    sumfux()
