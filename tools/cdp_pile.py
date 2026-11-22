#!/usr/bin/env python3
"""Diagnostic navigateur : met en pause la page du jeu (Chrome lancé avec --remote-debugging-port)
et affiche la pile de chaque fil (page + workers). Usage : cdp_pile.py [port] [attente_s]"""
import json, sys, time, urllib.request
import websocket

port = int(sys.argv[1]) if len(sys.argv) > 1 else 9333
wait = float(sys.argv[2]) if len(sys.argv) > 2 else 0
time.sleep(wait)
pages = [t for t in json.load(urllib.request.urlopen(f'http://127.0.0.1:{port}/json')) if t['type'] == 'page']
ws = websocket.create_connection(pages[0]['webSocketDebuggerUrl'], timeout=60, suppress_origin=True)
n = 0
def send(method, params=None, session=None):
    global n
    n += 1
    m = {'id': n, 'method': method, 'params': params or {}}
    if session: m['sessionId'] = session
    ws.send(json.dumps(m))
    return n

def pile(session, label):
    send('Debugger.enable', session=session)
    send('Debugger.pause', session=session)
    t0 = time.time()
    while time.time() - t0 < 20:
        m = json.loads(ws.recv())
        if m.get('method') == 'Debugger.paused' and m.get('sessionId') == session:
            print(f'--- {label}')
            for f in m['params']['callFrames'][:25]:
                print('   ', f['functionName'])
            send('Debugger.resume', session=session)
            return
    print(f'--- {label} : pas de pause (fil inactif ?)')

send('Target.setAutoAttach', {'autoAttach': True, 'waitForDebuggerOnStart': False, 'flatten': True})
sessions = []
t0 = time.time()
while time.time() - t0 < 3:
    try:
        ws.settimeout(1)
        m = json.loads(ws.recv())
    except Exception:
        continue
    if m.get('method') == 'Target.attachedToTarget':
        sessions.append((m['params']['sessionId'], m['params']['targetInfo']['type'] + ' ' + m['params']['targetInfo']['url'][-40:]))
ws.settimeout(60)
pile(None, 'page (fil principal)')
for sid, lab in sessions:
    pile(sid, lab)
