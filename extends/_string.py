import random
from sonyflake import SonyFlake

SF = SonyFlake()
RANDOM = random.SystemRandom()

def gen_snowflake_id():
    return str(SF.next_id())

if __name__ == '__main__':
    print(gen_snowflake_id())
