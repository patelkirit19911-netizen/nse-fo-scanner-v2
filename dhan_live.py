from dhanhq import dhanhq
import os

CLIENT_ID = os.getenv("DHAN_CLIENT_ID")
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

dhan = dhanhq(CLIENT_ID, ACCESS_TOKEN)


def test_connection():
    return "Dhan API Connected Successfully"
