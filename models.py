from sqlmodel import Field
from datetime import datetime
from gsuid_core.utils.database.base_models import BaseModel

class BiliMonitor(BaseModel, table=True):
    uid: str = Field(title="B站UID", primary_key=True)
    group_id: str = Field(title="QQ群号")
    last_status: bool = Field(default=False)
    last_check: datetime = Field(default_factory=datetime.now)