import random

def get_random_state(fmt):
    state = random.randint(0,1)
    defas = {"OC": ["OPEN", "CLOSED"],
             "OO": ["ON", "OFF"],
             "HL": ["HIGH", "LOW"]}
    out = defas[fmt][state]

if __name__ == "__main__":
    get_random_state("OO")
