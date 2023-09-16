import _ctypes
from typing import List, Union

import aioredis
from starlette.endpoints import WebSocketEndpoint


class AsyncWebsocketConsumer(WebSocketEndpoint):
    redis_conn: aioredis.Redis
    encoding = "json"
    group_key = "fastapi_websocket_group"

    # 连接 存储
    async def on_connect(self, websocket):
        await websocket.accept()

        # 用户输入名称
        group_id = websocket.path_params.get("group_id")
        user_id = websocket.query_params.get("user_id")
        await self.group_add(websocket, group_id, user_id)
        await self.group_send(websocket, {"msg": f"{user_id}-加入了聊天室"})

    # 收发
    async def on_receive(self, websocket, data):
        await self.group_send(websocket, data)

    # 断开 删除
    async def on_disconnect(self, websocket, close_code):
        if self.user_key:
            await self.redis_conn.hdel(self.group_key, self.user_key)
        pass

    async def group_add(self, websocket, group_key, user_key):
        if not self.redis_conn:
            await self.error(websocket, code=500, msg="redis未设置")
        if group_key:
            self.group_key = group_key
        if not user_key:
            await self.error(websocket, code=422, msg="未获取到用户信息")
        self.user_key = user_key

        await self.redis_conn.hset(self.group_key, self.user_key, id(websocket))

    async def group_send(self, websocket, data, code=200, exclude: Union[bool, list] = True):
        """
        用于内部视图发送消息
        :param websocket:
        :param data: 发送的数据
        :param code: 状态码
        :param exclude: 默认True排除自己；[int] 时可选排除其他人
        :return:
        """
        # 先循环 告诉之前的用户有新用户加入了
        result = await self.redis_conn.hgetall(self.group_key)
        if type(exclude) == bool:
            exclude = [id(websocket)] if exclude else []
        for key, value in result.items():
            if int(value) in exclude:
                continue
            try:
                websocket = _ctypes.PyObj_FromPtr(int(value))
            except Exception:
                await self.redis_conn.hdel(self.group_key, int(value))
                continue
            await websocket.send_json({
                "code": code,
                "from": self.user_key,
                # "message": "请求成功",
                "data": data
            })

    @staticmethod
    async def error(websocket, code=500, msg="请求失败"):
        await websocket.send_json({
            "code": code,
            "message": msg,
        })
        await websocket.close()

    @classmethod
    async def cls_group_send(cls, group_key, data, code=200, user_key=None, exclude: Union[List[int], bool] = True):
        """
        用于外部视图发送消息
        :param group_key: 组对应键值
        :param data: 发送的数据
        :param code: 状态码
        :param user_key: 当前用户的对应键
        :param exclude: 当传入 user_key 时默认排除自己；[int] 时可选排除其他人
        :return:
        """
        result = await cls.redis_conn.hgetall(group_key)
        if type(exclude) == bool:
            exclude = [id(user_key)] if user_key and exclude else []
        for key, value in result.items():
            if int(value) in exclude:
                continue
            try:
                websocket = _ctypes.PyObj_FromPtr(int(value))
            except Exception:
                await cls.redis_conn.hdel(group_key, int(value))
                continue
            await websocket.send_json({
                "code": code,
                "from": user_key,
                # "message": "请求成功",
                "data": data
            })



