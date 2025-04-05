from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event
from gsuid_core.aps import scheduler
from gsuid_core.logger import logger
from gsuid_core.gss import gss
from .models import BiliMonitor
from .api import BiliAPI
from .config import conf

# 初始化服务
sv_bili = SV("B站直播监控", pm=2, priority=5)
bili_api = BiliAPI()

# 帮助命令
@sv_bili.on_fullmatch(('直播监控帮助', 'bilhelp'))
async def show_help(bot: Bot, ev: Event):
    help_msg = """【B站直播监控插件】
/添加监控 ➠ 绑定UID与群号
/删除监控 [UID] ➠ 移除监控
/监控列表 ➠ 查看当前监控"""
    await bot.send(help_msg)

# 添加监控（完整交互流程）
@sv_bili.on_command('添加监控')
async def add_monitor(bot: Bot, ev: Event):
    # Step 1: 获取UID
    await bot.send("请发送要监控的B站UID：")
    uid_ev = await bot.receive_resp()
    uid = uid_ev.text.strip()
    
    # Step 2: 验证UID有效性
    data = await bili_api.check_live(uid)
    if not data:
        return await bot.send("UID无效或查询失败！")
    
    # Step 3: 获取群号
    await bot.send("请发送接收通知的QQ群号：")
    group_ev = await bot.receive_resp()
    group_id = group_ev.text.strip()
    
    # 保存到数据库
    await BiliMonitor.add_data(
        uid=uid,
        group_id=group_id,
        last_status=data['liveStatus'] == 1
    )
    await bot.send(f"✅ 已添加对 {data['uname']} 的监控！")

# 定时检查任务
@scheduler.scheduled_job('interval', minutes=conf.get_config('interval').data)
async def check_job():
    logger.info("[BiliMonitor] 开始检查直播状态...")
    records = await BiliMonitor.get_all_data()
    for record in records:
        data = await bili_api.check_live(record.uid)
        if data and (data['liveStatus'] != record.last_status):
            # 更新状态
            await BiliMonitor.update_data(
                record.uid, 
                last_status=data['liveStatus'] == 1,
                last_check=datetime.now()
            )
            
            # 发送通知
            if data['liveStatus'] == 1:
                for bot_id in gss.active_bot:
                    bot = gss.active_bot[bot_id]
                    msg = (
                        f"[CQ:at,qq=all]\n"
                        f"📢 {data['uname']} 开始直播啦！\n"
                        f"标题：{data['title']}\n"
                        f"房间号：{data['roomid']}"
                    )
                    await bot.target_send(
                        msg, 
                        'group', 
                        record.group_id, 
                        bot_id,
                        at_sender=False
                    )