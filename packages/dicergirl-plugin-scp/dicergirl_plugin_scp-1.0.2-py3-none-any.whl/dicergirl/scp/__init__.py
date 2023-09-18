from .agent import Agent
from .nbhandlers import commands
from .scpcards import scp_cards, scp_cache_cards
from .attributes import scp_attrs_dict
from .scputils import scp_at, scp_dam, scp_ra, scp_en
from dicergirl.utils.messages import regist

regist(
    "scp",
    """.scp Optional[begin|reset|deal|upgrade]  完成 SCP 人物卡作成
  begin: 展示基金会基本介绍
    .scp begin
  reset Optional[hp|p|enp|rep|card]: 重置人物卡
  - 无参数的`.scp reset`指令会重置人物所有附加属性, 包括生命值、熟练值、激励点和声望, 但不会改变已升级的技能和特工等级、类别.
    hp: 重置人物卡生命值为最大生命值
      .scp reset hp
    p: 重置人物卡熟练值为最大熟练值
      .scp reset p
    enp: 重置人物卡激励点为最大激励点
      .scp reset enp
    rep: 重置人物卡声望为最大声望
      .scp reset rep
    card: 重置人物卡(请谨慎使用)
    `.scp reset card`指令会重置人物卡为初始状态, 请谨慎使用.
      .scp reset card
  deal Optional[str: weapon]  装备购买
  - 无参数的`.scp deal`指令会给出当前特工允许的购买的武器.
    weapon: 武器名称
      .scp deal 燃烧瓶  购买一个燃烧瓶
  upgrade (up) [str: name] [int: level]  升级技能
    name: 技能名称
    level: 需要提升到的等级
      .scp up 计算机 5  将计算机提升到 5 级.""",
    alias=["scp", "基金会"]
)

scp_cards.load()

__version__ = "1.0.2"

__type__ = "plugin"
__charactor__ = Agent
__name__ = "scp"
__cname__ = "特工"
__cards__ = scp_cards
__cache__ = scp_cache_cards
__nbhandler__ = nbhandlers
__nbcommands__ = commands
__commands__ = {
    "at": scp_at,
    "dam": scp_dam,
    "ra": scp_ra,
    "en": scp_en
}
__baseattrs__ = scp_attrs_dict
__description__ = "SCP 模式是基于SCP基金会(SCP Foundation) 设定的 TRPG 跑团模式."