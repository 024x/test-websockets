import os
import json
try:
    from fastapi import FastAPI, WebSocket
    from typing import Dict
except ImportError:
    os.system("pip install fastapi 'uvicorn[standard]'")
    from fastapi import FastAPI, WebSocket
    from typing import Dictacs

app = router = FastAPI()
o_d = {'M1KOOMRRNB': 'SATYA', '37DMZL7V04': 'NAVEEN', 'ZYXO069NT5': 'PLUTO', '81IYLCIU79': 'SAFONE', '045RSCC9UP': 'BHAVANA', 'PUJMW4H2K3': 'MANIDEEP', 'EIFJEESSN0': 'TARSH', '44K2KGYFNT': 'AARYAN'}

rd = {'SATYA': 'M1KOOMRRNB', 'NAVEEN': '37DMZL7V04', 'PLUTO': 'ZYXO069NT5', 'SAFONE': '81IYLCIU79', 'BHAVANA': '045RSCC9UP', 'MANIDEEP': 'PUJMW4H2K3', 'TARSH': 'EIFJEESSN0', 'AARYAN': '44K2KGYFNT'}

active_connections: Dict[str, list] = {}


@router.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str, device: str = None):
    if o_d.get(username) is None:
        return
    if username not in active_connections:
        active_connections[username] = []
    await websocket.accept()
    active_connections[username].append({"websocket": websocket, "device": device})
    connected_devices = len(active_connections[username])
    message = f"Welcome, {o_d.get(username)}!"
    await websocket.send_text(json.dumps({"type":"greeting","message": message}))
    for connection in active_connections[username]:
        await connection["websocket"].send_text(json.dumps({"type":"connection","connected": f"{device}"}))
        await connection["websocket"].send_text(json.dumps({"type":"conn_dev","conn_dev": connected_devices}))
    try:
        while True:
            data = await websocket.receive_text()
            if data == "conn_dev":
                await websocket.send_text(json.dumps({"type":"conn_dev","conn_dev": len(active_connections[username])}))
            elif data == "dev_list":
                devices = [{"device": item["device"], "name": o_d.get(username)} for item in active_connections[username]]
                await websocket.send_text(json.dumps({"type":"dev_list","devices": devices}))
            else:
                for connection in active_connections[username]:
                    if connection["websocket"] != websocket:
                        await connection["websocket"].send_text(json.dumps({"type":"message","device": device, "data": data}))
    except Exception as e_x:
        
        for connection in active_connections[username]:
            try:
                await connection["websocket"].send_text(json.dumps({"type":"disconnect","disconnected": f"{device}"}))
            except:
                pass
        
    
        print(e_x)
        active_connections[username] = [c for c in active_connections[username] if c["websocket"] != websocket]
        try:
            await websocket.close()
        except:
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
