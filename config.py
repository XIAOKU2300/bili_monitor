from gsuid_core.utils.plugins_config import GsConfig
from gsuid_core.data_store import get_res_path

conf = GsConfig(
    'BiliMonitor',
    get_res_path('bili_monitor') / 'config.json',
    {'interval': ('检查间隔(分钟)', '直播状态检查频率', 5)}
)