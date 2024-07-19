import websocket
import _thread
import time
import rel
import json
import httpx
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)

def send_message(ws, message):
    ws.send(json.dumps([json.dumps(message)]))

def on_message(ws, message):
    decoded = None
    try: 
      decoded = json.loads(json.loads(message[1:])[0])
      logging.debug(decoded)
    except Exception as e:
      logging.error(f"Error decoding message: {e} {message}")

    if decoded:
      if decoded["msg"] == "ping":
          send_message(ws, {"msg":"pong"})
      elif decoded["msg"] == "added" and decoded["collection"] == "sales":
          logging.info("Got new sale")
          delta = datetime.now() - datetime.fromtimestamp(int(decoded["fields"]["timestamp"]["$date"]) / 1000)
          duration_in_s = delta.total_seconds() 

          if(duration_in_s < 3600):
            resp = httpx.post("http://vfd.display.crablab.uk/message", data={"message": f"Kaching! Sold {len(decoded['fields']['products'])} item for {decoded['fields']['amount']} HAX", "effect": "chase"})
            logging.info(resp.text)

def on_error(ws, error):
    logging.error(error)

def on_close(ws, close_status_code, close_msg):
    logging.error("### closed ###")
    exit()

def on_open(ws):
    logging.info("Opened connection")

def on_ping(ws, data):
    logging.info("Ping received")

if __name__ == "__main__":
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp("wss://pos.wip.bar/sockjs/253/ewtuljoo/websocket",
                              on_open=on_open,
                              on_message=on_message,
                              on_error=on_error,
                              on_close=on_close,
                              on_ping=on_ping)

    ws.run_forever(dispatcher=rel, reconnect=5, ping_interval=60, ping_timeout=10)  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
    send_message(ws, {"msg":"connect","version":"1","support":["1","pre2","pre1"]})
    send_message(ws, {"msg":"method","id":"1","method":"GALAXY_APP_VERSION_ID","params":[]})
    send_message(ws, {"msg":"sub","id":"vGcwunwSor6vakiYi","name":"meteor.loginServiceConfiguration","params":[]})
    send_message(ws, {"msg":"sub","id":"GjFjSFnxuhqr36cDX","name":"meteor_autoupdate_clientVersions","params":[]})
    # send_message(ws, {"msg":"sub","id":"kZMhCKboQ2REPtido","name":"products","params":[]})
    send_message(ws, {"msg":"sub","id": "ashdkjah67y", "name":"sales","params":[{}]})

    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()