BROKER = "127.0.0.1"
PORT = 1883
PUBLIC_KEY_PATH = "./keys/publickey.crt"
PRIVATE_KEY_PATH = "./keys/privatekey.pem"

PUBLIC_KEY = open(PUBLIC_KEY_PATH, "rb").read()
PRIVATE_KEY = open(PRIVATE_KEY_PATH, "rb").read()
