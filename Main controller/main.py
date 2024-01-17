from gpio import GPIO_init, clean_gpio
from application import run_covi
from conn import conn_close, conn_init

if __name__ == '__main__':
    GPIO_init()
    conn_init()
    status = 'waiting for plate'
    try:
        run_covi(status)
    except KeyboardInterrupt:
        clean_gpio()
        conn_close()
    clean_gpio()
