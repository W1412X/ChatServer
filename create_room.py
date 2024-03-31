import asyncio
import websockets
import random
import nest_asyncio
nest_asyncio.apply()
import subprocess
import threading
import time
import re
#receive the msg and send to all client
#the port list which can be connected
port_list=[i for i in range(8230,8280)]
#用于根据房间号分配房间
room_dict={}
#用于释放端口
port_dict={}
#the list to sign which port has already used
used_port_list=[False for i in range(8230,8280)]
threads=[]
#随机生成房间号
def generate_room_id(length):
    digits = "0123456789"
    random_string = ''.join(random.choice(digits) for _ in range(length))
    return random_string
#read port msg from file and update the msg in program and generate a free port
def generate_port():
    with open("ports_using.txt","r")as f:
        s=f.readline().split(" ")
        for i in range(10):
            if(str(i+8230)in s):
                used_port_list[i]=True
            else:
                used_port_list[i]=False
    for i in range(0,10):
        if(used_port_list[i]is False):
            used_port_list[i]=True
            return str(port_list[i])
    # if the port was all used then return none
    return "none"
async def receive_string(websocket, path):
    while True:
        message=await websocket.recv()
        if message.startswith("cr"):
            #get the url of video to be played
            split_string = message.split()
            video_url = split_string[1]
            print(video_url)
            # 产生房间号
            print("GET create command")
            room_id=generate_room_id(6)
            port=generate_port()
            print("TRY "+"create room : "+room_id+"    room port : "+port)
            #更新roomid信息
            room_dict[room_id]=[port,video_url]
            #update port msg
            port_dict[port]=room_id
            # 创建新的房间
            asyncio.create_task(create_room(room_id, port, video_url))
            await touch_html(video_url,room_id)
            await websocket.send("room_id " + room_id+" port "+port)
        elif message.startswith("id"):
            room_id=message.split()[1]
            # 发送对应房间号
            try:
                await websocket.send("room_id "+room_id+" port "+room_dict[room_id][0])
            except:
                await websocket.send("error")
        else:
            print("USELESS command")
            await websocket.send("USELESS command")
    async for message in websocket:
        websocket
        asyncio.create_task(deal_msg(websocket,message))
async def main():
    async with websockets.serve(receive_string, "0.0.0.0","8627"):
        await asyncio.Future()  # 挂起，直到服务器关闭

async def create_room(room_id, port, video_url):
    print(2)
    #await asyncio.sleep(5)
    await create_room_op(room_id, port, video_url)
    print(3)

async def create_room_op(room_id, port, video_url):
    # 启动子进程
    process = await asyncio.create_subprocess_exec(
        '/home/wangxv/test_image/venv/bin/python', '/home/wangxv/test_image/test_watch_together/son_watch.py',
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    # 发送输入到子进程
    input_str = port+" "+room_id+" "+video_url
    process.stdin.write(input_str.encode())
    await process.stdin.drain()
    process.stdin.close()
    
    # 读取子进程的标准输出和标准错误输出
    output, error = await asyncio.gather(
        process.stdout.readline(),
        process.stderr.readline())
    
    # 等待子进程结束
    await process.wait()
    
    # 处理输出结果
    output_str = output.decode().strip()
    error_str = error.decode().strip()
    
    return output_str, error_str


async def touch_html(url,room_id):
    print("create new html")
    process = await asyncio.create_subprocess_exec(
        'touch',
        '/var/www/chat_app_update/watch_html/'+room_id+'.html',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
        # 读取子进程的标准输出和标准错误输出
    output, error = await asyncio.gather(
        process.stdout.readline(),
        process.stderr.readline())
    # 等待子进程结束
    await process.wait()
    print("cp op finish")
    # 处理输出结果
    output_str = output.decode().strip()
    error_str = error.decode().strip()
    with open("/var/www/chat_app_update/watch_html/origin.html","r")as f:
        s=f.read()
        with open('/var/www/chat_app_update/watch_html/'+room_id+'.html',"w")as f1:
            f1.write(html_with_url(s,url))
    return  output_str,error_str
def html_with_url(html,url):
    # 定义正则表达式
    pattern = r'(?<=source": ")[^"]+'
    # 使用正则表达式查找需要替换的URL
    new_html = re.sub(pattern, url, html)
    return new_html
asyncio.run(main())





