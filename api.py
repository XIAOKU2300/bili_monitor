import httpx
from .models import BiliMonitor

class BiliAPI:
    def __init__(self):
        self.client = httpx.AsyncClient()
    
    async def check_live(self, uid: str):
        try:
            resp = await self.client.get(
                f"https://api.live.bilibili.com/room/v1/Room/getRoomInfoOld?mid={uid}",
                timeout=10
            )
            data = resp.json()
            return data.get('data', {}) if data['code'] == 0 else None
        except Exception:
            return None