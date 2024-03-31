import websockets
import asyncio 


class WatchChat:
    def __init__(self, host, port,room_id,video_url):
        self.host = host
        self.port = port
        self.time_set={}
        self.room_id=room_id
        self.video_url=video_url
        self.clients = set()
    async def handle_client(self, websocket, path):
        # 存储连接的客户端
        self.clients.add(websocket)
        try:
            await self.on_connect(websocket)
            async for message in websocket:
                await self.on_message(websocket, message)
        finally:
            # 客户端断开连接时从集合中移除
            self.clients.remove(websocket)
            await self.on_disconnect(websocket)
    async def on_connect(self, websocket):
        # 在客户端连接时触发的回调函数
        print(f"New client connected: {websocket.remote_address}")
    
    async def on_message(self, websocket, message):
        # 在接收到客户端消息时触发的回调函数
        print(f"Received from {websocket.remote_address}: {message}")
        if message.startswith("time"):#接收到的消息时间格式进行特殊处理
            second=message.split()[1]
            min_progress=999999999
            self.time_set[websocket]=int(second)
            for client in self.clients:
                try:
                    if min_progress>self.time_set[client]:
                        min_progress=self.time_set[client]
                except:
                    pass
            for client in self.clients:
                try:
                    if self.time_set[client]-min_progress>20:
                        await self.send_to_all("ad "+str(min_progress))
                        break
                except:
                    pass
        else:
            await self.send_to_all(message)  # 将消息发送给所有客户端
    
    async def on_disconnect(self, websocket):
        # 在客户端断开连接时触发的回调函数
        print(f"Client disconnected: {websocket.remote_address}")
    
    async def send_to_all(self, message):
        print("TRY send to all")
        print("Client num"+str(len(self.clients)))
        # 发送消息给所有客户端
        for client in self.clients:
            await client.send(message)
    
    async def check_clients(self):
        while True:
            await asyncio.sleep(60)  # 每隔30秒检查一次
            if len(self.clients) == 0:
                print("No clients, stopping server...")
                #update the file
                remove_port_from_file("ports_using.txt",self.port)
                exit("no connection")
                self.server.close()  # 关闭server
                await self.server.wait_closed()  # 等待server关闭
                break
    
    def start(self):
        self.server = websockets.serve(self.handle_client, self.host, self.port)
        asyncio.get_event_loop().create_task(self.check_clients())  # 创建定时任务
        asyncio.get_event_loop().run_until_complete(self.server)
        asyncio.get_event_loop().run_forever()
def remove_port_from_file(filename, port):
    try:
        with open(filename, "r") as file:
            ports = file.readline().split()
        
        if str(port) in ports:
            ports.remove(str(port))

        with open(filename, "w") as file:
            file.write(" ".join(ports))
        
        print(f"Port {port} removed from {filename} successfully.")
    except IOError as e:
        print(f"Error occurred while removing port {port} from {filename}: {e}")
def add_port_to_file(filename, port):
    try:
        with open(filename, "a") as file:
            file.write(str(port) + " ")
        print(f"Port {port} added to {filename} successfully.")
    except IOError as e:
        print(f"Error occurred while adding port {port} to {filename}: {e}")
s=input()
t=s.split(" ")
add_port_to_file("ports_using.txt",t[0])
WatchChat("0.0.0.0",t[0],t[1],t[2]).start()
