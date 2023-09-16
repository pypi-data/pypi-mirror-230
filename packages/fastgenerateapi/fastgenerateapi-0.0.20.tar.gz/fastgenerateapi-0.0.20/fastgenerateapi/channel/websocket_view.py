import aioredis

from fastgenerateapi.api_view.base_view import BaseView


class WebsocketView(BaseView):
    redis_conn: aioredis.Redis


