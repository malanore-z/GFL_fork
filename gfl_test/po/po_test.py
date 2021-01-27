from typing import *

from gfl_test.po.po import PlainObject


class PlainA(PlainObject):

    a: int          # 冒号后面是类型声明
    b: str = "1"    # 等号后面是默认值


class PlainB(PlainObject):

    c: List[int]
    d: Dict[str, PlainA]
    e: Any      # Any表示任意类型（json模块支持的类型）


class PlainC(PlainA):

    f: List[Dict[int, PlainA]]
    g: Set[float] = {1.0, 0.1, 2.3}


class PlainD(PlainC):

    h: Tuple[PlainB]
    i: Dict[str, Any]
