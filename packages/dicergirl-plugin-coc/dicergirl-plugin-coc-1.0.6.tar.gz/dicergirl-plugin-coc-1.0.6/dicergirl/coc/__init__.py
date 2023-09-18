from .investigator import Investigator
from .nbhandlers import commands
from .coccards import coc_cards, coc_cache_cards, coc_attrs_dict
from .cocutils import coc_at, coc_dam, coc_ra, coc_en
from dicergirl.utils.messages import regist

regist(
    "coc",
    """.coc [age] [roll] [name] [sex] Optioanl[cache]  完成 COC 人物作成
  age: 调查员年龄
  roll: 天命次数
  name: 调查员姓名
  sex: 调查员性别
  - 以上参数均可缺省
    .coc age 20 roll 5 name 欧若可 sex 女  进行5次姓名为`欧若可`的20岁女性调查员天命
  cache: 展示已天命的人物卡
    .coc cache
  - 值得注意的是, 调查员的年龄与调查员的外貌、教育值相关.""",
    alias=["coc", "克苏鲁"]
)
regist(
    "sc",
    """.sc [int: success]/[int: failure] Optional[int: SAN]  COC 疯狂检定
  success: 判定成功降低san值, 支持aDb语法(a、b与x为数字)
  failure: 判定失败降低san值, 支持aDb语法(a、b与x为数字)
  SAN: 指定检定的 SAN 值(可选参数)
  - 缺省该参数则会自动使用该用户已保存的人物卡数据.""",
    alias=["sc", "sancheck", "疯狂检定"]
)
regist(
    "ti",
    """.ti 对调查员进行临时疯狂检定""",
    alias=["ti", "临时疯狂", "临时疯狂检定"]
)
regist(
    "li",
    """.li  对调查员进行总结疯狂检定""",
    alias=["li", "总结疯狂", "总结疯狂检定"]
)

coc_cards.load()

__version__ = "1.0.6"

__type__ = "plugin"
__charactor__ = Investigator
__name__ = "coc"
__cname__ = "调查员"
__cards__ = coc_cards
__cache__ = coc_cache_cards
__nbhandler__ = nbhandlers
__nbcommands__ = commands
__commands__ = {
    "at": coc_at,
    "dam": coc_dam,
    "ra": coc_ra,
    "en": coc_en
}
__baseattrs__ = coc_attrs_dict
__description__ = "COC 模式是以H.P.洛夫克拉夫特《克苏鲁的呼唤(Call of Cthulhu)》为背景的 TRPG 跑团模式."