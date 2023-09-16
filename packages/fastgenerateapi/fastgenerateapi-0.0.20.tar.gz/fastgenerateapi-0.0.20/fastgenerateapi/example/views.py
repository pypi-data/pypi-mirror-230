from fastapi import Depends
from starlette.websockets import WebSocket
from tortoise import Tortoise

from fastgenerateapi import APIView, DeleteTreeView, GetTreeView, AsyncWebsocketConsumer, WebsocketView
from fastgenerateapi.deps import paginator_deps
from modules.example.models import StaffInfo, CompanyInfo
from modules.example.schemas import CompanyInfoRead, CompanyInfoCreate, TestSchema, ListTestSchema, StaffReadSchema


class CompanyView(APIView, DeleteTreeView, GetTreeView):
    model_class = CompanyInfo
    # schema = CompanyInfoRead
    # create_schema = CompanyInfoCreate

    async def view_get_list(self, paginator=Depends(paginator_deps())):

        return await self.pagination_data(queryset=self.queryset, fields=["id", "name"], paginator=paginator)


class StaffView(APIView):

    def __init__(self):
        self.model_class = StaffInfo
        self.order_by_fields = ["-created_at"]
        self.prefetch_related_fields = {"company": ["name"]}
        self.router_args = {
            # "view_get_staff_list": ListTestSchema
            "view_get_staff_list": TestSchema
        }
        self.get_all_schema = StaffReadSchema
        super().__init__()

    # async def view_get_staff_list(self, name: Optional[str] = None):
    #     conn = Tortoise.get_connection("default")
    #     # conn = Tortoise.get_connection("local")
    #     val = await conn.execute_query_dict("SELECT * FROM information_schema.columns WHERE TABLE_NAME = 'staffinfo'")
    #     # val = await conn.execute_query_dict("SELECT * FROM staffinfo")
    #     print(val)
    #     return self.success(data={"data_list": val})


class ChatView(WebsocketView):
    # redis_conn = default_redis
    tags = ["ws测试"]

    async def ws_wschat_pk(self, websocket: WebSocket, pk: str):
        """
        测试
        """
        await websocket.accept()
        while True:
            try:
                data = await websocket.receive_json()
                await websocket.send_text(f"接受到的消息是: {data}")
            except Exception:
                print(1)


class Consumer(AsyncWebsocketConsumer):
    # redis_conn = default_redis
    ...
