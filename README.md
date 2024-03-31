# 聊天室服务端的一个简单实现
> 使用python与websocket实现
> 本服务端代码是在写一个远程同步观看并聊天的功能实现的，所以如果只是想要聊天的话只需要保留核心逻辑即可
## 代码逻辑
  - 每一个端口号作为一个房间
  - 对一定时间内没有用户的房间进行清除，释放端口号和服务器资源
## 代码运行
- 需要修改一些代码内容来适配你自己的服务器
  - create_room.py中在创建子进程运行son_watch.py中，你需要修改python的路径
  - 对应开放的端口号根据情况进行改变
- **更多的修改可以通过阅读代码来理解**
