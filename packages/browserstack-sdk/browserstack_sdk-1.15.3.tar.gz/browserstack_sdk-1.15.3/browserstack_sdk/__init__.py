# coding: UTF-8
import sys
bstack1l1l111ll_opy_ = sys.version_info [0] == 2
bstack1l11ll11_opy_ = 2048
bstack1111ll1ll_opy_ = 7
def bstack111lll1l_opy_ (bstack1llll_opy_):
    global bstack1ll11l1ll_opy_
    bstack1lll1l_opy_ = ord (bstack1llll_opy_ [-1])
    bstack1llll1ll1_opy_ = bstack1llll_opy_ [:-1]
    bstack11llll_opy_ = bstack1lll1l_opy_ % len (bstack1llll1ll1_opy_)
    bstack11l1l11ll_opy_ = bstack1llll1ll1_opy_ [:bstack11llll_opy_] + bstack1llll1ll1_opy_ [bstack11llll_opy_:]
    if bstack1l1l111ll_opy_:
        bstack111111l_opy_ = unicode () .join ([unichr (ord (char) - bstack1l11ll11_opy_ - (bstack1111lll_opy_ + bstack1lll1l_opy_) % bstack1111ll1ll_opy_) for bstack1111lll_opy_, char in enumerate (bstack11l1l11ll_opy_)])
    else:
        bstack111111l_opy_ = str () .join ([chr (ord (char) - bstack1l11ll11_opy_ - (bstack1111lll_opy_ + bstack1lll1l_opy_) % bstack1111ll1ll_opy_) for bstack1111lll_opy_, char in enumerate (bstack11l1l11ll_opy_)])
    return eval (bstack111111l_opy_)
import atexit
import os
import signal
import sys
import time
import yaml
import requests
import logging
import threading
import socket
import datetime
import string
import random
import json
import collections.abc
import re
import multiprocessing
import traceback
import copy
from multiprocessing import Pool
from packaging import version
from browserstack.local import Local
from urllib.parse import urlparse
bstack1llll1l11_opy_ = {
	bstack111lll1l_opy_ (u"ࠫࡺࡹࡥࡳࡐࡤࡱࡪ࠭ࠀ"): bstack111lll1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡺࡹࡥࡳࠩࠁ"),
  bstack111lll1l_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩࠂ"): bstack111lll1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴࡫ࡦࡻࠪࠃ"),
  bstack111lll1l_opy_ (u"ࠨࡱࡶ࡚ࡪࡸࡳࡪࡱࡱࠫࠄ"): bstack111lll1l_opy_ (u"ࠩࡲࡷࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ࠅ"),
  bstack111lll1l_opy_ (u"ࠪࡹࡸ࡫ࡗ࠴ࡅࠪࠆ"): bstack111lll1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡹࡸ࡫࡟ࡸ࠵ࡦࠫࠇ"),
  bstack111lll1l_opy_ (u"ࠬࡶࡲࡰ࡬ࡨࡧࡹࡔࡡ࡮ࡧࠪࠈ"): bstack111lll1l_opy_ (u"࠭ࡰࡳࡱ࡭ࡩࡨࡺࠧࠉ"),
  bstack111lll1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡔࡡ࡮ࡧࠪࠊ"): bstack111lll1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࠧࠋ"),
  bstack111lll1l_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧࠌ"): bstack111lll1l_opy_ (u"ࠪࡲࡦࡳࡥࠨࠍ"),
  bstack111lll1l_opy_ (u"ࠫࡩ࡫ࡢࡶࡩࠪࠎ"): bstack111lll1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡩ࡫ࡢࡶࡩࠪࠏ"),
  bstack111lll1l_opy_ (u"࠭ࡣࡰࡰࡶࡳࡱ࡫ࡌࡰࡩࡶࠫࠐ"): bstack111lll1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰࡰࡶࡳࡱ࡫ࠧࠑ"),
  bstack111lll1l_opy_ (u"ࠨࡰࡨࡸࡼࡵࡲ࡬ࡎࡲ࡫ࡸ࠭ࠒ"): bstack111lll1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡰࡨࡸࡼࡵࡲ࡬ࡎࡲ࡫ࡸ࠭ࠓ"),
  bstack111lll1l_opy_ (u"ࠪࡥࡵࡶࡩࡶ࡯ࡏࡳ࡬ࡹࠧࠔ"): bstack111lll1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡥࡵࡶࡩࡶ࡯ࡏࡳ࡬ࡹࠧࠕ"),
  bstack111lll1l_opy_ (u"ࠬࡼࡩࡥࡧࡲࠫࠖ"): bstack111lll1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡼࡩࡥࡧࡲࠫࠗ"),
  bstack111lll1l_opy_ (u"ࠧࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࡎࡲ࡫ࡸ࠭࠘"): bstack111lll1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࡎࡲ࡫ࡸ࠭࠙"),
  bstack111lll1l_opy_ (u"ࠩࡷࡩࡱ࡫࡭ࡦࡶࡵࡽࡑࡵࡧࡴࠩࠚ"): bstack111lll1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡷࡩࡱ࡫࡭ࡦࡶࡵࡽࡑࡵࡧࡴࠩࠛ"),
  bstack111lll1l_opy_ (u"ࠫ࡬࡫࡯ࡍࡱࡦࡥࡹ࡯࡯࡯ࠩࠜ"): bstack111lll1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲࡬࡫࡯ࡍࡱࡦࡥࡹ࡯࡯࡯ࠩࠝ"),
  bstack111lll1l_opy_ (u"࠭ࡴࡪ࡯ࡨࡾࡴࡴࡥࠨࠞ"): bstack111lll1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡴࡪ࡯ࡨࡾࡴࡴࡥࠨࠟ"),
  bstack111lll1l_opy_ (u"ࠨࡵࡨࡰࡪࡴࡩࡶ࡯࡙ࡩࡷࡹࡩࡰࡰࠪࠠ"): bstack111lll1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡵࡨࡰࡪࡴࡩࡶ࡯ࡢࡺࡪࡸࡳࡪࡱࡱࠫࠡ"),
  bstack111lll1l_opy_ (u"ࠪࡱࡦࡹ࡫ࡄࡱࡰࡱࡦࡴࡤࡴࠩࠢ"): bstack111lll1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡱࡦࡹ࡫ࡄࡱࡰࡱࡦࡴࡤࡴࠩࠣ"),
  bstack111lll1l_opy_ (u"ࠬ࡯ࡤ࡭ࡧࡗ࡭ࡲ࡫࡯ࡶࡶࠪࠤ"): bstack111lll1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳࡯ࡤ࡭ࡧࡗ࡭ࡲ࡫࡯ࡶࡶࠪࠥ"),
  bstack111lll1l_opy_ (u"ࠧ࡮ࡣࡶ࡯ࡇࡧࡳࡪࡥࡄࡹࡹ࡮ࠧࠦ"): bstack111lll1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮࡮ࡣࡶ࡯ࡇࡧࡳࡪࡥࡄࡹࡹ࡮ࠧࠧ"),
  bstack111lll1l_opy_ (u"ࠩࡶࡩࡳࡪࡋࡦࡻࡶࠫࠨ"): bstack111lll1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡶࡩࡳࡪࡋࡦࡻࡶࠫࠩ"),
  bstack111lll1l_opy_ (u"ࠫࡦࡻࡴࡰ࡙ࡤ࡭ࡹ࠭ࠪ"): bstack111lll1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡦࡻࡴࡰ࡙ࡤ࡭ࡹ࠭ࠫ"),
  bstack111lll1l_opy_ (u"࠭ࡨࡰࡵࡷࡷࠬࠬ"): bstack111lll1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡨࡰࡵࡷࡷࠬ࠭"),
  bstack111lll1l_opy_ (u"ࠨࡤࡩࡧࡦࡩࡨࡦࠩ࠮"): bstack111lll1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡤࡩࡧࡦࡩࡨࡦࠩ࠯"),
  bstack111lll1l_opy_ (u"ࠪࡻࡸࡒ࡯ࡤࡣ࡯ࡗࡺࡶࡰࡰࡴࡷࠫ࠰"): bstack111lll1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡻࡸࡒ࡯ࡤࡣ࡯ࡗࡺࡶࡰࡰࡴࡷࠫ࠱"),
  bstack111lll1l_opy_ (u"ࠬࡪࡩࡴࡣࡥࡰࡪࡉ࡯ࡳࡵࡕࡩࡸࡺࡲࡪࡥࡷ࡭ࡴࡴࡳࠨ࠲"): bstack111lll1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡪࡩࡴࡣࡥࡰࡪࡉ࡯ࡳࡵࡕࡩࡸࡺࡲࡪࡥࡷ࡭ࡴࡴࡳࠨ࠳"),
  bstack111lll1l_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࡎࡢ࡯ࡨࠫ࠴"): bstack111lll1l_opy_ (u"ࠨࡦࡨࡺ࡮ࡩࡥࠨ࠵"),
  bstack111lll1l_opy_ (u"ࠩࡵࡩࡦࡲࡍࡰࡤ࡬ࡰࡪ࠭࠶"): bstack111lll1l_opy_ (u"ࠪࡶࡪࡧ࡬ࡠ࡯ࡲࡦ࡮ࡲࡥࠨ࠷"),
  bstack111lll1l_opy_ (u"ࠫࡦࡶࡰࡪࡷࡰ࡚ࡪࡸࡳࡪࡱࡱࠫ࠸"): bstack111lll1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡦࡶࡰࡪࡷࡰࡣࡻ࡫ࡲࡴ࡫ࡲࡲࠬ࠹"),
  bstack111lll1l_opy_ (u"࠭ࡣࡶࡵࡷࡳࡲࡔࡥࡵࡹࡲࡶࡰ࠭࠺"): bstack111lll1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡶࡵࡷࡳࡲࡔࡥࡵࡹࡲࡶࡰ࠭࠻"),
  bstack111lll1l_opy_ (u"ࠨࡰࡨࡸࡼࡵࡲ࡬ࡒࡵࡳ࡫࡯࡬ࡦࠩ࠼"): bstack111lll1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡰࡨࡸࡼࡵࡲ࡬ࡒࡵࡳ࡫࡯࡬ࡦࠩ࠽"),
  bstack111lll1l_opy_ (u"ࠪࡥࡨࡩࡥࡱࡶࡌࡲࡸ࡫ࡣࡶࡴࡨࡇࡪࡸࡴࡴࠩ࠾"): bstack111lll1l_opy_ (u"ࠫࡦࡩࡣࡦࡲࡷࡗࡸࡲࡃࡦࡴࡷࡷࠬ࠿"),
  bstack111lll1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡗࡉࡑࠧࡀ"): bstack111lll1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡗࡉࡑࠧࡁ"),
  bstack111lll1l_opy_ (u"ࠧࡴࡱࡸࡶࡨ࡫ࠧࡂ"): bstack111lll1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡴࡱࡸࡶࡨ࡫ࠧࡃ"),
  bstack111lll1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫࡄ"): bstack111lll1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫࡅ"),
  bstack111lll1l_opy_ (u"ࠫ࡭ࡵࡳࡵࡐࡤࡱࡪ࠭ࡆ"): bstack111lll1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲࡭ࡵࡳࡵࡐࡤࡱࡪ࠭ࡇ"),
}
bstack1ll11l_opy_ = [
  bstack111lll1l_opy_ (u"࠭࡯ࡴࠩࡈ"),
  bstack111lll1l_opy_ (u"ࠧࡰࡵ࡙ࡩࡷࡹࡩࡰࡰࠪࡉ"),
  bstack111lll1l_opy_ (u"ࠨࡵࡨࡰࡪࡴࡩࡶ࡯࡙ࡩࡷࡹࡩࡰࡰࠪࡊ"),
  bstack111lll1l_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧࡋ"),
  bstack111lll1l_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࡑࡥࡲ࡫ࠧࡌ"),
  bstack111lll1l_opy_ (u"ࠫࡷ࡫ࡡ࡭ࡏࡲࡦ࡮ࡲࡥࠨࡍ"),
  bstack111lll1l_opy_ (u"ࠬࡧࡰࡱ࡫ࡸࡱ࡛࡫ࡲࡴ࡫ࡲࡲࠬࡎ"),
]
bstack1l1ll111l_opy_ = {
  bstack111lll1l_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨࡏ"): [bstack111lll1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡕࡔࡇࡕࡒࡆࡓࡅࠨࡐ"), bstack111lll1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡖࡕࡈࡖࡤࡔࡁࡎࡇࠪࡑ")],
  bstack111lll1l_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬࡒ"): bstack111lll1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡄࡇࡈࡋࡓࡔࡡࡎࡉ࡞࠭ࡓ"),
  bstack111lll1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧࡔ"): bstack111lll1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡇ࡛ࡉࡍࡆࡢࡒࡆࡓࡅࠨࡕ"),
  bstack111lll1l_opy_ (u"࠭ࡰࡳࡱ࡭ࡩࡨࡺࡎࡢ࡯ࡨࠫࡖ"): bstack111lll1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡐࡓࡑࡍࡉࡈ࡚࡟ࡏࡃࡐࡉࠬࡗ"),
  bstack111lll1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪࡘ"): bstack111lll1l_opy_ (u"ࠩࡅࡖࡔ࡝ࡓࡆࡔࡖࡘࡆࡉࡋࡠࡄࡘࡍࡑࡊ࡟ࡊࡆࡈࡒ࡙ࡏࡆࡊࡇࡕ࡙ࠫ"),
  bstack111lll1l_opy_ (u"ࠪࡴࡦࡸࡡ࡭࡮ࡨࡰࡸࡖࡥࡳࡒ࡯ࡥࡹ࡬࡯ࡳ࡯࡚ࠪ"): bstack111lll1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡔࡆࡘࡁࡍࡎࡈࡐࡘࡥࡐࡆࡔࡢࡔࡑࡇࡔࡇࡑࡕࡑ࡛ࠬ"),
  bstack111lll1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩ࡜"): bstack111lll1l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡒࡏࡄࡃࡏࠫ࡝"),
  bstack111lll1l_opy_ (u"ࠧࡳࡧࡵࡹࡳ࡚ࡥࡴࡶࡶࠫ࡞"): bstack111lll1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡓࡇࡕ࡙ࡓࡥࡔࡆࡕࡗࡗࠬ࡟"),
  bstack111lll1l_opy_ (u"ࠩࡤࡴࡵ࠭ࡠ"): [bstack111lll1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡄࡔࡕࡥࡉࡅࠩࡡ"), bstack111lll1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡅࡕࡖࠧࡢ")],
  bstack111lll1l_opy_ (u"ࠬࡲ࡯ࡨࡎࡨࡺࡪࡲࠧࡣ"): bstack111lll1l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡕࡂࡔࡇࡕ࡚ࡆࡈࡉࡍࡋࡗ࡝ࡤࡊࡅࡃࡗࡊࠫࡤ"),
  bstack111lll1l_opy_ (u"ࠧࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࠫࡥ"): bstack111lll1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡂࡗࡗࡓࡒࡇࡔࡊࡑࡑࠫࡦ")
}
bstack111l1l1l_opy_ = {
  bstack111lll1l_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨࠫࡧ"): [bstack111lll1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡸࡷࡪࡸ࡟࡯ࡣࡰࡩࠬࡨ"), bstack111lll1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡹࡸ࡫ࡲࡏࡣࡰࡩࠬࡩ")],
  bstack111lll1l_opy_ (u"ࠬࡧࡣࡤࡧࡶࡷࡐ࡫ࡹࠨࡪ"): [bstack111lll1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡧࡣࡤࡧࡶࡷࡤࡱࡥࡺࠩ࡫"), bstack111lll1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩ࡬")],
  bstack111lll1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫ࡭"): bstack111lll1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫ࡮"),
  bstack111lll1l_opy_ (u"ࠪࡴࡷࡵࡪࡦࡥࡷࡒࡦࡳࡥࠨ࡯"): bstack111lll1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡴࡷࡵࡪࡦࡥࡷࡒࡦࡳࡥࠨࡰ"),
  bstack111lll1l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧࡱ"): bstack111lll1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧࡲ"),
  bstack111lll1l_opy_ (u"ࠧࡱࡣࡵࡥࡱࡲࡥ࡭ࡵࡓࡩࡷࡖ࡬ࡢࡶࡩࡳࡷࡳࠧࡳ"): [bstack111lll1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡱࡲࡳࠫࡴ"), bstack111lll1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨࡵ")],
  bstack111lll1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧࡶ"): bstack111lll1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡰࡴࡩࡡ࡭ࠩࡷ"),
  bstack111lll1l_opy_ (u"ࠬࡸࡥࡳࡷࡱࡘࡪࡹࡴࡴࠩࡸ"): bstack111lll1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡸࡥࡳࡷࡱࡘࡪࡹࡴࡴࠩࡹ"),
  bstack111lll1l_opy_ (u"ࠧࡢࡲࡳࠫࡺ"): bstack111lll1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡢࡲࡳࠫࡻ"),
  bstack111lll1l_opy_ (u"ࠩ࡯ࡳ࡬ࡒࡥࡷࡧ࡯ࠫࡼ"): bstack111lll1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰࡯ࡳ࡬ࡒࡥࡷࡧ࡯ࠫࡽ"),
  bstack111lll1l_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨࡾ"): bstack111lll1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡦࡻࡴࡰ࡯ࡤࡸ࡮ࡵ࡮ࠨࡿ")
}
bstack111ll1ll1_opy_ = {
  bstack111lll1l_opy_ (u"࠭࡯ࡴࡘࡨࡶࡸ࡯࡯࡯ࠩࢀ"): bstack111lll1l_opy_ (u"ࠧࡰࡵࡢࡺࡪࡸࡳࡪࡱࡱࠫࢁ"),
  bstack111lll1l_opy_ (u"ࠨࡵࡨࡰࡪࡴࡩࡶ࡯࡙ࡩࡷࡹࡩࡰࡰࠪࢂ"): [bstack111lll1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡵࡨࡰࡪࡴࡩࡶ࡯ࡢࡺࡪࡸࡳࡪࡱࡱࠫࢃ"), bstack111lll1l_opy_ (u"ࠪࡷࡪࡲࡥ࡯࡫ࡸࡱࡤࡼࡥࡳࡵ࡬ࡳࡳ࠭ࢄ")],
  bstack111lll1l_opy_ (u"ࠫࡸ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩࢅ"): bstack111lll1l_opy_ (u"ࠬࡴࡡ࡮ࡧࠪࢆ"),
  bstack111lll1l_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪࡔࡡ࡮ࡧࠪࢇ"): bstack111lll1l_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࠧ࢈"),
  bstack111lll1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭ࢉ"): [bstack111lll1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࠪࢊ"), bstack111lll1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡣࡳࡧ࡭ࡦࠩࢋ")],
  bstack111lll1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬࢌ"): bstack111lll1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡥࡶࡦࡴࡶ࡭ࡴࡴࠧࢍ"),
  bstack111lll1l_opy_ (u"࠭ࡲࡦࡣ࡯ࡑࡴࡨࡩ࡭ࡧࠪࢎ"): bstack111lll1l_opy_ (u"ࠧࡳࡧࡤࡰࡤࡳ࡯ࡣ࡫࡯ࡩࠬ࢏"),
  bstack111lll1l_opy_ (u"ࠨࡣࡳࡴ࡮ࡻ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠨ࢐"): [bstack111lll1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡣࡳࡴ࡮ࡻ࡭ࡠࡸࡨࡶࡸ࡯࡯࡯ࠩ࢑"), bstack111lll1l_opy_ (u"ࠪࡥࡵࡶࡩࡶ࡯ࡢࡺࡪࡸࡳࡪࡱࡱࠫ࢒")],
  bstack111lll1l_opy_ (u"ࠫࡦࡩࡣࡦࡲࡷࡍࡳࡹࡥࡤࡷࡵࡩࡈ࡫ࡲࡵࡵࠪ࢓"): [bstack111lll1l_opy_ (u"ࠬࡧࡣࡤࡧࡳࡸࡘࡹ࡬ࡄࡧࡵࡸࡸ࠭࢔"), bstack111lll1l_opy_ (u"࠭ࡡࡤࡥࡨࡴࡹ࡙ࡳ࡭ࡅࡨࡶࡹ࠭࢕")]
}
bstack1ll111111_opy_ = [
  bstack111lll1l_opy_ (u"ࠧࡢࡥࡦࡩࡵࡺࡉ࡯ࡵࡨࡧࡺࡸࡥࡄࡧࡵࡸࡸ࠭࢖"),
  bstack111lll1l_opy_ (u"ࠨࡲࡤ࡫ࡪࡒ࡯ࡢࡦࡖࡸࡷࡧࡴࡦࡩࡼࠫࢗ"),
  bstack111lll1l_opy_ (u"ࠩࡳࡶࡴࡾࡹࠨ࢘"),
  bstack111lll1l_opy_ (u"ࠪࡷࡪࡺࡗࡪࡰࡧࡳࡼࡘࡥࡤࡶ࢙ࠪ"),
  bstack111lll1l_opy_ (u"ࠫࡹ࡯࡭ࡦࡱࡸࡸࡸ࢚࠭"),
  bstack111lll1l_opy_ (u"ࠬࡹࡴࡳ࡫ࡦࡸࡋ࡯࡬ࡦࡋࡱࡸࡪࡸࡡࡤࡶࡤࡦ࡮ࡲࡩࡵࡻ࢛ࠪ"),
  bstack111lll1l_opy_ (u"࠭ࡵ࡯ࡪࡤࡲࡩࡲࡥࡥࡒࡵࡳࡲࡶࡴࡃࡧ࡫ࡥࡻ࡯࡯ࡳࠩ࢜"),
  bstack111lll1l_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬ࢝"),
  bstack111lll1l_opy_ (u"ࠨ࡯ࡲࡾ࠿࡬ࡩࡳࡧࡩࡳࡽࡕࡰࡵ࡫ࡲࡲࡸ࠭࢞"),
  bstack111lll1l_opy_ (u"ࠩࡰࡷ࠿࡫ࡤࡨࡧࡒࡴࡹ࡯࡯࡯ࡵࠪ࢟"),
  bstack111lll1l_opy_ (u"ࠪࡷࡪࡀࡩࡦࡑࡳࡸ࡮ࡵ࡮ࡴࠩࢠ"),
  bstack111lll1l_opy_ (u"ࠫࡸࡧࡦࡢࡴ࡬࠲ࡴࡶࡴࡪࡱࡱࡷࠬࢡ"),
]
bstack11lll1l11_opy_ = [
  bstack111lll1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩࢢ"),
  bstack111lll1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪࢣ"),
  bstack111lll1l_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ࢤ"),
  bstack111lll1l_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨࢥ"),
  bstack111lll1l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬࢦ"),
  bstack111lll1l_opy_ (u"ࠪࡰࡴ࡭ࡌࡦࡸࡨࡰࠬࢧ"),
  bstack111lll1l_opy_ (u"ࠫ࡭ࡺࡴࡱࡒࡵࡳࡽࡿࠧࢨ"),
  bstack111lll1l_opy_ (u"ࠬ࡮ࡴࡵࡲࡶࡔࡷࡵࡸࡺࠩࢩ"),
  bstack111lll1l_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠩࢪ"),
  bstack111lll1l_opy_ (u"ࠧࡵࡧࡶࡸࡈࡵ࡮ࡵࡧࡻࡸࡔࡶࡴࡪࡱࡱࡷࠬࢫ")
]
bstack1l111l_opy_ = [
  bstack111lll1l_opy_ (u"ࠨࡷࡳࡰࡴࡧࡤࡎࡧࡧ࡭ࡦ࠭ࢬ"),
  bstack111lll1l_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨࠫࢭ"),
  bstack111lll1l_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵࡎࡩࡾ࠭ࢮ"),
  bstack111lll1l_opy_ (u"ࠫࡸ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩࢯ"),
  bstack111lll1l_opy_ (u"ࠬࡺࡥࡴࡶࡓࡶ࡮ࡵࡲࡪࡶࡼࠫࢰ"),
  bstack111lll1l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩࢱ"),
  bstack111lll1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩ࡚ࡡࡨࠩࢲ"),
  bstack111lll1l_opy_ (u"ࠨࡲࡵࡳ࡯࡫ࡣࡵࡐࡤࡱࡪ࠭ࢳ"),
  bstack111lll1l_opy_ (u"ࠩࡶࡩࡱ࡫࡮ࡪࡷࡰ࡚ࡪࡸࡳࡪࡱࡱࠫࢴ"),
  bstack111lll1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡒࡦࡳࡥࠨࢵ"),
  bstack111lll1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬࢶ"),
  bstack111lll1l_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࠫࢷ"),
  bstack111lll1l_opy_ (u"࠭࡯ࡴࠩࢸ"),
  bstack111lll1l_opy_ (u"ࠧࡰࡵ࡙ࡩࡷࡹࡩࡰࡰࠪࢹ"),
  bstack111lll1l_opy_ (u"ࠨࡪࡲࡷࡹࡹࠧࢺ"),
  bstack111lll1l_opy_ (u"ࠩࡤࡹࡹࡵࡗࡢ࡫ࡷࠫࢻ"),
  bstack111lll1l_opy_ (u"ࠪࡶࡪ࡭ࡩࡰࡰࠪࢼ"),
  bstack111lll1l_opy_ (u"ࠫࡹ࡯࡭ࡦࡼࡲࡲࡪ࠭ࢽ"),
  bstack111lll1l_opy_ (u"ࠬࡳࡡࡤࡪ࡬ࡲࡪ࠭ࢾ"),
  bstack111lll1l_opy_ (u"࠭ࡲࡦࡵࡲࡰࡺࡺࡩࡰࡰࠪࢿ"),
  bstack111lll1l_opy_ (u"ࠧࡪࡦ࡯ࡩ࡙࡯࡭ࡦࡱࡸࡸࠬࣀ"),
  bstack111lll1l_opy_ (u"ࠨࡦࡨࡺ࡮ࡩࡥࡐࡴ࡬ࡩࡳࡺࡡࡵ࡫ࡲࡲࠬࣁ"),
  bstack111lll1l_opy_ (u"ࠩࡹ࡭ࡩ࡫࡯ࠨࣂ"),
  bstack111lll1l_opy_ (u"ࠪࡲࡴࡖࡡࡨࡧࡏࡳࡦࡪࡔࡪ࡯ࡨࡳࡺࡺࠧࣃ"),
  bstack111lll1l_opy_ (u"ࠫࡧ࡬ࡣࡢࡥ࡫ࡩࠬࣄ"),
  bstack111lll1l_opy_ (u"ࠬࡪࡥࡣࡷࡪࠫࣅ"),
  bstack111lll1l_opy_ (u"࠭ࡣࡶࡵࡷࡳࡲ࡙ࡣࡳࡧࡨࡲࡸ࡮࡯ࡵࡵࠪࣆ"),
  bstack111lll1l_opy_ (u"ࠧࡤࡷࡶࡸࡴࡳࡓࡦࡰࡧࡏࡪࡿࡳࠨࣇ"),
  bstack111lll1l_opy_ (u"ࠨࡴࡨࡥࡱࡓ࡯ࡣ࡫࡯ࡩࠬࣈ"),
  bstack111lll1l_opy_ (u"ࠩࡱࡳࡕ࡯ࡰࡦ࡮࡬ࡲࡪ࠭ࣉ"),
  bstack111lll1l_opy_ (u"ࠪࡧ࡭࡫ࡣ࡬ࡗࡕࡐࠬ࣊"),
  bstack111lll1l_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭࣋"),
  bstack111lll1l_opy_ (u"ࠬࡧࡣࡤࡧࡳࡸࡈࡵ࡯࡬࡫ࡨࡷࠬ࣌"),
  bstack111lll1l_opy_ (u"࠭ࡣࡢࡲࡷࡹࡷ࡫ࡃࡳࡣࡶ࡬ࠬ࣍"),
  bstack111lll1l_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࡎࡢ࡯ࡨࠫ࣎"),
  bstack111lll1l_opy_ (u"ࠨࡣࡳࡴ࡮ࡻ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠨ࣏"),
  bstack111lll1l_opy_ (u"ࠩࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳ࡜ࡥࡳࡵ࡬ࡳࡳ࣐࠭"),
  bstack111lll1l_opy_ (u"ࠪࡲࡴࡈ࡬ࡢࡰ࡮ࡔࡴࡲ࡬ࡪࡰࡪ࣑ࠫ"),
  bstack111lll1l_opy_ (u"ࠫࡲࡧࡳ࡬ࡕࡨࡲࡩࡑࡥࡺࡵ࣒ࠪ"),
  bstack111lll1l_opy_ (u"ࠬࡪࡥࡷ࡫ࡦࡩࡑࡵࡧࡴ࣓ࠩ"),
  bstack111lll1l_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪࡏࡤࠨࣔ"),
  bstack111lll1l_opy_ (u"ࠧࡥࡧࡧ࡭ࡨࡧࡴࡦࡦࡇࡩࡻ࡯ࡣࡦࠩࣕ"),
  bstack111lll1l_opy_ (u"ࠨࡪࡨࡥࡩ࡫ࡲࡑࡣࡵࡥࡲࡹࠧࣖ"),
  bstack111lll1l_opy_ (u"ࠩࡳ࡬ࡴࡴࡥࡏࡷࡰࡦࡪࡸࠧࣗ"),
  bstack111lll1l_opy_ (u"ࠪࡲࡪࡺࡷࡰࡴ࡮ࡐࡴ࡭ࡳࠨࣘ"),
  bstack111lll1l_opy_ (u"ࠫࡳ࡫ࡴࡸࡱࡵ࡯ࡑࡵࡧࡴࡑࡳࡸ࡮ࡵ࡮ࡴࠩࣙ"),
  bstack111lll1l_opy_ (u"ࠬࡩ࡯࡯ࡵࡲࡰࡪࡒ࡯ࡨࡵࠪࣚ"),
  bstack111lll1l_opy_ (u"࠭ࡵࡴࡧ࡚࠷ࡈ࠭ࣛ"),
  bstack111lll1l_opy_ (u"ࠧࡢࡲࡳ࡭ࡺࡳࡌࡰࡩࡶࠫࣜ"),
  bstack111lll1l_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡃ࡫ࡲࡱࡪࡺࡲࡪࡥࠪࣝ"),
  bstack111lll1l_opy_ (u"ࠩࡹ࡭ࡩ࡫࡯ࡗ࠴ࠪࣞ"),
  bstack111lll1l_opy_ (u"ࠪࡱ࡮ࡪࡓࡦࡵࡶ࡭ࡴࡴࡉ࡯ࡵࡷࡥࡱࡲࡁࡱࡲࡶࠫࣟ"),
  bstack111lll1l_opy_ (u"ࠫࡪࡹࡰࡳࡧࡶࡷࡴ࡙ࡥࡳࡸࡨࡶࠬ࣠"),
  bstack111lll1l_opy_ (u"ࠬࡹࡥ࡭ࡧࡱ࡭ࡺࡳࡌࡰࡩࡶࠫ࣡"),
  bstack111lll1l_opy_ (u"࠭ࡳࡦ࡮ࡨࡲ࡮ࡻ࡭ࡄࡦࡳࠫ࣢"),
  bstack111lll1l_opy_ (u"ࠧࡵࡧ࡯ࡩࡲ࡫ࡴࡳࡻࡏࡳ࡬ࡹࣣࠧ"),
  bstack111lll1l_opy_ (u"ࠨࡵࡼࡲࡨ࡚ࡩ࡮ࡧ࡚࡭ࡹ࡮ࡎࡕࡒࠪࣤ"),
  bstack111lll1l_opy_ (u"ࠩࡪࡩࡴࡒ࡯ࡤࡣࡷ࡭ࡴࡴࠧࣥ"),
  bstack111lll1l_opy_ (u"ࠪ࡫ࡵࡹࡌࡰࡥࡤࡸ࡮ࡵ࡮ࠨࣦ"),
  bstack111lll1l_opy_ (u"ࠫࡳ࡫ࡴࡸࡱࡵ࡯ࡕࡸ࡯ࡧ࡫࡯ࡩࠬࣧ"),
  bstack111lll1l_opy_ (u"ࠬࡩࡵࡴࡶࡲࡱࡓ࡫ࡴࡸࡱࡵ࡯ࠬࣨ"),
  bstack111lll1l_opy_ (u"࠭ࡦࡰࡴࡦࡩࡈ࡮ࡡ࡯ࡩࡨࡎࡦࡸࣩࠧ"),
  bstack111lll1l_opy_ (u"ࠧࡹ࡯ࡶࡎࡦࡸࠧ࣪"),
  bstack111lll1l_opy_ (u"ࠨࡺࡰࡼࡏࡧࡲࠨ࣫"),
  bstack111lll1l_opy_ (u"ࠩࡰࡥࡸࡱࡃࡰ࡯ࡰࡥࡳࡪࡳࠨ࣬"),
  bstack111lll1l_opy_ (u"ࠪࡱࡦࡹ࡫ࡃࡣࡶ࡭ࡨࡇࡵࡵࡪ࣭ࠪ"),
  bstack111lll1l_opy_ (u"ࠫࡼࡹࡌࡰࡥࡤࡰࡘࡻࡰࡱࡱࡵࡸ࣮ࠬ"),
  bstack111lll1l_opy_ (u"ࠬࡪࡩࡴࡣࡥࡰࡪࡉ࡯ࡳࡵࡕࡩࡸࡺࡲࡪࡥࡷ࡭ࡴࡴࡳࠨ࣯"),
  bstack111lll1l_opy_ (u"࠭ࡡࡱࡲ࡙ࡩࡷࡹࡩࡰࡰࣰࠪ"),
  bstack111lll1l_opy_ (u"ࠧࡢࡥࡦࡩࡵࡺࡉ࡯ࡵࡨࡧࡺࡸࡥࡄࡧࡵࡸࡸࣱ࠭"),
  bstack111lll1l_opy_ (u"ࠨࡴࡨࡷ࡮࡭࡮ࡂࡲࡳࣲࠫ"),
  bstack111lll1l_opy_ (u"ࠩࡧ࡭ࡸࡧࡢ࡭ࡧࡄࡲ࡮ࡳࡡࡵ࡫ࡲࡲࡸ࠭ࣳ"),
  bstack111lll1l_opy_ (u"ࠪࡧࡦࡴࡡࡳࡻࠪࣴ"),
  bstack111lll1l_opy_ (u"ࠫ࡫࡯ࡲࡦࡨࡲࡼࠬࣵ"),
  bstack111lll1l_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࣶࠬ"),
  bstack111lll1l_opy_ (u"࠭ࡩࡦࠩࣷ"),
  bstack111lll1l_opy_ (u"ࠧࡦࡦࡪࡩࠬࣸ"),
  bstack111lll1l_opy_ (u"ࠨࡵࡤࡪࡦࡸࡩࠨࣹ"),
  bstack111lll1l_opy_ (u"ࠩࡴࡹࡪࡻࡥࠨࣺ"),
  bstack111lll1l_opy_ (u"ࠪ࡭ࡳࡺࡥࡳࡰࡤࡰࠬࣻ"),
  bstack111lll1l_opy_ (u"ࠫࡦࡶࡰࡔࡶࡲࡶࡪࡉ࡯࡯ࡨ࡬࡫ࡺࡸࡡࡵ࡫ࡲࡲࠬࣼ"),
  bstack111lll1l_opy_ (u"ࠬ࡫࡮ࡢࡤ࡯ࡩࡈࡧ࡭ࡦࡴࡤࡍࡲࡧࡧࡦࡋࡱ࡮ࡪࡩࡴࡪࡱࡱࠫࣽ"),
  bstack111lll1l_opy_ (u"࠭࡮ࡦࡶࡺࡳࡷࡱࡌࡰࡩࡶࡉࡽࡩ࡬ࡶࡦࡨࡌࡴࡹࡴࡴࠩࣾ"),
  bstack111lll1l_opy_ (u"ࠧ࡯ࡧࡷࡻࡴࡸ࡫ࡍࡱࡪࡷࡎࡴࡣ࡭ࡷࡧࡩࡍࡵࡳࡵࡵࠪࣿ"),
  bstack111lll1l_opy_ (u"ࠨࡷࡳࡨࡦࡺࡥࡂࡲࡳࡗࡪࡺࡴࡪࡰࡪࡷࠬऀ"),
  bstack111lll1l_opy_ (u"ࠩࡵࡩࡸ࡫ࡲࡷࡧࡇࡩࡻ࡯ࡣࡦࠩँ"),
  bstack111lll1l_opy_ (u"ࠪࡷࡴࡻࡲࡤࡧࠪं"),
  bstack111lll1l_opy_ (u"ࠫࡸ࡫࡮ࡥࡍࡨࡽࡸ࠭ः"),
  bstack111lll1l_opy_ (u"ࠬ࡫࡮ࡢࡤ࡯ࡩࡕࡧࡳࡴࡥࡲࡨࡪ࠭ऄ"),
  bstack111lll1l_opy_ (u"࠭ࡵࡱࡦࡤࡸࡪࡏ࡯ࡴࡆࡨࡺ࡮ࡩࡥࡔࡧࡷࡸ࡮ࡴࡧࡴࠩअ"),
  bstack111lll1l_opy_ (u"ࠧࡦࡰࡤࡦࡱ࡫ࡁࡶࡦ࡬ࡳࡎࡴࡪࡦࡥࡷ࡭ࡴࡴࠧआ"),
  bstack111lll1l_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡂࡲࡳࡰࡪࡖࡡࡺࠩइ"),
  bstack111lll1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࠪई"),
  bstack111lll1l_opy_ (u"ࠪࡻࡩ࡯࡯ࡔࡧࡵࡺ࡮ࡩࡥࠨउ"),
  bstack111lll1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡖࡈࡐ࠭ऊ"),
  bstack111lll1l_opy_ (u"ࠬࡶࡲࡦࡸࡨࡲࡹࡉࡲࡰࡵࡶࡗ࡮ࡺࡥࡕࡴࡤࡧࡰ࡯࡮ࡨࠩऋ"),
  bstack111lll1l_opy_ (u"࠭ࡨࡪࡩ࡫ࡇࡴࡴࡴࡳࡣࡶࡸࠬऌ"),
  bstack111lll1l_opy_ (u"ࠧࡥࡧࡹ࡭ࡨ࡫ࡐࡳࡧࡩࡩࡷ࡫࡮ࡤࡧࡶࠫऍ"),
  bstack111lll1l_opy_ (u"ࠨࡧࡱࡥࡧࡲࡥࡔ࡫ࡰࠫऎ"),
  bstack111lll1l_opy_ (u"ࠩࡶ࡭ࡲࡕࡰࡵ࡫ࡲࡲࡸ࠭ए"),
  bstack111lll1l_opy_ (u"ࠪࡶࡪࡳ࡯ࡷࡧࡌࡓࡘࡇࡰࡱࡕࡨࡸࡹ࡯࡮ࡨࡵࡏࡳࡨࡧ࡬ࡪࡼࡤࡸ࡮ࡵ࡮ࠨऐ"),
  bstack111lll1l_opy_ (u"ࠫ࡭ࡵࡳࡵࡐࡤࡱࡪ࠭ऑ"),
  bstack111lll1l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧऒ"),
  bstack111lll1l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࠨओ"),
  bstack111lll1l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡐࡤࡱࡪ࠭औ"),
  bstack111lll1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯࡙ࡩࡷࡹࡩࡰࡰࠪक"),
  bstack111lll1l_opy_ (u"ࠩࡳࡥ࡬࡫ࡌࡰࡣࡧࡗࡹࡸࡡࡵࡧࡪࡽࠬख"),
  bstack111lll1l_opy_ (u"ࠪࡴࡷࡵࡸࡺࠩग"),
  bstack111lll1l_opy_ (u"ࠫࡹ࡯࡭ࡦࡱࡸࡸࡸ࠭घ"),
  bstack111lll1l_opy_ (u"ࠬࡻ࡮ࡩࡣࡱࡨࡱ࡫ࡤࡑࡴࡲࡱࡵࡺࡂࡦࡪࡤࡺ࡮ࡵࡲࠨङ")
]
bstack111l11l1_opy_ = {
  bstack111lll1l_opy_ (u"࠭ࡶࠨच"): bstack111lll1l_opy_ (u"ࠧࡷࠩछ"),
  bstack111lll1l_opy_ (u"ࠨࡨࠪज"): bstack111lll1l_opy_ (u"ࠩࡩࠫझ"),
  bstack111lll1l_opy_ (u"ࠪࡪࡴࡸࡣࡦࠩञ"): bstack111lll1l_opy_ (u"ࠫ࡫ࡵࡲࡤࡧࠪट"),
  bstack111lll1l_opy_ (u"ࠬࡵ࡮࡭ࡻࡤࡹࡹࡵ࡭ࡢࡶࡨࠫठ"): bstack111lll1l_opy_ (u"࠭࡯࡯࡮ࡼࡅࡺࡺ࡯࡮ࡣࡷࡩࠬड"),
  bstack111lll1l_opy_ (u"ࠧࡧࡱࡵࡧࡪࡲ࡯ࡤࡣ࡯ࠫढ"): bstack111lll1l_opy_ (u"ࠨࡨࡲࡶࡨ࡫࡬ࡰࡥࡤࡰࠬण"),
  bstack111lll1l_opy_ (u"ࠩࡳࡶࡴࡾࡹࡩࡱࡶࡸࠬत"): bstack111lll1l_opy_ (u"ࠪࡴࡷࡵࡸࡺࡊࡲࡷࡹ࠭थ"),
  bstack111lll1l_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡳࡳࡷࡺࠧद"): bstack111lll1l_opy_ (u"ࠬࡶࡲࡰࡺࡼࡔࡴࡸࡴࠨध"),
  bstack111lll1l_opy_ (u"࠭ࡰࡳࡱࡻࡽࡺࡹࡥࡳࠩन"): bstack111lll1l_opy_ (u"ࠧࡱࡴࡲࡼࡾ࡛ࡳࡦࡴࠪऩ"),
  bstack111lll1l_opy_ (u"ࠨࡲࡵࡳࡽࡿࡰࡢࡵࡶࠫप"): bstack111lll1l_opy_ (u"ࠩࡳࡶࡴࡾࡹࡑࡣࡶࡷࠬफ"),
  bstack111lll1l_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡲࡵࡳࡽࡿࡨࡰࡵࡷࠫब"): bstack111lll1l_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡓࡶࡴࡾࡹࡉࡱࡶࡸࠬभ"),
  bstack111lll1l_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡴࡷࡵࡸࡺࡲࡲࡶࡹ࠭म"): bstack111lll1l_opy_ (u"࠭࡬ࡰࡥࡤࡰࡕࡸ࡯ࡹࡻࡓࡳࡷࡺࠧय"),
  bstack111lll1l_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡶࡲࡰࡺࡼࡹࡸ࡫ࡲࠨर"): bstack111lll1l_opy_ (u"ࠨ࠯࡯ࡳࡨࡧ࡬ࡑࡴࡲࡼࡾ࡛ࡳࡦࡴࠪऱ"),
  bstack111lll1l_opy_ (u"ࠩ࠰ࡰࡴࡩࡡ࡭ࡲࡵࡳࡽࡿࡵࡴࡧࡵࠫल"): bstack111lll1l_opy_ (u"ࠪ࠱ࡱࡵࡣࡢ࡮ࡓࡶࡴࡾࡹࡖࡵࡨࡶࠬळ"),
  bstack111lll1l_opy_ (u"ࠫࡱࡵࡣࡢ࡮ࡳࡶࡴࡾࡹࡱࡣࡶࡷࠬऴ"): bstack111lll1l_opy_ (u"ࠬ࠳࡬ࡰࡥࡤࡰࡕࡸ࡯ࡹࡻࡓࡥࡸࡹࠧव"),
  bstack111lll1l_opy_ (u"࠭࠭࡭ࡱࡦࡥࡱࡶࡲࡰࡺࡼࡴࡦࡹࡳࠨश"): bstack111lll1l_opy_ (u"ࠧ࠮࡮ࡲࡧࡦࡲࡐࡳࡱࡻࡽࡕࡧࡳࡴࠩष"),
  bstack111lll1l_opy_ (u"ࠨࡤ࡬ࡲࡦࡸࡹࡱࡣࡷ࡬ࠬस"): bstack111lll1l_opy_ (u"ࠩࡥ࡭ࡳࡧࡲࡺࡲࡤࡸ࡭࠭ह"),
  bstack111lll1l_opy_ (u"ࠪࡴࡦࡩࡦࡪ࡮ࡨࠫऺ"): bstack111lll1l_opy_ (u"ࠫ࠲ࡶࡡࡤ࠯ࡩ࡭ࡱ࡫ࠧऻ"),
  bstack111lll1l_opy_ (u"ࠬࡶࡡࡤ࠯ࡩ࡭ࡱ࡫़ࠧ"): bstack111lll1l_opy_ (u"࠭࠭ࡱࡣࡦ࠱࡫࡯࡬ࡦࠩऽ"),
  bstack111lll1l_opy_ (u"ࠧ࠮ࡲࡤࡧ࠲࡬ࡩ࡭ࡧࠪा"): bstack111lll1l_opy_ (u"ࠨ࠯ࡳࡥࡨ࠳ࡦࡪ࡮ࡨࠫि"),
  bstack111lll1l_opy_ (u"ࠩ࡯ࡳ࡬࡬ࡩ࡭ࡧࠪी"): bstack111lll1l_opy_ (u"ࠪࡰࡴ࡭ࡦࡪ࡮ࡨࠫु"),
  bstack111lll1l_opy_ (u"ࠫࡱࡵࡣࡢ࡮࡬ࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭ू"): bstack111lll1l_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧृ"),
}
bstack1l11l11l_opy_ = bstack111lll1l_opy_ (u"࠭ࡨࡵࡶࡳࡷ࠿࠵࠯ࡩࡷࡥ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳ࠯ࡸࡦ࠲࡬ࡺࡨࠧॄ")
bstack1l111l1l1_opy_ = bstack111lll1l_opy_ (u"ࠧࡩࡶࡷࡴ࠿࠵࠯ࡩࡷࡥ࠲ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡳ࠺࠹࠲࠲ࡻࡩ࠵ࡨࡶࡤࠪॅ")
bstack11l11l11_opy_ = bstack111lll1l_opy_ (u"ࠨࡪࡷࡸࡵࡹ࠺࠰࠱࡫ࡹࡧ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮࠱ࡱࡩࡽࡺ࡟ࡩࡷࡥࡷࠬॆ")
bstack11l1l1ll_opy_ = {
  bstack111lll1l_opy_ (u"ࠩࡦࡶ࡮ࡺࡩࡤࡣ࡯ࠫे"): 50,
  bstack111lll1l_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩै"): 40,
  bstack111lll1l_opy_ (u"ࠫࡼࡧࡲ࡯࡫ࡱ࡫ࠬॉ"): 30,
  bstack111lll1l_opy_ (u"ࠬ࡯࡮ࡧࡱࠪॊ"): 20,
  bstack111lll1l_opy_ (u"࠭ࡤࡦࡤࡸ࡫ࠬो"): 10
}
bstack111l1lll1_opy_ = bstack11l1l1ll_opy_[bstack111lll1l_opy_ (u"ࠧࡪࡰࡩࡳࠬौ")]
bstack11ll11_opy_ = bstack111lll1l_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮࠮ࡲࡼࡸ࡭ࡵ࡮ࡢࡩࡨࡲࡹ࠵्ࠧ")
bstack11l11_opy_ = bstack111lll1l_opy_ (u"ࠩࡵࡳࡧࡵࡴ࠮ࡲࡼࡸ࡭ࡵ࡮ࡢࡩࡨࡲࡹ࠵ࠧॎ")
bstack111l1l11_opy_ = bstack111lll1l_opy_ (u"ࠪࡦࡪ࡮ࡡࡷࡧ࠰ࡴࡾࡺࡨࡰࡰࡤ࡫ࡪࡴࡴ࠰ࠩॏ")
bstack1ll111l1l_opy_ = bstack111lll1l_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷ࠱ࡵࡿࡴࡩࡱࡱࡥ࡬࡫࡮ࡵ࠱ࠪॐ")
bstack1l11l11l1_opy_ = [bstack111lll1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡚࡙ࡅࡓࡐࡄࡑࡊ࠭॑"), bstack111lll1l_opy_ (u"࡙࠭ࡐࡗࡕࡣ࡚࡙ࡅࡓࡐࡄࡑࡊ॒࠭")]
bstack1lll1l11_opy_ = [bstack111lll1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡁࡄࡅࡈࡗࡘࡥࡋࡆ࡛ࠪ॓"), bstack111lll1l_opy_ (u"ࠨ࡛ࡒ࡙ࡗࡥࡁࡄࡅࡈࡗࡘࡥࡋࡆ࡛ࠪ॔")]
bstack1ll1llll_opy_ = [
  bstack111lll1l_opy_ (u"ࠩࡤࡹࡹࡵ࡭ࡢࡶ࡬ࡳࡳࡔࡡ࡮ࡧࠪॕ"),
  bstack111lll1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱ࡛࡫ࡲࡴ࡫ࡲࡲࠬॖ"),
  bstack111lll1l_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࡒࡦࡳࡥࠨॗ"),
  bstack111lll1l_opy_ (u"ࠬࡴࡥࡸࡅࡲࡱࡲࡧ࡮ࡥࡖ࡬ࡱࡪࡵࡵࡵࠩक़"),
  bstack111lll1l_opy_ (u"࠭ࡡࡱࡲࠪख़"),
  bstack111lll1l_opy_ (u"ࠧࡶࡦ࡬ࡨࠬग़"),
  bstack111lll1l_opy_ (u"ࠨ࡮ࡤࡲ࡬ࡻࡡࡨࡧࠪज़"),
  bstack111lll1l_opy_ (u"ࠩ࡯ࡳࡨࡧ࡬ࡦࠩड़"),
  bstack111lll1l_opy_ (u"ࠪࡳࡷ࡯ࡥ࡯ࡶࡤࡸ࡮ࡵ࡮ࠨढ़"),
  bstack111lll1l_opy_ (u"ࠫࡦࡻࡴࡰ࡙ࡨࡦࡻ࡯ࡥࡸࠩफ़"),
  bstack111lll1l_opy_ (u"ࠬࡴ࡯ࡓࡧࡶࡩࡹ࠭य़"), bstack111lll1l_opy_ (u"࠭ࡦࡶ࡮࡯ࡖࡪࡹࡥࡵࠩॠ"),
  bstack111lll1l_opy_ (u"ࠧࡤ࡮ࡨࡥࡷ࡙ࡹࡴࡶࡨࡱࡋ࡯࡬ࡦࡵࠪॡ"),
  bstack111lll1l_opy_ (u"ࠨࡧࡹࡩࡳࡺࡔࡪ࡯࡬ࡲ࡬ࡹࠧॢ"),
  bstack111lll1l_opy_ (u"ࠩࡨࡲࡦࡨ࡬ࡦࡒࡨࡶ࡫ࡵࡲ࡮ࡣࡱࡧࡪࡒ࡯ࡨࡩ࡬ࡲ࡬࠭ॣ"),
  bstack111lll1l_opy_ (u"ࠪࡳࡹ࡮ࡥࡳࡃࡳࡴࡸ࠭।"),
  bstack111lll1l_opy_ (u"ࠫࡵࡸࡩ࡯ࡶࡓࡥ࡬࡫ࡓࡰࡷࡵࡧࡪࡕ࡮ࡇ࡫ࡱࡨࡋࡧࡩ࡭ࡷࡵࡩࠬ॥"),
  bstack111lll1l_opy_ (u"ࠬࡧࡰࡱࡃࡦࡸ࡮ࡼࡩࡵࡻࠪ०"), bstack111lll1l_opy_ (u"࠭ࡡࡱࡲࡓࡥࡨࡱࡡࡨࡧࠪ१"), bstack111lll1l_opy_ (u"ࠧࡢࡲࡳ࡛ࡦ࡯ࡴࡂࡥࡷ࡭ࡻ࡯ࡴࡺࠩ२"), bstack111lll1l_opy_ (u"ࠨࡣࡳࡴ࡜ࡧࡩࡵࡒࡤࡧࡰࡧࡧࡦࠩ३"), bstack111lll1l_opy_ (u"ࠩࡤࡴࡵ࡝ࡡࡪࡶࡇࡹࡷࡧࡴࡪࡱࡱࠫ४"),
  bstack111lll1l_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࡕࡩࡦࡪࡹࡕ࡫ࡰࡩࡴࡻࡴࠨ५"),
  bstack111lll1l_opy_ (u"ࠫࡦࡲ࡬ࡰࡹࡗࡩࡸࡺࡐࡢࡥ࡮ࡥ࡬࡫ࡳࠨ६"),
  bstack111lll1l_opy_ (u"ࠬࡧ࡮ࡥࡴࡲ࡭ࡩࡉ࡯ࡷࡧࡵࡥ࡬࡫ࠧ७"), bstack111lll1l_opy_ (u"࠭ࡡ࡯ࡦࡵࡳ࡮ࡪࡃࡰࡸࡨࡶࡦ࡭ࡥࡆࡰࡧࡍࡳࡺࡥ࡯ࡶࠪ८"),
  bstack111lll1l_opy_ (u"ࠧࡢࡰࡧࡶࡴ࡯ࡤࡅࡧࡹ࡭ࡨ࡫ࡒࡦࡣࡧࡽ࡙࡯࡭ࡦࡱࡸࡸࠬ९"),
  bstack111lll1l_opy_ (u"ࠨࡣࡧࡦࡕࡵࡲࡵࠩ॰"),
  bstack111lll1l_opy_ (u"ࠩࡤࡲࡩࡸ࡯ࡪࡦࡇࡩࡻ࡯ࡣࡦࡕࡲࡧࡰ࡫ࡴࠨॱ"),
  bstack111lll1l_opy_ (u"ࠪࡥࡳࡪࡲࡰ࡫ࡧࡍࡳࡹࡴࡢ࡮࡯ࡘ࡮ࡳࡥࡰࡷࡷࠫॲ"),
  bstack111lll1l_opy_ (u"ࠫࡦࡴࡤࡳࡱ࡬ࡨࡎࡴࡳࡵࡣ࡯ࡰࡕࡧࡴࡩࠩॳ"),
  bstack111lll1l_opy_ (u"ࠬࡧࡶࡥࠩॴ"), bstack111lll1l_opy_ (u"࠭ࡡࡷࡦࡏࡥࡺࡴࡣࡩࡖ࡬ࡱࡪࡵࡵࡵࠩॵ"), bstack111lll1l_opy_ (u"ࠧࡢࡸࡧࡖࡪࡧࡤࡺࡖ࡬ࡱࡪࡵࡵࡵࠩॶ"), bstack111lll1l_opy_ (u"ࠨࡣࡹࡨࡆࡸࡧࡴࠩॷ"),
  bstack111lll1l_opy_ (u"ࠩࡸࡷࡪࡑࡥࡺࡵࡷࡳࡷ࡫ࠧॸ"), bstack111lll1l_opy_ (u"ࠪ࡯ࡪࡿࡳࡵࡱࡵࡩࡕࡧࡴࡩࠩॹ"), bstack111lll1l_opy_ (u"ࠫࡰ࡫ࡹࡴࡶࡲࡶࡪࡖࡡࡴࡵࡺࡳࡷࡪࠧॺ"),
  bstack111lll1l_opy_ (u"ࠬࡱࡥࡺࡃ࡯࡭ࡦࡹࠧॻ"), bstack111lll1l_opy_ (u"࠭࡫ࡦࡻࡓࡥࡸࡹࡷࡰࡴࡧࠫॼ"),
  bstack111lll1l_opy_ (u"ࠧࡤࡪࡵࡳࡲ࡫ࡤࡳ࡫ࡹࡩࡷࡋࡸࡦࡥࡸࡸࡦࡨ࡬ࡦࠩॽ"), bstack111lll1l_opy_ (u"ࠨࡥ࡫ࡶࡴࡳࡥࡥࡴ࡬ࡺࡪࡸࡁࡳࡩࡶࠫॾ"), bstack111lll1l_opy_ (u"ࠩࡦ࡬ࡷࡵ࡭ࡦࡦࡵ࡭ࡻ࡫ࡲࡆࡺࡨࡧࡺࡺࡡࡣ࡮ࡨࡈ࡮ࡸࠧॿ"), bstack111lll1l_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࡧࡶ࡮ࡼࡥࡳࡅ࡫ࡶࡴࡳࡥࡎࡣࡳࡴ࡮ࡴࡧࡇ࡫࡯ࡩࠬঀ"), bstack111lll1l_opy_ (u"ࠫࡨ࡮ࡲࡰ࡯ࡨࡨࡷ࡯ࡶࡦࡴࡘࡷࡪ࡙ࡹࡴࡶࡨࡱࡊࡾࡥࡤࡷࡷࡥࡧࡲࡥࠨঁ"),
  bstack111lll1l_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࡩࡸࡩࡷࡧࡵࡔࡴࡸࡴࠨং"), bstack111lll1l_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪࡪࡲࡪࡸࡨࡶࡕࡵࡲࡵࡵࠪঃ"),
  bstack111lll1l_opy_ (u"ࠧࡤࡪࡵࡳࡲ࡫ࡤࡳ࡫ࡹࡩࡷࡊࡩࡴࡣࡥࡰࡪࡈࡵࡪ࡮ࡧࡇ࡭࡫ࡣ࡬ࠩ঄"),
  bstack111lll1l_opy_ (u"ࠨࡣࡸࡸࡴ࡝ࡥࡣࡸ࡬ࡩࡼ࡚ࡩ࡮ࡧࡲࡹࡹ࠭অ"),
  bstack111lll1l_opy_ (u"ࠩ࡬ࡲࡹ࡫࡮ࡵࡃࡦࡸ࡮ࡵ࡮ࠨআ"), bstack111lll1l_opy_ (u"ࠪ࡭ࡳࡺࡥ࡯ࡶࡆࡥࡹ࡫ࡧࡰࡴࡼࠫই"), bstack111lll1l_opy_ (u"ࠫ࡮ࡴࡴࡦࡰࡷࡊࡱࡧࡧࡴࠩঈ"), bstack111lll1l_opy_ (u"ࠬࡵࡰࡵ࡫ࡲࡲࡦࡲࡉ࡯ࡶࡨࡲࡹࡇࡲࡨࡷࡰࡩࡳࡺࡳࠨউ"),
  bstack111lll1l_opy_ (u"࠭ࡤࡰࡰࡷࡗࡹࡵࡰࡂࡲࡳࡓࡳࡘࡥࡴࡧࡷࠫঊ"),
  bstack111lll1l_opy_ (u"ࠧࡶࡰ࡬ࡧࡴࡪࡥࡌࡧࡼࡦࡴࡧࡲࡥࠩঋ"), bstack111lll1l_opy_ (u"ࠨࡴࡨࡷࡪࡺࡋࡦࡻࡥࡳࡦࡸࡤࠨঌ"),
  bstack111lll1l_opy_ (u"ࠩࡱࡳࡘ࡯ࡧ࡯ࠩ঍"),
  bstack111lll1l_opy_ (u"ࠪ࡭࡬ࡴ࡯ࡳࡧࡘࡲ࡮ࡳࡰࡰࡴࡷࡥࡳࡺࡖࡪࡧࡺࡷࠬ঎"),
  bstack111lll1l_opy_ (u"ࠫࡩ࡯ࡳࡢࡤ࡯ࡩࡆࡴࡤࡳࡱ࡬ࡨ࡜ࡧࡴࡤࡪࡨࡶࡸ࠭এ"),
  bstack111lll1l_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬঐ"),
  bstack111lll1l_opy_ (u"࠭ࡲࡦࡥࡵࡩࡦࡺࡥࡄࡪࡵࡳࡲ࡫ࡄࡳ࡫ࡹࡩࡷ࡙ࡥࡴࡵ࡬ࡳࡳࡹࠧ঑"),
  bstack111lll1l_opy_ (u"ࠧ࡯ࡣࡷ࡭ࡻ࡫ࡗࡦࡤࡖࡧࡷ࡫ࡥ࡯ࡵ࡫ࡳࡹ࠭঒"),
  bstack111lll1l_opy_ (u"ࠨࡣࡱࡨࡷࡵࡩࡥࡕࡦࡶࡪ࡫࡮ࡴࡪࡲࡸࡕࡧࡴࡩࠩও"),
  bstack111lll1l_opy_ (u"ࠩࡱࡩࡹࡽ࡯ࡳ࡭ࡖࡴࡪ࡫ࡤࠨঔ"),
  bstack111lll1l_opy_ (u"ࠪ࡫ࡵࡹࡅ࡯ࡣࡥࡰࡪࡪࠧক"),
  bstack111lll1l_opy_ (u"ࠫ࡮ࡹࡈࡦࡣࡧࡰࡪࡹࡳࠨখ"),
  bstack111lll1l_opy_ (u"ࠬࡧࡤࡣࡇࡻࡩࡨ࡚ࡩ࡮ࡧࡲࡹࡹ࠭গ"),
  bstack111lll1l_opy_ (u"࠭࡬ࡰࡥࡤࡰࡪ࡙ࡣࡳ࡫ࡳࡸࠬঘ"),
  bstack111lll1l_opy_ (u"ࠧࡴ࡭࡬ࡴࡉ࡫ࡶࡪࡥࡨࡍࡳ࡯ࡴࡪࡣ࡯࡭ࡿࡧࡴࡪࡱࡱࠫঙ"),
  bstack111lll1l_opy_ (u"ࠨࡣࡸࡸࡴࡍࡲࡢࡰࡷࡔࡪࡸ࡭ࡪࡵࡶ࡭ࡴࡴࡳࠨচ"),
  bstack111lll1l_opy_ (u"ࠩࡤࡲࡩࡸ࡯ࡪࡦࡑࡥࡹࡻࡲࡢ࡮ࡒࡶ࡮࡫࡮ࡵࡣࡷ࡭ࡴࡴࠧছ"),
  bstack111lll1l_opy_ (u"ࠪࡷࡾࡹࡴࡦ࡯ࡓࡳࡷࡺࠧজ"),
  bstack111lll1l_opy_ (u"ࠫࡷ࡫࡭ࡰࡶࡨࡅࡩࡨࡈࡰࡵࡷࠫঝ"),
  bstack111lll1l_opy_ (u"ࠬࡹ࡫ࡪࡲࡘࡲࡱࡵࡣ࡬ࠩঞ"), bstack111lll1l_opy_ (u"࠭ࡵ࡯࡮ࡲࡧࡰ࡚ࡹࡱࡧࠪট"), bstack111lll1l_opy_ (u"ࠧࡶࡰ࡯ࡳࡨࡱࡋࡦࡻࠪঠ"),
  bstack111lll1l_opy_ (u"ࠨࡣࡸࡸࡴࡒࡡࡶࡰࡦ࡬ࠬড"),
  bstack111lll1l_opy_ (u"ࠩࡶ࡯࡮ࡶࡌࡰࡩࡦࡥࡹࡉࡡࡱࡶࡸࡶࡪ࠭ঢ"),
  bstack111lll1l_opy_ (u"ࠪࡹࡳ࡯࡮ࡴࡶࡤࡰࡱࡕࡴࡩࡧࡵࡔࡦࡩ࡫ࡢࡩࡨࡷࠬণ"),
  bstack111lll1l_opy_ (u"ࠫࡩ࡯ࡳࡢࡤ࡯ࡩ࡜࡯࡮ࡥࡱࡺࡅࡳ࡯࡭ࡢࡶ࡬ࡳࡳ࠭ত"),
  bstack111lll1l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡘࡴࡵ࡬ࡴࡘࡨࡶࡸ࡯࡯࡯ࠩথ"),
  bstack111lll1l_opy_ (u"࠭ࡥ࡯ࡨࡲࡶࡨ࡫ࡁࡱࡲࡌࡲࡸࡺࡡ࡭࡮ࠪদ"),
  bstack111lll1l_opy_ (u"ࠧࡦࡰࡶࡹࡷ࡫ࡗࡦࡤࡹ࡭ࡪࡽࡳࡉࡣࡹࡩࡕࡧࡧࡦࡵࠪধ"), bstack111lll1l_opy_ (u"ࠨࡹࡨࡦࡻ࡯ࡥࡸࡆࡨࡺࡹࡵ࡯࡭ࡵࡓࡳࡷࡺࠧন"), bstack111lll1l_opy_ (u"ࠩࡨࡲࡦࡨ࡬ࡦ࡙ࡨࡦࡻ࡯ࡥࡸࡆࡨࡸࡦ࡯࡬ࡴࡅࡲࡰࡱ࡫ࡣࡵ࡫ࡲࡲࠬ঩"),
  bstack111lll1l_opy_ (u"ࠪࡶࡪࡳ࡯ࡵࡧࡄࡴࡵࡹࡃࡢࡥ࡫ࡩࡑ࡯࡭ࡪࡶࠪপ"),
  bstack111lll1l_opy_ (u"ࠫࡨࡧ࡬ࡦࡰࡧࡥࡷࡌ࡯ࡳ࡯ࡤࡸࠬফ"),
  bstack111lll1l_opy_ (u"ࠬࡨࡵ࡯ࡦ࡯ࡩࡎࡪࠧব"),
  bstack111lll1l_opy_ (u"࠭࡬ࡢࡷࡱࡧ࡭࡚ࡩ࡮ࡧࡲࡹࡹ࠭ভ"),
  bstack111lll1l_opy_ (u"ࠧ࡭ࡱࡦࡥࡹ࡯࡯࡯ࡕࡨࡶࡻ࡯ࡣࡦࡵࡈࡲࡦࡨ࡬ࡦࡦࠪম"), bstack111lll1l_opy_ (u"ࠨ࡮ࡲࡧࡦࡺࡩࡰࡰࡖࡩࡷࡼࡩࡤࡧࡶࡅࡺࡺࡨࡰࡴ࡬ࡾࡪࡪࠧয"),
  bstack111lll1l_opy_ (u"ࠩࡤࡹࡹࡵࡁࡤࡥࡨࡴࡹࡇ࡬ࡦࡴࡷࡷࠬর"), bstack111lll1l_opy_ (u"ࠪࡥࡺࡺ࡯ࡅ࡫ࡶࡱ࡮ࡹࡳࡂ࡮ࡨࡶࡹࡹࠧ঱"),
  bstack111lll1l_opy_ (u"ࠫࡳࡧࡴࡪࡸࡨࡍࡳࡹࡴࡳࡷࡰࡩࡳࡺࡳࡍ࡫ࡥࠫল"),
  bstack111lll1l_opy_ (u"ࠬࡴࡡࡵ࡫ࡹࡩ࡜࡫ࡢࡕࡣࡳࠫ঳"),
  bstack111lll1l_opy_ (u"࠭ࡳࡢࡨࡤࡶ࡮ࡏ࡮ࡪࡶ࡬ࡥࡱ࡛ࡲ࡭ࠩ঴"), bstack111lll1l_opy_ (u"ࠧࡴࡣࡩࡥࡷ࡯ࡁ࡭࡮ࡲࡻࡕࡵࡰࡶࡲࡶࠫ঵"), bstack111lll1l_opy_ (u"ࠨࡵࡤࡪࡦࡸࡩࡊࡩࡱࡳࡷ࡫ࡆࡳࡣࡸࡨ࡜ࡧࡲ࡯࡫ࡱ࡫ࠬশ"), bstack111lll1l_opy_ (u"ࠩࡶࡥ࡫ࡧࡲࡪࡑࡳࡩࡳࡒࡩ࡯࡭ࡶࡍࡳࡈࡡࡤ࡭ࡪࡶࡴࡻ࡮ࡥࠩষ"),
  bstack111lll1l_opy_ (u"ࠪ࡯ࡪ࡫ࡰࡌࡧࡼࡇ࡭ࡧࡩ࡯ࡵࠪস"),
  bstack111lll1l_opy_ (u"ࠫࡱࡵࡣࡢ࡮࡬ࡾࡦࡨ࡬ࡦࡕࡷࡶ࡮ࡴࡧࡴࡆ࡬ࡶࠬহ"),
  bstack111lll1l_opy_ (u"ࠬࡶࡲࡰࡥࡨࡷࡸࡇࡲࡨࡷࡰࡩࡳࡺࡳࠨ঺"),
  bstack111lll1l_opy_ (u"࠭ࡩ࡯ࡶࡨࡶࡐ࡫ࡹࡅࡧ࡯ࡥࡾ࠭঻"),
  bstack111lll1l_opy_ (u"ࠧࡴࡪࡲࡻࡎࡕࡓࡍࡱࡪ়ࠫ"),
  bstack111lll1l_opy_ (u"ࠨࡵࡨࡲࡩࡑࡥࡺࡕࡷࡶࡦࡺࡥࡨࡻࠪঽ"),
  bstack111lll1l_opy_ (u"ࠩࡺࡩࡧࡱࡩࡵࡔࡨࡷࡵࡵ࡮ࡴࡧࡗ࡭ࡲ࡫࡯ࡶࡶࠪা"), bstack111lll1l_opy_ (u"ࠪࡷࡨࡸࡥࡦࡰࡶ࡬ࡴࡺࡗࡢ࡫ࡷࡘ࡮ࡳࡥࡰࡷࡷࠫি"),
  bstack111lll1l_opy_ (u"ࠫࡷ࡫࡭ࡰࡶࡨࡈࡪࡨࡵࡨࡒࡵࡳࡽࡿࠧী"),
  bstack111lll1l_opy_ (u"ࠬ࡫࡮ࡢࡤ࡯ࡩࡆࡹࡹ࡯ࡥࡈࡼࡪࡩࡵࡵࡧࡉࡶࡴࡳࡈࡵࡶࡳࡷࠬু"),
  bstack111lll1l_opy_ (u"࠭ࡳ࡬࡫ࡳࡐࡴ࡭ࡃࡢࡲࡷࡹࡷ࡫ࠧূ"),
  bstack111lll1l_opy_ (u"ࠧࡸࡧࡥ࡯࡮ࡺࡄࡦࡤࡸ࡫ࡕࡸ࡯ࡹࡻࡓࡳࡷࡺࠧৃ"),
  bstack111lll1l_opy_ (u"ࠨࡨࡸࡰࡱࡉ࡯࡯ࡶࡨࡼࡹࡒࡩࡴࡶࠪৄ"),
  bstack111lll1l_opy_ (u"ࠩࡺࡥ࡮ࡺࡆࡰࡴࡄࡴࡵ࡙ࡣࡳ࡫ࡳࡸࠬ৅"),
  bstack111lll1l_opy_ (u"ࠪࡻࡪࡨࡶࡪࡧࡺࡇࡴࡴ࡮ࡦࡥࡷࡖࡪࡺࡲࡪࡧࡶࠫ৆"),
  bstack111lll1l_opy_ (u"ࠫࡦࡶࡰࡏࡣࡰࡩࠬে"),
  bstack111lll1l_opy_ (u"ࠬࡩࡵࡴࡶࡲࡱࡘ࡙ࡌࡄࡧࡵࡸࠬৈ"),
  bstack111lll1l_opy_ (u"࠭ࡴࡢࡲ࡚࡭ࡹ࡮ࡓࡩࡱࡵࡸࡕࡸࡥࡴࡵࡇࡹࡷࡧࡴࡪࡱࡱࠫ৉"),
  bstack111lll1l_opy_ (u"ࠧࡴࡥࡤࡰࡪࡌࡡࡤࡶࡲࡶࠬ৊"),
  bstack111lll1l_opy_ (u"ࠨࡹࡧࡥࡑࡵࡣࡢ࡮ࡓࡳࡷࡺࠧো"),
  bstack111lll1l_opy_ (u"ࠩࡶ࡬ࡴࡽࡘࡤࡱࡧࡩࡑࡵࡧࠨৌ"),
  bstack111lll1l_opy_ (u"ࠪ࡭ࡴࡹࡉ࡯ࡵࡷࡥࡱࡲࡐࡢࡷࡶࡩ্ࠬ"),
  bstack111lll1l_opy_ (u"ࠫࡽࡩ࡯ࡥࡧࡆࡳࡳ࡬ࡩࡨࡈ࡬ࡰࡪ࠭ৎ"),
  bstack111lll1l_opy_ (u"ࠬࡱࡥࡺࡥ࡫ࡥ࡮ࡴࡐࡢࡵࡶࡻࡴࡸࡤࠨ৏"),
  bstack111lll1l_opy_ (u"࠭ࡵࡴࡧࡓࡶࡪࡨࡵࡪ࡮ࡷ࡛ࡉࡇࠧ৐"),
  bstack111lll1l_opy_ (u"ࠧࡱࡴࡨࡺࡪࡴࡴࡘࡆࡄࡅࡹࡺࡡࡤࡪࡰࡩࡳࡺࡳࠨ৑"),
  bstack111lll1l_opy_ (u"ࠨࡹࡨࡦࡉࡸࡩࡷࡧࡵࡅ࡬࡫࡮ࡵࡗࡵࡰࠬ৒"),
  bstack111lll1l_opy_ (u"ࠩ࡮ࡩࡾࡩࡨࡢ࡫ࡱࡔࡦࡺࡨࠨ৓"),
  bstack111lll1l_opy_ (u"ࠪࡹࡸ࡫ࡎࡦࡹ࡚ࡈࡆ࠭৔"),
  bstack111lll1l_opy_ (u"ࠫࡼࡪࡡࡍࡣࡸࡲࡨ࡮ࡔࡪ࡯ࡨࡳࡺࡺࠧ৕"), bstack111lll1l_opy_ (u"ࠬࡽࡤࡢࡅࡲࡲࡳ࡫ࡣࡵ࡫ࡲࡲ࡙࡯࡭ࡦࡱࡸࡸࠬ৖"),
  bstack111lll1l_opy_ (u"࠭ࡸࡤࡱࡧࡩࡔࡸࡧࡊࡦࠪৗ"), bstack111lll1l_opy_ (u"ࠧࡹࡥࡲࡨࡪ࡙ࡩࡨࡰ࡬ࡲ࡬ࡏࡤࠨ৘"),
  bstack111lll1l_opy_ (u"ࠨࡷࡳࡨࡦࡺࡥࡥ࡙ࡇࡅࡇࡻ࡮ࡥ࡮ࡨࡍࡩ࠭৙"),
  bstack111lll1l_opy_ (u"ࠩࡵࡩࡸ࡫ࡴࡐࡰࡖࡩࡸࡹࡩࡰࡰࡖࡸࡦࡸࡴࡐࡰ࡯ࡽࠬ৚"),
  bstack111lll1l_opy_ (u"ࠪࡧࡴࡳ࡭ࡢࡰࡧࡘ࡮ࡳࡥࡰࡷࡷࡷࠬ৛"),
  bstack111lll1l_opy_ (u"ࠫࡼࡪࡡࡔࡶࡤࡶࡹࡻࡰࡓࡧࡷࡶ࡮࡫ࡳࠨড়"), bstack111lll1l_opy_ (u"ࠬࡽࡤࡢࡕࡷࡥࡷࡺࡵࡱࡔࡨࡸࡷࡿࡉ࡯ࡶࡨࡶࡻࡧ࡬ࠨঢ়"),
  bstack111lll1l_opy_ (u"࠭ࡣࡰࡰࡱࡩࡨࡺࡈࡢࡴࡧࡻࡦࡸࡥࡌࡧࡼࡦࡴࡧࡲࡥࠩ৞"),
  bstack111lll1l_opy_ (u"ࠧ࡮ࡣࡻࡘࡾࡶࡩ࡯ࡩࡉࡶࡪࡷࡵࡦࡰࡦࡽࠬয়"),
  bstack111lll1l_opy_ (u"ࠨࡵ࡬ࡱࡵࡲࡥࡊࡵ࡙࡭ࡸ࡯ࡢ࡭ࡧࡆ࡬ࡪࡩ࡫ࠨৠ"),
  bstack111lll1l_opy_ (u"ࠩࡸࡷࡪࡉࡡࡳࡶ࡫ࡥ࡬࡫ࡓࡴ࡮ࠪৡ"),
  bstack111lll1l_opy_ (u"ࠪࡷ࡭ࡵࡵ࡭ࡦࡘࡷࡪ࡙ࡩ࡯ࡩ࡯ࡩࡹࡵ࡮ࡕࡧࡶࡸࡒࡧ࡮ࡢࡩࡨࡶࠬৢ"),
  bstack111lll1l_opy_ (u"ࠫࡸࡺࡡࡳࡶࡌ࡛ࡉࡖࠧৣ"),
  bstack111lll1l_opy_ (u"ࠬࡧ࡬࡭ࡱࡺࡘࡴࡻࡣࡩࡋࡧࡉࡳࡸ࡯࡭࡮ࠪ৤"),
  bstack111lll1l_opy_ (u"࠭ࡩࡨࡰࡲࡶࡪࡎࡩࡥࡦࡨࡲࡆࡶࡩࡑࡱ࡯࡭ࡨࡿࡅࡳࡴࡲࡶࠬ৥"),
  bstack111lll1l_opy_ (u"ࠧ࡮ࡱࡦ࡯ࡑࡵࡣࡢࡶ࡬ࡳࡳࡇࡰࡱࠩ০"),
  bstack111lll1l_opy_ (u"ࠨ࡮ࡲ࡫ࡨࡧࡴࡇࡱࡵࡱࡦࡺࠧ১"), bstack111lll1l_opy_ (u"ࠩ࡯ࡳ࡬ࡩࡡࡵࡈ࡬ࡰࡹ࡫ࡲࡔࡲࡨࡧࡸ࠭২"),
  bstack111lll1l_opy_ (u"ࠪࡥࡱࡲ࡯ࡸࡆࡨࡰࡦࡿࡁࡥࡤࠪ৩")
]
bstack11l1lll1_opy_ = bstack111lll1l_opy_ (u"ࠫ࡭ࡺࡴࡱࡵ࠽࠳࠴ࡧࡰࡪ࠯ࡦࡰࡴࡻࡤ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰ࠳ࡦࡶࡰ࠮ࡣࡸࡸࡴࡳࡡࡵࡧ࠲ࡹࡵࡲ࡯ࡢࡦࠪ৪")
bstack1l1ll1l1l_opy_ = [bstack111lll1l_opy_ (u"ࠬ࠴ࡡࡱ࡭ࠪ৫"), bstack111lll1l_opy_ (u"࠭࠮ࡢࡣࡥࠫ৬"), bstack111lll1l_opy_ (u"ࠧ࠯࡫ࡳࡥࠬ৭")]
bstack1ll1l11l1_opy_ = [bstack111lll1l_opy_ (u"ࠨ࡫ࡧࠫ৮"), bstack111lll1l_opy_ (u"ࠩࡳࡥࡹ࡮ࠧ৯"), bstack111lll1l_opy_ (u"ࠪࡧࡺࡹࡴࡰ࡯ࡢ࡭ࡩ࠭ৰ"), bstack111lll1l_opy_ (u"ࠫࡸ࡮ࡡࡳࡧࡤࡦࡱ࡫࡟ࡪࡦࠪৱ")]
bstack11l111111_opy_ = {
  bstack111lll1l_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬ৲"): bstack111lll1l_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫ৳"),
  bstack111lll1l_opy_ (u"ࠧࡧ࡫ࡵࡩ࡫ࡵࡸࡐࡲࡷ࡭ࡴࡴࡳࠨ৴"): bstack111lll1l_opy_ (u"ࠨ࡯ࡲࡾ࠿࡬ࡩࡳࡧࡩࡳࡽࡕࡰࡵ࡫ࡲࡲࡸ࠭৵"),
  bstack111lll1l_opy_ (u"ࠩࡨࡨ࡬࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ৶"): bstack111lll1l_opy_ (u"ࠪࡱࡸࡀࡥࡥࡩࡨࡓࡵࡺࡩࡰࡰࡶࠫ৷"),
  bstack111lll1l_opy_ (u"ࠫ࡮࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ৸"): bstack111lll1l_opy_ (u"ࠬࡹࡥ࠻࡫ࡨࡓࡵࡺࡩࡰࡰࡶࠫ৹"),
  bstack111lll1l_opy_ (u"࠭ࡳࡢࡨࡤࡶ࡮ࡕࡰࡵ࡫ࡲࡲࡸ࠭৺"): bstack111lll1l_opy_ (u"ࠧࡴࡣࡩࡥࡷ࡯࠮ࡰࡲࡷ࡭ࡴࡴࡳࠨ৻")
}
bstack1l111l1_opy_ = [
  bstack111lll1l_opy_ (u"ࠨࡩࡲࡳ࡬ࡀࡣࡩࡴࡲࡱࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭ৼ"),
  bstack111lll1l_opy_ (u"ࠩࡰࡳࡿࡀࡦࡪࡴࡨࡪࡴࡾࡏࡱࡶ࡬ࡳࡳࡹࠧ৽"),
  bstack111lll1l_opy_ (u"ࠪࡱࡸࡀࡥࡥࡩࡨࡓࡵࡺࡩࡰࡰࡶࠫ৾"),
  bstack111lll1l_opy_ (u"ࠫࡸ࡫࠺ࡪࡧࡒࡴࡹ࡯࡯࡯ࡵࠪ৿"),
  bstack111lll1l_opy_ (u"ࠬࡹࡡࡧࡣࡵ࡭࠳ࡵࡰࡵ࡫ࡲࡲࡸ࠭਀"),
]
bstack11111ll1_opy_ = bstack11lll1l11_opy_ + bstack1l111l_opy_ + bstack1ll1llll_opy_
bstack1l11l11ll_opy_ = [
  bstack111lll1l_opy_ (u"࠭࡞࡭ࡱࡦࡥࡱ࡮࡯ࡴࡶࠧࠫਁ"),
  bstack111lll1l_opy_ (u"ࠧ࡟ࡤࡶ࠱ࡱࡵࡣࡢ࡮࠱ࡧࡴࡳࠤࠨਂ"),
  bstack111lll1l_opy_ (u"ࠨࡠ࠴࠶࠼࠴ࠧਃ"),
  bstack111lll1l_opy_ (u"ࠩࡡ࠵࠵࠴ࠧ਄"),
  bstack111lll1l_opy_ (u"ࠪࡢ࠶࠽࠲࠯࠳࡞࠺࠲࠿࡝࠯ࠩਅ"),
  bstack111lll1l_opy_ (u"ࠫࡣ࠷࠷࠳࠰࠵࡟࠵࠳࠹࡞࠰ࠪਆ"),
  bstack111lll1l_opy_ (u"ࠬࡤ࠱࠸࠴࠱࠷ࡠ࠶࠭࠲࡟࠱ࠫਇ"),
  bstack111lll1l_opy_ (u"࠭࡞࠲࠻࠵࠲࠶࠼࠸࠯ࠩਈ")
]
bstack11l111l11_opy_ = bstack111lll1l_opy_ (u"ࠧࡩࡶࡷࡴࡸࡀ࠯࠰ࡣࡳ࡭࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡨࡵ࡭࠰ࡽࢀࠫਉ")
bstack111l1l1ll_opy_ = bstack111lll1l_opy_ (u"ࠨࡵࡧ࡯࠴ࡼ࠱࠰ࡧࡹࡩࡳࡺࠧਊ")
bstack11llll111_opy_ = [ bstack111lll1l_opy_ (u"ࠩࡤࡹࡹࡵ࡭ࡢࡶࡨࠫ਋") ]
bstack1l1llll1_opy_ = [ bstack111lll1l_opy_ (u"ࠪࡥࡵࡶ࠭ࡢࡷࡷࡳࡲࡧࡴࡦࠩ਌") ]
bstack111l1l1_opy_ = [ bstack111lll1l_opy_ (u"ࠫࡴࡨࡳࡦࡴࡹࡥࡧ࡯࡬ࡪࡶࡼࠫ਍") ]
bstack1l1l11l1_opy_ = bstack111lll1l_opy_ (u"࡙ࠬࡄࡌࡕࡨࡸࡺࡶࠧ਎")
bstack1l1l1l_opy_ = bstack111lll1l_opy_ (u"࠭ࡓࡅࡍࡗࡩࡸࡺࡁࡵࡶࡨࡱࡵࡺࡥࡥࠩਏ")
bstack11llll11_opy_ = bstack111lll1l_opy_ (u"ࠧࡔࡆࡎࡘࡪࡹࡴࡔࡷࡦࡧࡪࡹࡳࡧࡷ࡯ࠫਐ")
bstack1l1lll1ll_opy_ = bstack111lll1l_opy_ (u"ࠨ࠶࠱࠴࠳࠶ࠧ਑")
bstack11ll1_opy_ = [
  bstack111lll1l_opy_ (u"ࠩࡈࡖࡗࡥࡆࡂࡋࡏࡉࡉ࠭਒"),
  bstack111lll1l_opy_ (u"ࠪࡉࡗࡘ࡟ࡕࡋࡐࡉࡉࡥࡏࡖࡖࠪਓ"),
  bstack111lll1l_opy_ (u"ࠫࡊࡘࡒࡠࡄࡏࡓࡈࡑࡅࡅࡡࡅ࡝ࡤࡉࡌࡊࡇࡑࡘࠬਔ"),
  bstack111lll1l_opy_ (u"ࠬࡋࡒࡓࡡࡑࡉ࡙࡝ࡏࡓࡍࡢࡇࡍࡇࡎࡈࡇࡇࠫਕ"),
  bstack111lll1l_opy_ (u"࠭ࡅࡓࡔࡢࡗࡔࡉࡋࡆࡖࡢࡒࡔ࡚࡟ࡄࡑࡑࡒࡊࡉࡔࡆࡆࠪਖ"),
  bstack111lll1l_opy_ (u"ࠧࡆࡔࡕࡣࡈࡕࡎࡏࡇࡆࡘࡎࡕࡎࡠࡅࡏࡓࡘࡋࡄࠨਗ"),
  bstack111lll1l_opy_ (u"ࠨࡇࡕࡖࡤࡉࡏࡏࡐࡈࡇ࡙ࡏࡏࡏࡡࡕࡉࡘࡋࡔࠨਘ"),
  bstack111lll1l_opy_ (u"ࠩࡈࡖࡗࡥࡃࡐࡐࡑࡉࡈ࡚ࡉࡐࡐࡢࡖࡊࡌࡕࡔࡇࡇࠫਙ"),
  bstack111lll1l_opy_ (u"ࠪࡉࡗࡘ࡟ࡄࡑࡑࡒࡊࡉࡔࡊࡑࡑࡣࡆࡈࡏࡓࡖࡈࡈࠬਚ"),
  bstack111lll1l_opy_ (u"ࠫࡊࡘࡒࡠࡅࡒࡒࡓࡋࡃࡕࡋࡒࡒࡤࡌࡁࡊࡎࡈࡈࠬਛ"),
  bstack111lll1l_opy_ (u"ࠬࡋࡒࡓࡡࡑࡅࡒࡋ࡟ࡏࡑࡗࡣࡗࡋࡓࡐࡎ࡙ࡉࡉ࠭ਜ"),
  bstack111lll1l_opy_ (u"࠭ࡅࡓࡔࡢࡅࡉࡊࡒࡆࡕࡖࡣࡎࡔࡖࡂࡎࡌࡈࠬਝ"),
  bstack111lll1l_opy_ (u"ࠧࡆࡔࡕࡣࡆࡊࡄࡓࡇࡖࡗࡤ࡛ࡎࡓࡇࡄࡇࡍࡇࡂࡍࡇࠪਞ"),
  bstack111lll1l_opy_ (u"ࠨࡇࡕࡖࡤ࡚ࡕࡏࡐࡈࡐࡤࡉࡏࡏࡐࡈࡇ࡙ࡏࡏࡏࡡࡉࡅࡎࡒࡅࡅࠩਟ"),
  bstack111lll1l_opy_ (u"ࠩࡈࡖࡗࡥࡃࡐࡐࡑࡉࡈ࡚ࡉࡐࡐࡢࡘࡎࡓࡅࡅࡡࡒ࡙࡙࠭ਠ"),
  bstack111lll1l_opy_ (u"ࠪࡉࡗࡘ࡟ࡔࡑࡆࡏࡘࡥࡃࡐࡐࡑࡉࡈ࡚ࡉࡐࡐࡢࡊࡆࡏࡌࡆࡆࠪਡ"),
  bstack111lll1l_opy_ (u"ࠫࡊࡘࡒࡠࡕࡒࡇࡐ࡙࡟ࡄࡑࡑࡒࡊࡉࡔࡊࡑࡑࡣࡍࡕࡓࡕࡡࡘࡒࡗࡋࡁࡄࡊࡄࡆࡑࡋࠧਢ"),
  bstack111lll1l_opy_ (u"ࠬࡋࡒࡓࡡࡓࡖࡔ࡞࡙ࡠࡅࡒࡒࡓࡋࡃࡕࡋࡒࡒࡤࡌࡁࡊࡎࡈࡈࠬਣ"),
  bstack111lll1l_opy_ (u"࠭ࡅࡓࡔࡢࡒࡆࡓࡅࡠࡐࡒࡘࡤࡘࡅࡔࡑࡏ࡚ࡊࡊࠧਤ"),
  bstack111lll1l_opy_ (u"ࠧࡆࡔࡕࡣࡓࡇࡍࡆࡡࡕࡉࡘࡕࡌࡖࡖࡌࡓࡓࡥࡆࡂࡋࡏࡉࡉ࠭ਥ"),
  bstack111lll1l_opy_ (u"ࠨࡇࡕࡖࡤࡓࡁࡏࡆࡄࡘࡔࡘ࡙ࡠࡒࡕࡓ࡝࡟࡟ࡄࡑࡑࡊࡎࡍࡕࡓࡃࡗࡍࡔࡔ࡟ࡇࡃࡌࡐࡊࡊࠧਦ"),
]
bstack11l1l1ll1_opy_ = bstack111lll1l_opy_ (u"ࠩ࠱࠳ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠰ࡥࡷࡺࡩࡧࡣࡦࡸࡸ࠵ࠧਧ")
def bstack11l111l1_opy_():
  global CONFIG
  headers = {
        bstack111lll1l_opy_ (u"ࠪࡇࡴࡴࡴࡦࡰࡷ࠱ࡹࡿࡰࡦࠩਨ"): bstack111lll1l_opy_ (u"ࠫࡦࡶࡰ࡭࡫ࡦࡥࡹ࡯࡯࡯࠱࡭ࡷࡴࡴࠧ਩"),
      }
  proxies = bstack1l11111l_opy_(CONFIG, bstack11l11l11_opy_)
  try:
    response = requests.get(bstack11l11l11_opy_, headers=headers, proxies=proxies, timeout=5)
    if response.json():
      bstack11111l1l_opy_ = response.json()[bstack111lll1l_opy_ (u"ࠬ࡮ࡵࡣࡵࠪਪ")]
      logger.debug(bstack11l1l_opy_.format(response.json()))
      return bstack11111l1l_opy_
    else:
      logger.debug(bstack111lll111_opy_.format(bstack111lll1l_opy_ (u"ࠨࡒࡦࡵࡳࡳࡳࡹࡥࠡࡌࡖࡓࡓࠦࡰࡢࡴࡶࡩࠥ࡫ࡲࡳࡱࡵࠤࠧਫ")))
  except Exception as e:
    logger.debug(bstack111lll111_opy_.format(e))
def bstack1ll1lll_opy_(hub_url):
  global CONFIG
  url = bstack111lll1l_opy_ (u"ࠢࡩࡶࡷࡴࡸࡀ࠯࠰ࠤਬ")+  hub_url + bstack111lll1l_opy_ (u"ࠣ࠱ࡦ࡬ࡪࡩ࡫ࠣਭ")
  headers = {
        bstack111lll1l_opy_ (u"ࠩࡆࡳࡳࡺࡥ࡯ࡶ࠰ࡸࡾࡶࡥࠨਮ"): bstack111lll1l_opy_ (u"ࠪࡥࡵࡶ࡬ࡪࡥࡤࡸ࡮ࡵ࡮࠰࡬ࡶࡳࡳ࠭ਯ"),
      }
  proxies = bstack1l11111l_opy_(CONFIG, url)
  try:
    start_time = time.perf_counter()
    requests.get(url, headers=headers, proxies=proxies, timeout=5)
    latency = time.perf_counter() - start_time
    logger.debug(bstack1l1l1l1_opy_.format(hub_url, latency))
    return dict(hub_url=hub_url, latency=latency)
  except Exception as e:
    logger.debug(bstack1l11111_opy_.format(hub_url, e))
def bstack11l11ll1l_opy_():
  try:
    global bstack1l111ll1_opy_
    bstack11111l1l_opy_ = bstack11l111l1_opy_()
    bstack1l11llll1_opy_ = []
    results = []
    for bstack11l1ll11l_opy_ in bstack11111l1l_opy_:
      bstack1l11llll1_opy_.append(bstack1lll111l1_opy_(target=bstack1ll1lll_opy_,args=(bstack11l1ll11l_opy_,)))
    for t in bstack1l11llll1_opy_:
      t.start()
    for t in bstack1l11llll1_opy_:
      results.append(t.join())
    bstack1ll1ll1ll_opy_ = {}
    for item in results:
      hub_url = item[bstack111lll1l_opy_ (u"ࠫ࡭ࡻࡢࡠࡷࡵࡰࠬਰ")]
      latency = item[bstack111lll1l_opy_ (u"ࠬࡲࡡࡵࡧࡱࡧࡾ࠭਱")]
      bstack1ll1ll1ll_opy_[hub_url] = latency
    bstack1l1111_opy_ = min(bstack1ll1ll1ll_opy_, key= lambda x: bstack1ll1ll1ll_opy_[x])
    bstack1l111ll1_opy_ = bstack1l1111_opy_
    logger.debug(bstack1ll11llll_opy_.format(bstack1l1111_opy_))
  except Exception as e:
    logger.debug(bstack11ll111l_opy_.format(e))
bstack11l11111_opy_ = bstack111lll1l_opy_ (u"࠭ࡓࡦࡶࡷ࡭ࡳ࡭ࠠࡶࡲࠣࡪࡴࡸࠠࡃࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠲ࠠࡶࡵ࡬ࡲ࡬ࠦࡦࡳࡣࡰࡩࡼࡵࡲ࡬࠼ࠣࡿࢂ࠭ਲ")
bstack1l1lll11_opy_ = bstack111lll1l_opy_ (u"ࠧࡄࡱࡰࡴࡱ࡫ࡴࡦࡦࠣࡷࡪࡺࡵࡱࠣࠪਲ਼")
bstack11ll11lll_opy_ = bstack111lll1l_opy_ (u"ࠨࡒࡤࡶࡸ࡫ࡤࠡࡥࡲࡲ࡫࡯ࡧࠡࡨ࡬ࡰࡪࡀࠠࡼࡿࠪ਴")
bstack1l11l_opy_ = bstack111lll1l_opy_ (u"ࠩࡖࡥࡳ࡯ࡴࡪࡼࡨࡨࠥࡩ࡯࡯ࡨ࡬࡫ࠥ࡬ࡩ࡭ࡧ࠽ࠤࢀࢃࠧਵ")
bstack11ll1ll_opy_ = bstack111lll1l_opy_ (u"࡙ࠪࡸ࡯࡮ࡨࠢ࡫ࡹࡧࠦࡵࡳ࡮࠽ࠤࢀࢃࠧਸ਼")
bstack1lll11lll_opy_ = bstack111lll1l_opy_ (u"ࠫࡘ࡫ࡳࡴ࡫ࡲࡲࠥࡹࡴࡢࡴࡷࡩࡩࠦࡷࡪࡶ࡫ࠤ࡮ࡪ࠺ࠡࡽࢀࠫ਷")
bstack1l1lll1l_opy_ = bstack111lll1l_opy_ (u"ࠬࡘࡥࡤࡧ࡬ࡺࡪࡪࠠࡪࡰࡷࡩࡷࡸࡵࡱࡶ࠯ࠤࡪࡾࡩࡵ࡫ࡱ࡫ࠬਸ")
bstack1lll1ll_opy_ = bstack111lll1l_opy_ (u"࠭ࡐ࡭ࡧࡤࡷࡪࠦࡩ࡯ࡵࡷࡥࡱࡲࠠࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࠢࡷࡳࠥࡸࡵ࡯ࠢࡷࡩࡸࡺࡳ࠯ࠢࡣࡴ࡮ࡶࠠࡪࡰࡶࡸࡦࡲ࡬ࠡࡵࡨࡰࡪࡴࡩࡶ࡯ࡣࠫਹ")
bstack11llll1_opy_ = bstack111lll1l_opy_ (u"ࠧࡑ࡮ࡨࡥࡸ࡫ࠠࡪࡰࡶࡸࡦࡲ࡬ࠡࡲࡼࡸࡪࡹࡴࠡࡣࡱࡨࠥࡶࡹࡵࡧࡶࡸ࠲ࡹࡥ࡭ࡧࡱ࡭ࡺࡳࠠࡱࡣࡦ࡯ࡦ࡭ࡥࡴ࠰ࠣࡤࡵ࡯ࡰࠡ࡫ࡱࡷࡹࡧ࡬࡭ࠢࡳࡽࡹ࡫ࡳࡵࠢࡳࡽࡹ࡫ࡳࡵ࠯ࡶࡩࡱ࡫࡮ࡪࡷࡰࡤࠬ਺")
bstack11_opy_ = bstack111lll1l_opy_ (u"ࠨࡒ࡯ࡩࡦࡹࡥࠡ࡫ࡱࡷࡹࡧ࡬࡭ࠢࡄࡴࡵ࡯ࡵ࡮ࡎ࡬ࡦࡷࡧࡲࡺࠢࡳࡥࡨࡱࡡࡨࡧ࠱ࠤࡥࡶࡩࡱࠢ࡬ࡲࡸࡺࡡ࡭࡮ࠣࡶࡴࡨ࡯ࡵࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮࠱ࡦࡶࡰࡪࡷࡰࡰ࡮ࡨࡲࡢࡴࡼࡤࠬ਻")
bstack111l11lll_opy_ = bstack111lll1l_opy_ (u"ࠩࡓࡰࡪࡧࡳࡦࠢ࡬ࡲࡸࡺࡡ࡭࡮ࠣࡶࡴࡨ࡯ࡵ࠮ࠣࡴࡦࡨ࡯ࡵࠢࡤࡲࡩࠦࡳࡦ࡮ࡨࡲ࡮ࡻ࡭࡭࡫ࡥࡶࡦࡸࡹࠡࡲࡤࡧࡰࡧࡧࡦࡵࠣࡸࡴࠦࡲࡶࡰࠣࡶࡴࡨ࡯ࡵࠢࡷࡩࡸࡺࡳࠡ࡫ࡱࠤࡵࡧࡲࡢ࡮࡯ࡩࡱ࠴ࠠࡡࡲ࡬ࡴࠥ࡯࡮ࡴࡶࡤࡰࡱࠦࡲࡰࡤࡲࡸ࡫ࡸࡡ࡮ࡧࡺࡳࡷࡱࠠࡳࡱࡥࡳࡹ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫࠮ࡲࡤࡦࡴࡺࠠࡳࡱࡥࡳࡹ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫࠮ࡵࡨࡰࡪࡴࡩࡶ࡯࡯࡭ࡧࡸࡡࡳࡻࡣ਼ࠫ")
bstack111l1l1l1_opy_ = bstack111lll1l_opy_ (u"ࠪࡔࡱ࡫ࡡࡴࡧࠣ࡭ࡳࡹࡴࡢ࡮࡯ࠤࡧ࡫ࡨࡢࡸࡨࠤࡹࡵࠠࡳࡷࡱࠤࡹ࡫ࡳࡵࡵ࠱ࠤࡥࡶࡩࡱࠢ࡬ࡲࡸࡺࡡ࡭࡮ࠣࡦࡪ࡮ࡡࡷࡧࡣࠫ਽")
bstack1l1lllll_opy_ = bstack111lll1l_opy_ (u"ࠫࡕࡲࡥࡢࡵࡨࠤ࡮ࡴࡳࡵࡣ࡯ࡰࠥࡧࡰࡱ࡫ࡸࡱ࠲ࡩ࡬ࡪࡧࡱࡸࠥࡺ࡯ࠡࡴࡸࡲࠥࡺࡥࡴࡶࡶ࠲ࠥࡦࡰࡪࡲࠣ࡭ࡳࡹࡴࡢ࡮࡯ࠤࡆࡶࡰࡪࡷࡰ࠱ࡕࡿࡴࡩࡱࡱ࠱ࡈࡲࡩࡦࡰࡷࡤࠬਾ")
bstack1l11lll11_opy_ = bstack111lll1l_opy_ (u"ࠬࡖ࡬ࡦࡣࡶࡩࠥ࡯࡮ࡴࡶࡤࡰࡱࠦࡰ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠣࡸࡴࠦࡲࡶࡰࠣࡸࡪࡹࡴࡴ࠰ࠣࡤࡵ࡯ࡰࠡ࡫ࡱࡷࡹࡧ࡬࡭ࠢࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࡦࠧਿ")
bstack11l1lllll_opy_ = bstack111lll1l_opy_ (u"࠭ࡃࡰࡷ࡯ࡨࠥࡴ࡯ࡵࠢࡩ࡭ࡳࡪࠠࡦ࡫ࡷ࡬ࡪࡸࠠࡔࡧ࡯ࡩࡳ࡯ࡵ࡮ࠢࡲࡶࠥࡖ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠢࡷࡳࠥࡸࡵ࡯ࠢࡷࡩࡸࡺࡳ࠯ࠢࡓࡰࡪࡧࡳࡦࠢ࡬ࡲࡹࡧ࡬࡭ࠢࡷ࡬ࡪࠦࡲࡦ࡮ࡨࡺࡦࡴࡴࠡࡲࡤࡧࡰࡧࡧࡦࡵࠣࡹࡸ࡯࡮ࡨࠢࡳ࡭ࡵࠦࡴࡰࠢࡵࡹࡳࠦࡴࡦࡵࡷࡷ࠳࠭ੀ")
bstack1ll11lll1_opy_ = bstack111lll1l_opy_ (u"ࠧࡉࡣࡱࡨࡱ࡯࡮ࡨࠢࡶࡩࡸࡹࡩࡰࡰࠣࡧࡱࡵࡳࡦࠩੁ")
bstack111lllll_opy_ = bstack111lll1l_opy_ (u"ࠨࡃ࡯ࡰࠥࡪ࡯࡯ࡧࠤࠫੂ")
bstack11lll1111_opy_ = bstack111lll1l_opy_ (u"ࠩࡆࡳࡳ࡬ࡩࡨࠢࡩ࡭ࡱ࡫ࠠࡥࡱࡨࡷࠥࡴ࡯ࡵࠢࡨࡼ࡮ࡹࡴࠡࡣࡷࠤࡦࡴࡹࠡࡲࡤࡶࡪࡴࡴࠡࡦ࡬ࡶࡪࡩࡴࡰࡴࡼࠤࡴ࡬ࠠࠣࡽࢀࠦ࠳ࠦࡐ࡭ࡧࡤࡷࡪࠦࡩ࡯ࡥ࡯ࡹࡩ࡫ࠠࡢࠢࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡻࡰࡰ࠴ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡾࡧ࡭࡭ࠢࡩ࡭ࡱ࡫ࠠࡤࡱࡱࡸࡦ࡯࡮ࡪࡰࡪࠤࡨࡵ࡮ࡧ࡫ࡪࡹࡷࡧࡴࡪࡱࡱࠤ࡫ࡵࡲࠡࡶࡨࡷࡹࡹ࠮ࠨ੃")
bstack1ll1l111_opy_ = bstack111lll1l_opy_ (u"ࠪࡆࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠢࡦࡶࡪࡪࡥ࡯ࡶ࡬ࡥࡱࡹࠠ࡯ࡱࡷࠤࡵࡸ࡯ࡷ࡫ࡧࡩࡩ࠴ࠠࡑ࡮ࡨࡥࡸ࡫ࠠࡢࡦࡧࠤࡹ࡮ࡥ࡮ࠢ࡬ࡲࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲ࡾࡳ࡬ࠡࡥࡲࡲ࡫࡯ࡧࠡࡨ࡬ࡰࡪࠦࡡࡴࠢࠥࡹࡸ࡫ࡲࡏࡣࡰࡩࠧࠦࡡ࡯ࡦࠣࠦࡦࡩࡣࡦࡵࡶࡏࡪࡿࠢࠡࡱࡵࠤࡸ࡫ࡴࠡࡶ࡫ࡩࡲࠦࡡࡴࠢࡨࡲࡻ࡯ࡲࡰࡰࡰࡩࡳࡺࠠࡷࡣࡵ࡭ࡦࡨ࡬ࡦࡵ࠽ࠤࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣ࡚࡙ࡅࡓࡐࡄࡑࡊࠨࠠࡢࡰࡧࠤࠧࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡆࡉࡃࡆࡕࡖࡣࡐࡋ࡙ࠣࠩ੄")
bstack1111l1l_opy_ = bstack111lll1l_opy_ (u"ࠫࡒࡧ࡬ࡧࡱࡵࡱࡪࡪࠠࡤࡱࡱࡪ࡮࡭ࠠࡧ࡫࡯ࡩ࠿ࠨࡻࡾࠤࠪ੅")
bstack1lll1l1l1_opy_ = bstack111lll1l_opy_ (u"ࠬࡋ࡮ࡤࡱࡸࡲࡹ࡫ࡲࡦࡦࠣࡩࡷࡸ࡯ࡳࠢࡺ࡬࡮ࡲࡥࠡࡵࡨࡸࡹ࡯࡮ࡨࠢࡸࡴࠥ࠳ࠠࡼࡿࠪ੆")
bstack111l1lll_opy_ = bstack111lll1l_opy_ (u"࠭ࡓࡵࡣࡵࡸ࡮ࡴࡧࠡࡄࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡍࡱࡦࡥࡱ࠭ੇ")
bstack111lllll1_opy_ = bstack111lll1l_opy_ (u"ࠧࡔࡶࡲࡴࡵ࡯࡮ࡨࠢࡅࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠡࡎࡲࡧࡦࡲࠧੈ")
bstack11llllll_opy_ = bstack111lll1l_opy_ (u"ࠨࡄࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡍࡱࡦࡥࡱࠦࡩࡴࠢࡱࡳࡼࠦࡲࡶࡰࡱ࡭ࡳ࡭ࠡࠨ੉")
bstack1111ll1_opy_ = bstack111lll1l_opy_ (u"ࠩࡆࡳࡺࡲࡤࠡࡰࡲࡸࠥࡹࡴࡢࡴࡷࠤࡇࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠣࡐࡴࡩࡡ࡭࠼ࠣࡿࢂ࠭੊")
bstack1l1ll1111_opy_ = bstack111lll1l_opy_ (u"ࠪࡗࡹࡧࡲࡵ࡫ࡱ࡫ࠥࡲ࡯ࡤࡣ࡯ࠤࡧ࡯࡮ࡢࡴࡼࠤࡼ࡯ࡴࡩࠢࡲࡴࡹ࡯࡯࡯ࡵ࠽ࠤࢀࢃࠧੋ")
bstack11ll11ll1_opy_ = bstack111lll1l_opy_ (u"࡚ࠫࡶࡤࡢࡶ࡬ࡲ࡬ࠦࡳࡦࡵࡶ࡭ࡴࡴࠠࡥࡧࡷࡥ࡮ࡲࡳ࠻ࠢࡾࢁࠬੌ")
bstack1ll1l11_opy_ = bstack111lll1l_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡴࡧࡷࡸ࡮ࡴࡧࠡࡷࡳࡨࡦࡺࡩ࡯ࡩࠣࡸࡪࡹࡴࠡࡵࡷࡥࡹࡻࡳࠡࡽࢀ੍ࠫ")
bstack11l1ll1ll_opy_ = bstack111lll1l_opy_ (u"࠭ࡐ࡭ࡧࡤࡷࡪࠦࡰࡳࡱࡹ࡭ࡩ࡫ࠠࡢࡰࠣࡥࡵࡶࡲࡰࡲࡵ࡭ࡦࡺࡥࠡࡈ࡚ࠤ࠭ࡸ࡯ࡣࡱࡷ࠳ࡵࡧࡢࡰࡶࠬࠤ࡮ࡴࠠࡤࡱࡱࡪ࡮࡭ࠠࡧ࡫࡯ࡩ࠱ࠦࡳ࡬࡫ࡳࠤࡹ࡮ࡥࠡࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠤࡰ࡫ࡹࠡ࡫ࡱࠤࡨࡵ࡮ࡧ࡫ࡪࠤ࡮࡬ࠠࡳࡷࡱࡲ࡮ࡴࡧࠡࡵ࡬ࡱࡵࡲࡥࠡࡲࡼࡸ࡭ࡵ࡮ࠡࡵࡦࡶ࡮ࡶࡴࠡࡹ࡬ࡸ࡭ࡵࡵࡵࠢࡤࡲࡾࠦࡆࡘ࠰ࠪ੎")
bstack11l11l1_opy_ = bstack111lll1l_opy_ (u"ࠧࡔࡧࡷࡸ࡮ࡴࡧࠡࡪࡷࡸࡵࡖࡲࡰࡺࡼ࠳࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠡ࡫ࡶࠤࡳࡵࡴࠡࡵࡸࡴࡵࡵࡲࡵࡧࡧࠤࡴࡴࠠࡤࡷࡵࡶࡪࡴࡴ࡭ࡻࠣ࡭ࡳࡹࡴࡢ࡮࡯ࡩࡩࠦࡶࡦࡴࡶ࡭ࡴࡴࠠࡰࡨࠣࡷࡪࡲࡥ࡯࡫ࡸࡱࠥ࠮ࡻࡾࠫ࠯ࠤࡵࡲࡥࡢࡵࡨࠤࡺࡶࡧࡳࡣࡧࡩࠥࡺ࡯ࠡࡕࡨࡰࡪࡴࡩࡶ࡯ࡁࡁ࠹࠴࠰࠯࠲ࠣࡳࡷࠦࡲࡦࡨࡨࡶࠥࡺ࡯ࠡࡪࡷࡸࡵࡹ࠺࠰࠱ࡺࡻࡼ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮࠱ࡧࡳࡨࡹ࠯ࡢࡷࡷࡳࡲࡧࡴࡦ࠱ࡶࡩࡱ࡫࡮ࡪࡷࡰ࠳ࡷࡻ࡮࠮ࡶࡨࡷࡹࡹ࠭ࡣࡧ࡫࡭ࡳࡪ࠭ࡱࡴࡲࡼࡾࠩࡰࡺࡶ࡫ࡳࡳࠦࡦࡰࡴࠣࡥࠥࡽ࡯ࡳ࡭ࡤࡶࡴࡻ࡮ࡥ࠰ࠪ੏")
bstack1l11l1lll_opy_ = bstack111lll1l_opy_ (u"ࠨࡉࡨࡲࡪࡸࡡࡵ࡫ࡱ࡫ࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠤࡨࡵ࡮ࡧ࡫ࡪࡹࡷࡧࡴࡪࡱࡱࠤࡾࡳ࡬ࠡࡨ࡬ࡰࡪ࠴࠮ࠨ੐")
bstack1111_opy_ = bstack111lll1l_opy_ (u"ࠩࡖࡹࡨࡩࡥࡴࡵࡩࡹࡱࡲࡹࠡࡩࡨࡲࡪࡸࡡࡵࡧࡧࠤࡹ࡮ࡥࠡࡥࡲࡲ࡫࡯ࡧࡶࡴࡤࡸ࡮ࡵ࡮ࠡࡨ࡬ࡰࡪࠧࠧੑ")
bstack111l11ll1_opy_ = bstack111lll1l_opy_ (u"ࠪࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡧࡦࡰࡨࡶࡦࡺࡥࠡࡶ࡫ࡩࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠤࡨࡵ࡮ࡧ࡫ࡪࡹࡷࡧࡴࡪࡱࡱࠤ࡫࡯࡬ࡦ࠰ࠣࡿࢂ࠭੒")
bstack111l1l_opy_ = bstack111lll1l_opy_ (u"ࠫࡊࡾࡰࡦࡥࡷࡩࡩࠦࡡࡵࠢ࡯ࡩࡦࡹࡴࠡ࠳ࠣ࡭ࡳࡶࡵࡵ࠮ࠣࡶࡪࡩࡥࡪࡸࡨࡨࠥ࠶ࠧ੓")
bstack1l11l1l_opy_ = bstack111lll1l_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤࡩࡻࡲࡪࡰࡪࠤࡆࡶࡰࠡࡷࡳࡰࡴࡧࡤ࠯ࠢࡾࢁࠬ੔")
bstack1ll11l1l1_opy_ = bstack111lll1l_opy_ (u"࠭ࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡸࡴࡱࡵࡡࡥࠢࡄࡴࡵ࠴ࠠࡊࡰࡹࡥࡱ࡯ࡤࠡࡨ࡬ࡰࡪࠦࡰࡢࡶ࡫ࠤࡵࡸ࡯ࡷ࡫ࡧࡩࡩࠦࡻࡾ࠰ࠪ੕")
bstack1ll1l111l_opy_ = bstack111lll1l_opy_ (u"ࠧࡌࡧࡼࡷࠥࡩࡡ࡯ࡰࡲࡸࠥࡩ࡯࠮ࡧࡻ࡭ࡸࡺࠠࡢࡵࠣࡥࡵࡶࠠࡷࡣ࡯ࡹࡪࡹࠬࠡࡷࡶࡩࠥࡧ࡮ࡺࠢࡲࡲࡪࠦࡰࡳࡱࡳࡩࡷࡺࡹࠡࡨࡵࡳࡲࠦࡻࡪࡦ࠿ࡷࡹࡸࡩ࡯ࡩࡁ࠰ࠥࡶࡡࡵࡪ࠿ࡷࡹࡸࡩ࡯ࡩࡁ࠰ࠥࡩࡵࡴࡶࡲࡱࡤ࡯ࡤ࠽ࡵࡷࡶ࡮ࡴࡧ࠿࠮ࠣࡷ࡭ࡧࡲࡦࡣࡥࡰࡪࡥࡩࡥ࠾ࡶࡸࡷ࡯࡮ࡨࡀࢀ࠰ࠥࡵ࡮࡭ࡻࠣࠦࡵࡧࡴࡩࠤࠣࡥࡳࡪࠠࠣࡥࡸࡷࡹࡵ࡭ࡠ࡫ࡧࠦࠥࡩࡡ࡯ࠢࡦࡳ࠲࡫ࡸࡪࡵࡷࠤࡹࡵࡧࡦࡶ࡫ࡩࡷ࠴ࠧ੖")
bstack1l1l11l11_opy_ = bstack111lll1l_opy_ (u"ࠨ࡝ࡌࡲࡻࡧ࡬ࡪࡦࠣࡥࡵࡶࠠࡱࡴࡲࡴࡪࡸࡴࡺ࡟ࠣࡷࡺࡶࡰࡰࡴࡷࡩࡩࠦࡰࡳࡱࡳࡩࡷࡺࡩࡦࡵࠣࡥࡷ࡫ࠠࡼ࡫ࡧࡀࡸࡺࡲࡪࡰࡪࡂ࠱ࠦࡰࡢࡶ࡫ࡀࡸࡺࡲࡪࡰࡪࡂ࠱ࠦࡣࡶࡵࡷࡳࡲࡥࡩࡥ࠾ࡶࡸࡷ࡯࡮ࡨࡀ࠯ࠤࡸ࡮ࡡࡳࡧࡤࡦࡱ࡫࡟ࡪࡦ࠿ࡷࡹࡸࡩ࡯ࡩࡁࢁ࠳ࠦࡆࡰࡴࠣࡱࡴࡸࡥࠡࡦࡨࡸࡦ࡯࡬ࡴࠢࡳࡰࡪࡧࡳࡦࠢࡹ࡭ࡸ࡯ࡴࠡࡪࡷࡸࡵࡹ࠺࠰࠱ࡺࡻࡼ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮࠱ࡧࡳࡨࡹ࠯ࡢࡲࡳ࠱ࡦࡻࡴࡰ࡯ࡤࡸࡪ࠵ࡡࡱࡲ࡬ࡹࡲ࠵ࡳࡦࡶ࠰ࡹࡵ࠳ࡴࡦࡵࡷࡷ࠴ࡹࡰࡦࡥ࡬ࡪࡾ࠳ࡡࡱࡲࠪ੗")
bstack11lll1_opy_ = bstack111lll1l_opy_ (u"ࠩ࡞ࡍࡳࡼࡡ࡭࡫ࡧࠤࡦࡶࡰࠡࡲࡵࡳࡵ࡫ࡲࡵࡻࡠࠤࡘࡻࡰࡱࡱࡵࡸࡪࡪࠠࡷࡣ࡯ࡹࡪࡹࠠࡰࡨࠣࡥࡵࡶࠠࡢࡴࡨࠤࡴ࡬ࠠࡼ࡫ࡧࡀࡸࡺࡲࡪࡰࡪࡂ࠱ࠦࡰࡢࡶ࡫ࡀࡸࡺࡲࡪࡰࡪࡂ࠱ࠦࡣࡶࡵࡷࡳࡲࡥࡩࡥ࠾ࡶࡸࡷ࡯࡮ࡨࡀ࠯ࠤࡸ࡮ࡡࡳࡧࡤࡦࡱ࡫࡟ࡪࡦ࠿ࡷࡹࡸࡩ࡯ࡩࡁࢁ࠳ࠦࡆࡰࡴࠣࡱࡴࡸࡥࠡࡦࡨࡸࡦ࡯࡬ࡴࠢࡳࡰࡪࡧࡳࡦࠢࡹ࡭ࡸ࡯ࡴࠡࡪࡷࡸࡵࡹ࠺࠰࠱ࡺࡻࡼ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡩ࡯࡮࠱ࡧࡳࡨࡹ࠯ࡢࡲࡳ࠱ࡦࡻࡴࡰ࡯ࡤࡸࡪ࠵ࡡࡱࡲ࡬ࡹࡲ࠵ࡳࡦࡶ࠰ࡹࡵ࠳ࡴࡦࡵࡷࡷ࠴ࡹࡰࡦࡥ࡬ࡪࡾ࠳ࡡࡱࡲࠪ੘")
bstack1l11l111_opy_ = bstack111lll1l_opy_ (u"࡙ࠪࡸ࡯࡮ࡨࠢࡨࡼ࡮ࡹࡴࡪࡰࡪࠤࡦࡶࡰࠡ࡫ࡧࠤࢀࢃࠠࡧࡱࡵࠤ࡭ࡧࡳࡩࠢ࠽ࠤࢀࢃ࠮ࠨਖ਼")
bstack1lll1llll_opy_ = bstack111lll1l_opy_ (u"ࠫࡆࡶࡰࠡࡗࡳࡰࡴࡧࡤࡦࡦࠣࡗࡺࡩࡣࡦࡵࡶࡪࡺࡲ࡬ࡺ࠰ࠣࡍࡉࠦ࠺ࠡࡽࢀࠫਗ਼")
bstack11l1lll1l_opy_ = bstack111lll1l_opy_ (u"࡛ࠬࡳࡪࡰࡪࠤࡆࡶࡰࠡ࠼ࠣࡿࢂ࠴ࠧਜ਼")
bstack1llll1l_opy_ = bstack111lll1l_opy_ (u"࠭ࡰࡢࡴࡤࡰࡱ࡫࡬ࡴࡒࡨࡶࡕࡲࡡࡵࡨࡲࡶࡲࠦࡩࡴࠢࡱࡳࡹࠦࡳࡶࡲࡳࡳࡷࡺࡥࡥࠢࡩࡳࡷࠦࡶࡢࡰ࡬ࡰࡱࡧࠠࡱࡻࡷ࡬ࡴࡴࠠࡵࡧࡶࡸࡸ࠲ࠠࡳࡷࡱࡲ࡮ࡴࡧࠡࡹ࡬ࡸ࡭ࠦࡰࡢࡴࡤࡰࡱ࡫࡬ࡑࡧࡵࡔࡱࡧࡴࡧࡱࡵࡱࠥࡃࠠ࠲ࠩੜ")
bstack1l1ll_opy_ = bstack111lll1l_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡦࡶࡪࡧࡴࡪࡰࡪࠤࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷࡀࠠࡼࡿࠪ੝")
bstack11ll1l_opy_ = bstack111lll1l_opy_ (u"ࠨࡅࡲࡹࡱࡪࠠ࡯ࡱࡷࠤࡨࡲ࡯ࡴࡧࠣࡦࡷࡵࡷࡴࡧࡵ࠾ࠥࢁࡽࠨਫ਼")
bstack1lll1l1_opy_ = bstack111lll1l_opy_ (u"ࠩࡆࡳࡺࡲࡤࠡࡰࡲࡸࠥ࡭ࡥࡵࠢࡵࡩࡦࡹ࡯࡯ࠢࡩࡳࡷࠦࡢࡦࡪࡤࡺࡪࠦࡦࡦࡣࡷࡹࡷ࡫ࠠࡧࡣ࡬ࡰࡺࡸࡥ࠯ࠢࡾࢁࠬ੟")
bstack11ll_opy_ = bstack111lll1l_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢࡺ࡬࡮ࡲࡥࠡࡩࡨࡸࡹ࡯࡮ࡨࠢࡵࡩࡸࡶ࡯࡯ࡵࡨࠤ࡫ࡸ࡯࡮ࠢࡤࡴ࡮ࠦࡣࡢ࡮࡯࠲ࠥࡋࡲࡳࡱࡵ࠾ࠥࢁࡽࠨ੠")
bstack1l111l1l_opy_ = bstack111lll1l_opy_ (u"࡚ࠫࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡴࡪࡲࡻࠥࡨࡵࡪ࡮ࡧࠤ࡚ࡘࡌ࠭ࠢࡤࡷࠥࡨࡵࡪ࡮ࡧࠤࡨࡧࡰࡢࡤ࡬ࡰ࡮ࡺࡹࠡ࡫ࡶࠤࡳࡵࡴࠡࡷࡶࡩࡩ࠴ࠧ੡")
bstack1l11111ll_opy_ = bstack111lll1l_opy_ (u"࡙ࠬࡥࡳࡸࡨࡶࠥࡹࡩࡥࡧࠣࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠮ࡻࡾࠫࠣ࡭ࡸࠦ࡮ࡰࡶࠣࡷࡦࡳࡥࠡࡣࡶࠤࡨࡲࡩࡦࡰࡷࠤࡸ࡯ࡤࡦࠢࡥࡹ࡮ࡲࡤࡏࡣࡰࡩ࠭ࢁࡽࠪࠩ੢")
bstack11ll11l11_opy_ = bstack111lll1l_opy_ (u"࠭ࡖࡪࡧࡺࠤࡧࡻࡩ࡭ࡦࠣࡳࡳࠦࡂࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࠥࡪࡡࡴࡪࡥࡳࡦࡸࡤ࠻ࠢࡾࢁࠬ੣")
bstack111111_opy_ = bstack111lll1l_opy_ (u"ࠧࡖࡰࡤࡦࡱ࡫ࠠࡵࡱࠣࡥࡨࡩࡥࡴࡵࠣࡥࠥࡶࡲࡪࡸࡤࡸࡪࠦࡤࡰ࡯ࡤ࡭ࡳࡀࠠࡼࡿࠣ࠲࡙ࠥࡥࡵࠢࡷ࡬ࡪࠦࡦࡰ࡮࡯ࡳࡼ࡯࡮ࡨࠢࡦࡳࡳ࡬ࡩࡨࠢ࡬ࡲࠥࡿ࡯ࡶࡴࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰ࡼࡱࡱࠦࡦࡪ࡮ࡨ࠾ࠥࡢ࡮࠮࠯࠰࠱࠲࠳࠭࠮࠯࠰࠱ࠥࡢ࡮ࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰ࠿ࠦࡴࡳࡷࡨࠤࡡࡴ࠭࠮࠯࠰࠱࠲࠳࠭࠮࠯࠰ࠫ੤")
bstack1l1llll1l_opy_ = bstack111lll1l_opy_ (u"ࠨࡕࡲࡱࡪࡺࡨࡪࡰࡪࠤࡼ࡫࡮ࡵࠢࡺࡶࡴࡴࡧࠡࡹ࡫࡭ࡱ࡫ࠠࡦࡺࡨࡧࡺࡺࡩ࡯ࡩࠣ࡫ࡪࡺ࡟࡯ࡷࡧ࡫ࡪࡥ࡬ࡰࡥࡤࡰࡤ࡫ࡲࡳࡱࡵࠤ࠿ࠦࡻࡾࠩ੥")
bstack11l1111_opy_ = bstack111lll1l_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡸ࡫࡮ࡥࡡࡤࡱࡵࡲࡩࡵࡷࡧࡩࡤ࡫ࡶࡦࡰࡷࠤ࡫ࡵࡲࠡࡕࡇࡏࡘ࡫ࡴࡶࡲࠣࡿࢂࠨ੦")
bstack11l1ll1l_opy_ = bstack111lll1l_opy_ (u"ࠥࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥࡹࡥ࡯ࡦࡢࡥࡲࡶ࡬ࡪࡶࡸࡨࡪࡥࡥࡷࡧࡱࡸࠥ࡬࡯ࡳࠢࡖࡈࡐ࡚ࡥࡴࡶࡄࡸࡹ࡫࡭ࡱࡶࡨࡨࠥࢁࡽࠣ੧")
bstack1l111l111_opy_ = bstack111lll1l_opy_ (u"ࠦࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡳࡦࡰࡧࡣࡦࡳࡰ࡭࡫ࡷࡹࡩ࡫࡟ࡦࡸࡨࡲࡹࠦࡦࡰࡴࠣࡗࡉࡑࡔࡦࡵࡷࡗࡺࡩࡣࡦࡵࡶࡪࡺࡲࠠࡼࡿࠥ੨")
bstack1ll11111l_opy_ = bstack111lll1l_opy_ (u"ࠧࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡧ࡫ࡵࡩࡤࡸࡥࡲࡷࡨࡷࡹࠦࡻࡾࠤ੩")
bstack1l_opy_ = bstack111lll1l_opy_ (u"ࠨࡐࡐࡕࡗࠤࡊࡼࡥ࡯ࡶࠣࡿࢂࠦࡲࡦࡵࡳࡳࡳࡹࡥࠡ࠼ࠣࡿࢂࠨ੪")
bstack11ll11l1l_opy_ = bstack111lll1l_opy_ (u"ࠧࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡧࡴࡴࡦࡪࡩࡸࡶࡪࠦࡰࡳࡱࡻࡽࠥࡹࡥࡵࡶ࡬ࡲ࡬ࡹࠬࠡࡧࡵࡶࡴࡸ࠺ࠡࡽࢀࠫ੫")
bstack11l1l_opy_ = bstack111lll1l_opy_ (u"ࠨࡔࡨࡷࡵࡵ࡮ࡴࡧࠣࡪࡷࡵ࡭ࠡ࠱ࡱࡩࡽࡺ࡟ࡩࡷࡥࡷࠥࢁࡽࠨ੬")
bstack111lll111_opy_ = bstack111lll1l_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤ࡬࡫ࡴࡵ࡫ࡱ࡫ࠥࡸࡥࡴࡲࡲࡲࡸ࡫ࠠࡧࡴࡲࡱࠥ࠵࡮ࡦࡺࡷࡣ࡭ࡻࡢࡴ࠼ࠣࡿࢂ࠭੭")
bstack1ll11llll_opy_ = bstack111lll1l_opy_ (u"ࠪࡒࡪࡧࡲࡦࡵࡷࠤ࡭ࡻࡢࠡࡣ࡯ࡰࡴࡩࡡࡵࡧࡧࠤ࡮ࡹ࠺ࠡࡽࢀࠫ੮")
bstack11ll111l_opy_ = bstack111lll1l_opy_ (u"ࠫࡊࡘࡒࡐࡔࠣࡍࡓࠦࡁࡍࡎࡒࡇࡆ࡚ࡅࠡࡊࡘࡆࠥࢁࡽࠨ੯")
bstack1l1l1l1_opy_ = bstack111lll1l_opy_ (u"ࠬࡒࡡࡵࡧࡱࡧࡾࠦ࡯ࡧࠢ࡫ࡹࡧࡀࠠࡼࡿࠣ࡭ࡸࡀࠠࡼࡿࠪੰ")
bstack1l11111_opy_ = bstack111lll1l_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡩࡨࡸࡹ࡯࡮ࡨࠢ࡯ࡥࡹ࡫࡮ࡤࡻࠣࡪࡴࡸࠠࡼࡿࠣ࡬ࡺࡨ࠺ࠡࡽࢀࠫੱ")
bstack1111l1l1_opy_ = bstack111lll1l_opy_ (u"ࠧࡉࡷࡥࠤࡺࡸ࡬ࠡࡥ࡫ࡥࡳ࡭ࡥࡥࠢࡷࡳࠥࡺࡨࡦࠢࡲࡴࡹ࡯࡭ࡢ࡮ࠣ࡬ࡺࡨ࠺ࠡࡽࢀࠫੲ")
bstack1ll1111_opy_ = bstack111lll1l_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡸࡪ࡬ࡰࡪࠦࡳࡦࡶࡷ࡭ࡳ࡭ࠠࡵࡪࡨࠤࡴࡶࡴࡪ࡯ࡤࡰࠥ࡮ࡵࡣࠢࡸࡶࡱࡀࠠࡼࡿࠪੳ")
bstack111ll11l1_opy_ = bstack111lll1l_opy_ (u"ࠩࡉࡥ࡮ࡲࡥࡥࠢࡷࡳࠥ࡭ࡥࡵࠢࡶࡩࡸࡹࡩࡰࡰࠣࡰ࡮ࡹࡴࡴ࠼ࠣࡿࢂ࠭ੴ")
bstack1llllll1_opy_ = bstack111lll1l_opy_ (u"ࠪࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦࡧࡦࡰࡨࡶࡦࡺࡥࠡࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠠࡣࡷ࡬ࡰࡩࠦࡡࡳࡶ࡬ࡪࡦࡩࡴࡴ࠼ࠣࡿࢂ࠭ੵ")
bstack11ll1l1l_opy_ = bstack111lll1l_opy_ (u"࡚ࠫࡴࡡࡣ࡮ࡨࠤࡹࡵࠠࡱࡣࡵࡷࡪࠦࡰࡢࡥࠣࡪ࡮ࡲࡥࠡࡽࢀ࠲ࠥࡋࡲࡳࡱࡵࠤ࠲ࠦࡻࡾࠩ੶")
bstackl_opy_ = bstack111lll1l_opy_ (u"ࠬࠦࠠ࠰ࠬࠣࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃࠠࠫ࠱࡟ࡲࠥࠦࡩࡧࠪࡳࡥ࡬࡫ࠠ࠾࠿ࡀࠤࡻࡵࡩࡥࠢ࠳࠭ࠥࢁ࡜࡯ࠢࠣࠤࡹࡸࡹࡼ࡞ࡱࠤࡨࡵ࡮ࡴࡶࠣࡪࡸࠦ࠽ࠡࡴࡨࡵࡺ࡯ࡲࡦࠪ࡟ࠫ࡫ࡹ࡜ࠨࠫ࠾ࡠࡳࠦࠠࠡࠢࠣࡪࡸ࠴ࡡࡱࡲࡨࡲࡩࡌࡩ࡭ࡧࡖࡽࡳࡩࠨࡣࡵࡷࡥࡨࡱ࡟ࡱࡣࡷ࡬࠱ࠦࡊࡔࡑࡑ࠲ࡸࡺࡲࡪࡰࡪ࡭࡫ࡿࠨࡱࡡ࡬ࡲࡩ࡫ࡸࠪࠢ࠮ࠤࠧࡀࠢࠡ࠭ࠣࡎࡘࡕࡎ࠯ࡵࡷࡶ࡮ࡴࡧࡪࡨࡼࠬࡏ࡙ࡏࡏ࠰ࡳࡥࡷࡹࡥࠩࠪࡤࡻࡦ࡯ࡴࠡࡰࡨࡻࡕࡧࡧࡦ࠴࠱ࡩࡻࡧ࡬ࡶࡣࡷࡩ࠭ࠨࠨࠪࠢࡀࡂࠥࢁࡽࠣ࠮ࠣࡠࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧ࡭ࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡆࡨࡸࡦ࡯࡬ࡴࠤࢀࡠࠬ࠯ࠩࠪ࡝ࠥ࡬ࡦࡹࡨࡦࡦࡢ࡭ࡩࠨ࡝ࠪࠢ࠮ࠤࠧ࠲࡜࡝ࡰࠥ࠭ࡡࡴࠠࠡࠢࠣࢁࡨࡧࡴࡤࡪࠫࡩࡽ࠯ࡻ࡝ࡰࠣࠤࠥࠦࡽ࡝ࡰࠣࠤࢂࡢ࡮ࠡࠢ࠲࠮ࠥࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾ࠢ࠭࠳ࠬ੷")
bstack111_opy_ = bstack111lll1l_opy_ (u"࠭࡜࡯࠱࠭ࠤࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽ࠡࠬ࠲ࡠࡳࡩ࡯࡯ࡵࡷࠤࡧࡹࡴࡢࡥ࡮ࡣࡵࡧࡴࡩࠢࡀࠤࡵࡸ࡯ࡤࡧࡶࡷ࠳ࡧࡲࡨࡸ࡞ࡴࡷࡵࡣࡦࡵࡶ࠲ࡦࡸࡧࡷ࠰࡯ࡩࡳ࡭ࡴࡩࠢ࠰ࠤ࠸ࡣ࡜࡯ࡥࡲࡲࡸࡺࠠࡣࡵࡷࡥࡨࡱ࡟ࡤࡣࡳࡷࠥࡃࠠࡱࡴࡲࡧࡪࡹࡳ࠯ࡣࡵ࡫ࡻࡡࡰࡳࡱࡦࡩࡸࡹ࠮ࡢࡴࡪࡺ࠳ࡲࡥ࡯ࡩࡷ࡬ࠥ࠳ࠠ࠲࡟࡟ࡲࡨࡵ࡮ࡴࡶࠣࡴࡤ࡯࡮ࡥࡧࡻࠤࡂࠦࡰࡳࡱࡦࡩࡸࡹ࠮ࡢࡴࡪࡺࡠࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹ࠲ࡱ࡫࡮ࡨࡶ࡫ࠤ࠲ࠦ࠲࡞࡞ࡱࡴࡷࡵࡣࡦࡵࡶ࠲ࡦࡸࡧࡷࠢࡀࠤࡵࡸ࡯ࡤࡧࡶࡷ࠳ࡧࡲࡨࡸ࠱ࡷࡱ࡯ࡣࡦࠪ࠳࠰ࠥࡶࡲࡰࡥࡨࡷࡸ࠴ࡡࡳࡩࡹ࠲ࡱ࡫࡮ࡨࡶ࡫ࠤ࠲ࠦ࠳ࠪ࡞ࡱࡧࡴࡴࡳࡵࠢ࡬ࡱࡵࡵࡲࡵࡡࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹ࠺࡟ࡣࡵࡷࡥࡨࡱࠠ࠾ࠢࡵࡩࡶࡻࡩࡳࡧࠫࠦࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࠣࠫ࠾ࡠࡳ࡯࡭ࡱࡱࡵࡸࡤࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵ࠶ࡢࡦࡸࡺࡡࡤ࡭࠱ࡧ࡭ࡸ࡯࡮࡫ࡸࡱ࠳ࡲࡡࡶࡰࡦ࡬ࠥࡃࠠࡢࡵࡼࡲࡨࠦࠨ࡭ࡣࡸࡲࡨ࡮ࡏࡱࡶ࡬ࡳࡳࡹࠩࠡ࠿ࡁࠤࢀࡢ࡮࡭ࡧࡷࠤࡨࡧࡰࡴ࠽࡟ࡲࡹࡸࡹࠡࡽ࡟ࡲࡨࡧࡰࡴࠢࡀࠤࡏ࡙ࡏࡏ࠰ࡳࡥࡷࡹࡥࠩࡤࡶࡸࡦࡩ࡫ࡠࡥࡤࡴࡸ࠯࡜࡯ࠢࠣࢁࠥࡩࡡࡵࡥ࡫ࠬࡪࡾࠩࠡࡽ࡟ࡲࠥࠦࠠࠡࡿ࡟ࡲࠥࠦࡲࡦࡶࡸࡶࡳࠦࡡࡸࡣ࡬ࡸࠥ࡯࡭ࡱࡱࡵࡸࡤࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵ࠶ࡢࡦࡸࡺࡡࡤ࡭࠱ࡧ࡭ࡸ࡯࡮࡫ࡸࡱ࠳ࡩ࡯࡯ࡰࡨࡧࡹ࠮ࡻ࡝ࡰࠣࠤࠥࠦࡷࡴࡇࡱࡨࡵࡵࡩ࡯ࡶ࠽ࠤࡥࡽࡳࡴ࠼࠲࠳ࡨࡪࡰ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰ࠳ࡵࡲࡡࡺࡹࡵ࡭࡬࡮ࡴࡀࡥࡤࡴࡸࡃࠤࡼࡧࡱࡧࡴࡪࡥࡖࡔࡌࡇࡴࡳࡰࡰࡰࡨࡲࡹ࠮ࡊࡔࡑࡑ࠲ࡸࡺࡲࡪࡰࡪ࡭࡫ࡿࠨࡤࡣࡳࡷ࠮࠯ࡽࡡ࠮࡟ࡲࠥࠦࠠࠡ࠰࠱࠲ࡱࡧࡵ࡯ࡥ࡫ࡓࡵࡺࡩࡰࡰࡶࡠࡳࠦࠠࡾࠫ࡟ࡲࢂࡢ࡮࠰ࠬࠣࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃ࠽࠾࠿ࡀࡁࡂࡃࠠࠫ࠱࡟ࡲࠬ੸")
from ._version import __version__
bstack111ll1111_opy_ = None
CONFIG = {}
bstack1l1ll1ll_opy_ = {}
bstack1ll11l1l_opy_ = {}
bstack11l11l111_opy_ = None
bstack1llll111_opy_ = None
bstack11ll1llll_opy_ = None
bstack1l1l1111_opy_ = -1
bstack1llll1_opy_ = bstack111l1lll1_opy_
bstack1l1lll1_opy_ = 1
bstack111l1ll11_opy_ = False
bstack1lll1l1ll_opy_ = False
bstack1lll1l11l_opy_ = bstack111lll1l_opy_ (u"ࠧࠨ੹")
bstack111l1ll1_opy_ = bstack111lll1l_opy_ (u"ࠨࠩ੺")
bstack111llll11_opy_ = False
bstack1lllll111_opy_ = True
bstack1ll11l111_opy_ = bstack111lll1l_opy_ (u"ࠩࠪ੻")
bstack1lll_opy_ = []
bstack1l111ll1_opy_ = bstack111lll1l_opy_ (u"ࠪࠫ੼")
bstack1l1111l1_opy_ = False
bstack1ll11ll1l_opy_ = None
bstack111ll11l_opy_ = None
bstack11111l11_opy_ = -1
bstack1lll1l111_opy_ = os.path.join(os.path.expanduser(bstack111lll1l_opy_ (u"ࠫࢃ࠭੽")), bstack111lll1l_opy_ (u"ࠬ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠬ੾"), bstack111lll1l_opy_ (u"࠭࠮ࡳࡱࡥࡳࡹ࠳ࡲࡦࡲࡲࡶࡹ࠳ࡨࡦ࡮ࡳࡩࡷ࠴ࡪࡴࡱࡱࠫ੿"))
bstack1111l11l_opy_ = []
bstack1ll1ll11_opy_ = False
bstack1lllll1l1_opy_ = False
bstack111l111_opy_ = None
bstack1llll1l1l_opy_ = None
bstack1l1lll_opy_ = None
bstack111lll11_opy_ = None
bstack1l11ll1_opy_ = None
bstack11l1l111_opy_ = None
bstack1l11lllll_opy_ = None
bstack1l1llllll_opy_ = None
bstack111lll11l_opy_ = None
bstack111111ll_opy_ = None
bstack1ll1l1ll_opy_ = None
bstack1lll111ll_opy_ = None
bstack1111ll1l_opy_ = None
bstack111ll1_opy_ = None
bstack1l1lll111_opy_ = None
bstack1l1ll1lll_opy_ = None
bstack111l11l_opy_ = None
bstack1l1l11_opy_ = None
bstack1l111ll11_opy_ = bstack111lll1l_opy_ (u"ࠢࠣ઀")
class bstack1lll111l1_opy_(threading.Thread):
  def run(self):
    self.exc = None
    try:
      self.ret = self._target(*self._args, **self._kwargs)
    except Exception as e:
      self.exc = e
  def join(self, timeout=None):
    super(bstack1lll111l1_opy_, self).join(timeout)
    if self.exc:
      raise self.exc
    return self.ret
logger = logging.getLogger(__name__)
logging.basicConfig(level=bstack1llll1_opy_,
                    format=bstack111lll1l_opy_ (u"ࠨ࡞ࡱࠩ࠭ࡧࡳࡤࡶ࡬ࡱࡪ࠯ࡳࠡ࡝ࠨࠬࡳࡧ࡭ࡦࠫࡶࡡࡠࠫࠨ࡭ࡧࡹࡩࡱࡴࡡ࡮ࡧࠬࡷࡢࠦ࠭ࠡࠧࠫࡱࡪࡹࡳࡢࡩࡨ࠭ࡸ࠭ઁ"),
                    datefmt=bstack111lll1l_opy_ (u"ࠩࠨࡌ࠿ࠫࡍ࠻ࠧࡖࠫં"))
def bstack11llllll1_opy_():
  global CONFIG
  global bstack1llll1_opy_
  if bstack111lll1l_opy_ (u"ࠪࡰࡴ࡭ࡌࡦࡸࡨࡰࠬઃ") in CONFIG:
    bstack1llll1_opy_ = bstack11l1l1ll_opy_[CONFIG[bstack111lll1l_opy_ (u"ࠫࡱࡵࡧࡍࡧࡹࡩࡱ࠭઄")]]
    logging.getLogger().setLevel(bstack1llll1_opy_)
def bstack11l11l1ll_opy_():
  global CONFIG
  global bstack1ll1ll11_opy_
  bstack1l1l1lll1_opy_ = bstack11lllll11_opy_(CONFIG)
  if(bstack111lll1l_opy_ (u"ࠬࡹ࡫ࡪࡲࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧઅ") in bstack1l1l1lll1_opy_ and str(bstack1l1l1lll1_opy_[bstack111lll1l_opy_ (u"࠭ࡳ࡬࡫ࡳࡗࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨઆ")]).lower() == bstack111lll1l_opy_ (u"ࠧࡵࡴࡸࡩࠬઇ")):
    bstack1ll1ll11_opy_ = True
def bstack1l1l11111_opy_():
  from appium.version import version as appium_version
  return version.parse(appium_version)
def bstack1l111lll_opy_():
  from selenium import webdriver
  return version.parse(webdriver.__version__)
def bstack1ll1l1ll1_opy_():
  args = sys.argv
  for i in range(len(args)):
    if bstack111lll1l_opy_ (u"ࠣ࠯࠰ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡥࡲࡲ࡫࡯ࡧࡧ࡫࡯ࡩࠧઈ") == args[i].lower() or bstack111lll1l_opy_ (u"ࠤ࠰࠱ࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡧࡴࡴࡦࡪࡩࠥઉ") == args[i].lower():
      path = args[i+1]
      sys.argv.remove(args[i])
      sys.argv.remove(path)
      global bstack1ll11l111_opy_
      bstack1ll11l111_opy_ += bstack111lll1l_opy_ (u"ࠪ࠱࠲ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡇࡴࡴࡦࡪࡩࡉ࡭ࡱ࡫ࠠࠨઊ") + path
      return path
  return None
bstack1l11l1l1_opy_ = re.compile(bstack111lll1l_opy_ (u"ࡶࠧ࠴ࠪࡀ࡞ࠧࡿ࠭࠴ࠪࡀࠫࢀ࠲࠯ࡅࠢઋ"))
def bstack1l11ll11l_opy_(loader, node):
    value = loader.construct_scalar(node)
    for group in bstack1l11l1l1_opy_.findall(value):
        if group is not None and os.environ.get(group) is not None:
          value = value.replace(bstack111lll1l_opy_ (u"ࠧࠪࡻࠣઌ") + group + bstack111lll1l_opy_ (u"ࠨࡽࠣઍ"), os.environ.get(group))
    return value
def bstack11ll1111l_opy_():
  bstack11ll11l1_opy_ = bstack1ll1l1ll1_opy_()
  if bstack11ll11l1_opy_ and os.path.exists(os.path.abspath(bstack11ll11l1_opy_)):
    fileName = bstack11ll11l1_opy_
  if bstack111lll1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡃࡐࡐࡉࡍࡌࡥࡆࡊࡎࡈࠫ઎") in os.environ and os.path.exists(os.path.abspath(os.environ[bstack111lll1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡄࡑࡑࡊࡎࡍ࡟ࡇࡋࡏࡉࠬએ")])) and not bstack111lll1l_opy_ (u"ࠩࡩ࡭ࡱ࡫ࡎࡢ࡯ࡨࠫઐ") in locals():
    fileName = os.environ[bstack111lll1l_opy_ (u"ࠪࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡆࡓࡓࡌࡉࡈࡡࡉࡍࡑࡋࠧઑ")]
  if bstack111lll1l_opy_ (u"ࠫ࡫࡯࡬ࡦࡐࡤࡱࡪ࠭઒") in locals():
    bstack111ll1ll_opy_ = os.path.abspath(fileName)
  else:
    bstack111ll1ll_opy_ = bstack111lll1l_opy_ (u"ࠬ࠭ઓ")
  bstack1l1l11ll_opy_ = os.getcwd()
  bstack1llll11l_opy_ = bstack111lll1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡿ࡭࡭ࠩઔ")
  bstack1l1l1ll1_opy_ = bstack111lll1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡹࡢ࡯࡯ࠫક")
  while (not os.path.exists(bstack111ll1ll_opy_)) and bstack1l1l11ll_opy_ != bstack111lll1l_opy_ (u"ࠣࠤખ"):
    bstack111ll1ll_opy_ = os.path.join(bstack1l1l11ll_opy_, bstack1llll11l_opy_)
    if not os.path.exists(bstack111ll1ll_opy_):
      bstack111ll1ll_opy_ = os.path.join(bstack1l1l11ll_opy_, bstack1l1l1ll1_opy_)
    if bstack1l1l11ll_opy_ != os.path.dirname(bstack1l1l11ll_opy_):
      bstack1l1l11ll_opy_ = os.path.dirname(bstack1l1l11ll_opy_)
    else:
      bstack1l1l11ll_opy_ = bstack111lll1l_opy_ (u"ࠤࠥગ")
  if not os.path.exists(bstack111ll1ll_opy_):
    bstack1l11ll1l_opy_(
      bstack11lll1111_opy_.format(os.getcwd()))
  try:
    with open(bstack111ll1ll_opy_, bstack111lll1l_opy_ (u"ࠪࡶࠬઘ")) as stream:
        yaml.add_implicit_resolver(bstack111lll1l_opy_ (u"ࠦࠦࡶࡡࡵࡪࡨࡼࠧઙ"), bstack1l11l1l1_opy_)
        yaml.add_constructor(bstack111lll1l_opy_ (u"ࠧࠧࡰࡢࡶ࡫ࡩࡽࠨચ"), bstack1l11ll11l_opy_)
        config = yaml.load(stream, yaml.FullLoader)
        return config
  except:
    with open(bstack111ll1ll_opy_, bstack111lll1l_opy_ (u"࠭ࡲࠨછ")) as stream:
      try:
        config = yaml.safe_load(stream)
        return config
      except yaml.YAMLError as exc:
        bstack1l11ll1l_opy_(bstack1111l1l_opy_.format(str(exc)))
def bstack1l1l1l1l1_opy_(config):
  bstack111l111ll_opy_ = bstack111ll1l11_opy_(config)
  for option in list(bstack111l111ll_opy_):
    if option.lower() in bstack111l11l1_opy_ and option != bstack111l11l1_opy_[option.lower()]:
      bstack111l111ll_opy_[bstack111l11l1_opy_[option.lower()]] = bstack111l111ll_opy_[option]
      del bstack111l111ll_opy_[option]
  return config
def bstack11l111l_opy_():
  global bstack1ll11l1l_opy_
  for key, bstack111l111l1_opy_ in bstack1l1ll111l_opy_.items():
    if isinstance(bstack111l111l1_opy_, list):
      for var in bstack111l111l1_opy_:
        if var in os.environ and os.environ[var] and str(os.environ[var]).strip():
          bstack1ll11l1l_opy_[key] = os.environ[var]
          break
    elif bstack111l111l1_opy_ in os.environ and os.environ[bstack111l111l1_opy_] and str(os.environ[bstack111l111l1_opy_]).strip():
      bstack1ll11l1l_opy_[key] = os.environ[bstack111l111l1_opy_]
  if bstack111lll1l_opy_ (u"ࠧࡃࡔࡒ࡛ࡘࡋࡒࡔࡖࡄࡇࡐࡥࡌࡐࡅࡄࡐࡤࡏࡄࡆࡐࡗࡍࡋࡏࡅࡓࠩજ") in os.environ:
    bstack1ll11l1l_opy_[bstack111lll1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬઝ")] = {}
    bstack1ll11l1l_opy_[bstack111lll1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ઞ")][bstack111lll1l_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬટ")] = os.environ[bstack111lll1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡐࡔࡉࡁࡍࡡࡌࡈࡊࡔࡔࡊࡈࡌࡉࡗ࠭ઠ")]
def bstack11l1lll_opy_():
  global bstack1l1ll1ll_opy_
  global bstack1ll11l111_opy_
  for idx, val in enumerate(sys.argv):
    if idx<len(sys.argv) and bstack111lll1l_opy_ (u"ࠬ࠳࠭ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴࡬ࡰࡥࡤࡰࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨડ").lower() == val.lower():
      bstack1l1ll1ll_opy_[bstack111lll1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪઢ")] = {}
      bstack1l1ll1ll_opy_[bstack111lll1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫણ")][bstack111lll1l_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪત")] = sys.argv[idx+1]
      del sys.argv[idx:idx+2]
      break
  for key, bstack1l1l1_opy_ in bstack111l1l1l_opy_.items():
    if isinstance(bstack1l1l1_opy_, list):
      for idx, val in enumerate(sys.argv):
        for var in bstack1l1l1_opy_:
          if idx<len(sys.argv) and bstack111lll1l_opy_ (u"ࠩ࠰࠱ࠬથ") + var.lower() == val.lower() and not key in bstack1l1ll1ll_opy_:
            bstack1l1ll1ll_opy_[key] = sys.argv[idx+1]
            bstack1ll11l111_opy_ += bstack111lll1l_opy_ (u"ࠪࠤ࠲࠳ࠧદ") + var + bstack111lll1l_opy_ (u"ࠫࠥ࠭ધ") + sys.argv[idx+1]
            del sys.argv[idx:idx+2]
            break
    else:
      for idx, val in enumerate(sys.argv):
        if idx<len(sys.argv) and bstack111lll1l_opy_ (u"ࠬ࠳࠭ࠨન") + bstack1l1l1_opy_.lower() == val.lower() and not key in bstack1l1ll1ll_opy_:
          bstack1l1ll1ll_opy_[key] = sys.argv[idx+1]
          bstack1ll11l111_opy_ += bstack111lll1l_opy_ (u"࠭ࠠ࠮࠯ࠪ઩") + bstack1l1l1_opy_ + bstack111lll1l_opy_ (u"ࠧࠡࠩપ") + sys.argv[idx+1]
          del sys.argv[idx:idx+2]
def bstack1ll111l11_opy_(config):
  bstack1lll11_opy_ = config.keys()
  for bstack1lll111l_opy_, bstack11ll1l1ll_opy_ in bstack1llll1l11_opy_.items():
    if bstack11ll1l1ll_opy_ in bstack1lll11_opy_:
      config[bstack1lll111l_opy_] = config[bstack11ll1l1ll_opy_]
      del config[bstack11ll1l1ll_opy_]
  for bstack1lll111l_opy_, bstack11ll1l1ll_opy_ in bstack111ll1ll1_opy_.items():
    if isinstance(bstack11ll1l1ll_opy_, list):
      for bstack111l1l11l_opy_ in bstack11ll1l1ll_opy_:
        if bstack111l1l11l_opy_ in bstack1lll11_opy_:
          config[bstack1lll111l_opy_] = config[bstack111l1l11l_opy_]
          del config[bstack111l1l11l_opy_]
          break
    elif bstack11ll1l1ll_opy_ in bstack1lll11_opy_:
        config[bstack1lll111l_opy_] = config[bstack11ll1l1ll_opy_]
        del config[bstack11ll1l1ll_opy_]
  for bstack111l1l11l_opy_ in list(config):
    for bstack1111111l_opy_ in bstack11111ll1_opy_:
      if bstack111l1l11l_opy_.lower() == bstack1111111l_opy_.lower() and bstack111l1l11l_opy_ != bstack1111111l_opy_:
        config[bstack1111111l_opy_] = config[bstack111l1l11l_opy_]
        del config[bstack111l1l11l_opy_]
  bstack1ll1ll1_opy_ = []
  if bstack111lll1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫફ") in config:
    bstack1ll1ll1_opy_ = config[bstack111lll1l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬબ")]
  for platform in bstack1ll1ll1_opy_:
    for bstack111l1l11l_opy_ in list(platform):
      for bstack1111111l_opy_ in bstack11111ll1_opy_:
        if bstack111l1l11l_opy_.lower() == bstack1111111l_opy_.lower() and bstack111l1l11l_opy_ != bstack1111111l_opy_:
          platform[bstack1111111l_opy_] = platform[bstack111l1l11l_opy_]
          del platform[bstack111l1l11l_opy_]
  for bstack1lll111l_opy_, bstack11ll1l1ll_opy_ in bstack111ll1ll1_opy_.items():
    for platform in bstack1ll1ll1_opy_:
      if isinstance(bstack11ll1l1ll_opy_, list):
        for bstack111l1l11l_opy_ in bstack11ll1l1ll_opy_:
          if bstack111l1l11l_opy_ in platform:
            platform[bstack1lll111l_opy_] = platform[bstack111l1l11l_opy_]
            del platform[bstack111l1l11l_opy_]
            break
      elif bstack11ll1l1ll_opy_ in platform:
        platform[bstack1lll111l_opy_] = platform[bstack11ll1l1ll_opy_]
        del platform[bstack11ll1l1ll_opy_]
  for bstack111ll111l_opy_ in bstack11l111111_opy_:
    if bstack111ll111l_opy_ in config:
      if not bstack11l111111_opy_[bstack111ll111l_opy_] in config:
        config[bstack11l111111_opy_[bstack111ll111l_opy_]] = {}
      config[bstack11l111111_opy_[bstack111ll111l_opy_]].update(config[bstack111ll111l_opy_])
      del config[bstack111ll111l_opy_]
  for platform in bstack1ll1ll1_opy_:
    for bstack111ll111l_opy_ in bstack11l111111_opy_:
      if bstack111ll111l_opy_ in list(platform):
        if not bstack11l111111_opy_[bstack111ll111l_opy_] in platform:
          platform[bstack11l111111_opy_[bstack111ll111l_opy_]] = {}
        platform[bstack11l111111_opy_[bstack111ll111l_opy_]].update(platform[bstack111ll111l_opy_])
        del platform[bstack111ll111l_opy_]
  config = bstack1l1l1l1l1_opy_(config)
  return config
def bstack1ll1lll1l_opy_(config):
  global bstack111l1ll1_opy_
  if bstack111lll1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡎࡲࡧࡦࡲࠧભ") in config and str(config[bstack111lll1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࠨમ")]).lower() != bstack111lll1l_opy_ (u"ࠬ࡬ࡡ࡭ࡵࡨࠫય"):
    if not bstack111lll1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪર") in config:
      config[bstack111lll1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡔࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫ઱")] = {}
    if not bstack111lll1l_opy_ (u"ࠨ࡮ࡲࡧࡦࡲࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪલ") in config[bstack111lll1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ળ")]:
      bstack11l11ll1_opy_ = datetime.datetime.now()
      bstack111ll1l_opy_ = bstack11l11ll1_opy_.strftime(bstack111lll1l_opy_ (u"ࠪࠩࡩࡥࠥࡣࡡࠨࡌࠪࡓࠧ઴"))
      hostname = socket.gethostname()
      bstack1ll1111ll_opy_ = bstack111lll1l_opy_ (u"ࠫࠬવ").join(random.choices(string.ascii_lowercase + string.digits, k=4))
      identifier = bstack111lll1l_opy_ (u"ࠬࢁࡽࡠࡽࢀࡣࢀࢃࠧશ").format(bstack111ll1l_opy_, hostname, bstack1ll1111ll_opy_)
      config[bstack111lll1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࡒࡴࡹ࡯࡯࡯ࡵࠪષ")][bstack111lll1l_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩસ")] = identifier
    bstack111l1ll1_opy_ = config[bstack111lll1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡕࡷࡥࡨࡱࡌࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬહ")][bstack111lll1l_opy_ (u"ࠩ࡯ࡳࡨࡧ࡬ࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ઺")]
  return config
def bstack1l1l1l11l_opy_():
  if (
    isinstance(os.getenv(bstack111lll1l_opy_ (u"ࠪࡎࡊࡔࡋࡊࡐࡖࡣ࡚ࡘࡌࠨ઻")), str) and len(os.getenv(bstack111lll1l_opy_ (u"ࠫࡏࡋࡎࡌࡋࡑࡗࡤ࡛ࡒࡍ઼ࠩ"))) > 0
  ) or (
    isinstance(os.getenv(bstack111lll1l_opy_ (u"ࠬࡐࡅࡏࡍࡌࡒࡘࡥࡈࡐࡏࡈࠫઽ")), str) and len(os.getenv(bstack111lll1l_opy_ (u"࠭ࡊࡆࡐࡎࡍࡓ࡙࡟ࡉࡑࡐࡉࠬા"))) > 0
  ):
    return os.getenv(bstack111lll1l_opy_ (u"ࠧࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗ࠭િ"), 0)
  if str(os.getenv(bstack111lll1l_opy_ (u"ࠨࡅࡌࠫી"))).lower() == bstack111lll1l_opy_ (u"ࠩࡷࡶࡺ࡫ࠧુ") and str(os.getenv(bstack111lll1l_opy_ (u"ࠪࡇࡎࡘࡃࡍࡇࡆࡍࠬૂ"))).lower() == bstack111lll1l_opy_ (u"ࠫࡹࡸࡵࡦࠩૃ"):
    return os.getenv(bstack111lll1l_opy_ (u"ࠬࡉࡉࡓࡅࡏࡉࡤࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࠨૄ"), 0)
  if str(os.getenv(bstack111lll1l_opy_ (u"࠭ࡃࡊࠩૅ"))).lower() == bstack111lll1l_opy_ (u"ࠧࡵࡴࡸࡩࠬ૆") and str(os.getenv(bstack111lll1l_opy_ (u"ࠨࡖࡕࡅ࡛ࡏࡓࠨે"))).lower() == bstack111lll1l_opy_ (u"ࠩࡷࡶࡺ࡫ࠧૈ"):
    return os.getenv(bstack111lll1l_opy_ (u"ࠪࡘࡗࡇࡖࡊࡕࡢࡆ࡚ࡏࡌࡅࡡࡑ࡙ࡒࡈࡅࡓࠩૉ"), 0)
  if str(os.getenv(bstack111lll1l_opy_ (u"ࠫࡈࡏࠧ૊"))).lower() == bstack111lll1l_opy_ (u"ࠬࡺࡲࡶࡧࠪો") and str(os.getenv(bstack111lll1l_opy_ (u"࠭ࡃࡊࡡࡑࡅࡒࡋࠧૌ"))).lower() == bstack111lll1l_opy_ (u"ࠧࡤࡱࡧࡩࡸ࡮ࡩࡱ્ࠩ"):
    return 0 # bstack1l1ll11_opy_ bstack111lll1_opy_ not set build number env
  if os.getenv(bstack111lll1l_opy_ (u"ࠨࡄࡌࡘࡇ࡛ࡃࡌࡇࡗࡣࡇࡘࡁࡏࡅࡋࠫ૎")) and os.getenv(bstack111lll1l_opy_ (u"ࠩࡅࡍ࡙ࡈࡕࡄࡍࡈࡘࡤࡉࡏࡎࡏࡌࡘࠬ૏")):
    return os.getenv(bstack111lll1l_opy_ (u"ࠪࡆࡎ࡚ࡂࡖࡅࡎࡉ࡙ࡥࡂࡖࡋࡏࡈࡤࡔࡕࡎࡄࡈࡖࠬૐ"), 0)
  if str(os.getenv(bstack111lll1l_opy_ (u"ࠫࡈࡏࠧ૑"))).lower() == bstack111lll1l_opy_ (u"ࠬࡺࡲࡶࡧࠪ૒") and str(os.getenv(bstack111lll1l_opy_ (u"࠭ࡄࡓࡑࡑࡉࠬ૓"))).lower() == bstack111lll1l_opy_ (u"ࠧࡵࡴࡸࡩࠬ૔"):
    return os.getenv(bstack111lll1l_opy_ (u"ࠨࡆࡕࡓࡓࡋ࡟ࡃࡗࡌࡐࡉࡥࡎࡖࡏࡅࡉࡗ࠭૕"), 0)
  if str(os.getenv(bstack111lll1l_opy_ (u"ࠩࡆࡍࠬ૖"))).lower() == bstack111lll1l_opy_ (u"ࠪࡸࡷࡻࡥࠨ૗") and str(os.getenv(bstack111lll1l_opy_ (u"ࠫࡘࡋࡍࡂࡒࡋࡓࡗࡋࠧ૘"))).lower() == bstack111lll1l_opy_ (u"ࠬࡺࡲࡶࡧࠪ૙"):
    return os.getenv(bstack111lll1l_opy_ (u"࠭ࡓࡆࡏࡄࡔࡍࡕࡒࡆࡡࡍࡓࡇࡥࡉࡅࠩ૚"), 0)
  if str(os.getenv(bstack111lll1l_opy_ (u"ࠧࡄࡋࠪ૛"))).lower() == bstack111lll1l_opy_ (u"ࠨࡶࡵࡹࡪ࠭૜") and str(os.getenv(bstack111lll1l_opy_ (u"ࠩࡊࡍ࡙ࡒࡁࡃࡡࡆࡍࠬ૝"))).lower() == bstack111lll1l_opy_ (u"ࠪࡸࡷࡻࡥࠨ૞"):
    return os.getenv(bstack111lll1l_opy_ (u"ࠫࡈࡏ࡟ࡋࡑࡅࡣࡎࡊࠧ૟"), 0)
  if str(os.getenv(bstack111lll1l_opy_ (u"ࠬࡉࡉࠨૠ"))).lower() == bstack111lll1l_opy_ (u"࠭ࡴࡳࡷࡨࠫૡ") and str(os.getenv(bstack111lll1l_opy_ (u"ࠧࡃࡗࡌࡐࡉࡑࡉࡕࡇࠪૢ"))).lower() == bstack111lll1l_opy_ (u"ࠨࡶࡵࡹࡪ࠭ૣ"):
    return os.getenv(bstack111lll1l_opy_ (u"ࠩࡅ࡙ࡎࡒࡄࡌࡋࡗࡉࡤࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࡃࡇࡕࠫ૤"), 0)
  if str(os.getenv(bstack111lll1l_opy_ (u"ࠪࡘࡋࡥࡂࡖࡋࡏࡈࠬ૥"))).lower() == bstack111lll1l_opy_ (u"ࠫࡹࡸࡵࡦࠩ૦"):
    return os.getenv(bstack111lll1l_opy_ (u"ࠬࡈࡕࡊࡎࡇࡣࡇ࡛ࡉࡍࡆࡌࡈࠬ૧"), 0)
  return -1
def bstack1llllll11_opy_(bstack1lll11111_opy_):
  global CONFIG
  if not bstack111lll1l_opy_ (u"࠭ࠤࡼࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࡽࠨ૨") in CONFIG[bstack111lll1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩ૩")]:
    return
  CONFIG[bstack111lll1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪ૪")] = CONFIG[bstack111lll1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ૫")].replace(
    bstack111lll1l_opy_ (u"ࠪࠨࢀࡈࡕࡊࡎࡇࡣࡓ࡛ࡍࡃࡇࡕࢁࠬ૬"),
    str(bstack1lll11111_opy_)
  )
def bstack11l1ll_opy_():
  global CONFIG
  if not bstack111lll1l_opy_ (u"ࠫࠩࢁࡄࡂࡖࡈࡣ࡙ࡏࡍࡆࡿࠪ૭") in CONFIG[bstack111lll1l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧ૮")]:
    return
  bstack11l11ll1_opy_ = datetime.datetime.now()
  bstack111ll1l_opy_ = bstack11l11ll1_opy_.strftime(bstack111lll1l_opy_ (u"࠭ࠥࡥ࠯ࠨࡦ࠲ࠫࡈ࠻ࠧࡐࠫ૯"))
  CONFIG[bstack111lll1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩ૰")] = CONFIG[bstack111lll1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪ૱")].replace(
    bstack111lll1l_opy_ (u"ࠩࠧࡿࡉࡇࡔࡆࡡࡗࡍࡒࡋࡽࠨ૲"),
    bstack111ll1l_opy_
  )
def bstack1111l1_opy_():
  global CONFIG
  if bstack111lll1l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ૳") in CONFIG and not bool(CONFIG[bstack111lll1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭૴")]):
    del CONFIG[bstack111lll1l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧ૵")]
    return
  if not bstack111lll1l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ૶") in CONFIG:
    CONFIG[bstack111lll1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩ૷")] = bstack111lll1l_opy_ (u"ࠨࠥࠧࡿࡇ࡛ࡉࡍࡆࡢࡒ࡚ࡓࡂࡆࡔࢀࠫ૸")
  if bstack111lll1l_opy_ (u"ࠩࠧࡿࡉࡇࡔࡆࡡࡗࡍࡒࡋࡽࠨૹ") in CONFIG[bstack111lll1l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬૺ")]:
    bstack11l1ll_opy_()
    os.environ[bstack111lll1l_opy_ (u"ࠫࡇ࡙ࡔࡂࡅࡎࡣࡈࡕࡍࡃࡋࡑࡉࡉࡥࡂࡖࡋࡏࡈࡤࡏࡄࠨૻ")] = CONFIG[bstack111lll1l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧૼ")]
  if not bstack111lll1l_opy_ (u"࠭ࠤࡼࡄࡘࡍࡑࡊ࡟ࡏࡗࡐࡆࡊࡘࡽࠨ૽") in CONFIG[bstack111lll1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩ૾")]:
    return
  bstack1lll11111_opy_ = bstack111lll1l_opy_ (u"ࠨࠩ૿")
  bstack1ll1l1l11_opy_ = bstack1l1l1l11l_opy_()
  if bstack1ll1l1l11_opy_ != -1:
    bstack1lll11111_opy_ = bstack111lll1l_opy_ (u"ࠩࡆࡍࠥ࠭଀") + str(bstack1ll1l1l11_opy_)
  if bstack1lll11111_opy_ == bstack111lll1l_opy_ (u"ࠪࠫଁ"):
    bstack11l1111l_opy_ = bstack1l1ll11l_opy_(CONFIG[bstack111lll1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧଂ")])
    if bstack11l1111l_opy_ != -1:
      bstack1lll11111_opy_ = str(bstack11l1111l_opy_)
  if bstack1lll11111_opy_:
    bstack1llllll11_opy_(bstack1lll11111_opy_)
    os.environ[bstack111lll1l_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡤࡉࡏࡎࡄࡌࡒࡊࡊ࡟ࡃࡗࡌࡐࡉࡥࡉࡅࠩଃ")] = CONFIG[bstack111lll1l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ଄")]
def bstack1111ll1l1_opy_(bstack11lll11l_opy_, bstack1lll11l1_opy_, path):
  bstack1ll1l11ll_opy_ = {
    bstack111lll1l_opy_ (u"ࠧࡪࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫଅ"): bstack1lll11l1_opy_
  }
  if os.path.exists(path):
    bstack1l111lll1_opy_ = json.load(open(path, bstack111lll1l_opy_ (u"ࠨࡴࡥࠫଆ")))
  else:
    bstack1l111lll1_opy_ = {}
  bstack1l111lll1_opy_[bstack11lll11l_opy_] = bstack1ll1l11ll_opy_
  with open(path, bstack111lll1l_opy_ (u"ࠤࡺ࠯ࠧଇ")) as outfile:
    json.dump(bstack1l111lll1_opy_, outfile)
def bstack1l1ll11l_opy_(bstack11lll11l_opy_):
  bstack11lll11l_opy_ = str(bstack11lll11l_opy_)
  bstack1ll111ll_opy_ = os.path.join(os.path.expanduser(bstack111lll1l_opy_ (u"ࠪࢂࠬଈ")), bstack111lll1l_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫଉ"))
  try:
    if not os.path.exists(bstack1ll111ll_opy_):
      os.makedirs(bstack1ll111ll_opy_)
    file_path = os.path.join(os.path.expanduser(bstack111lll1l_opy_ (u"ࠬࢄࠧଊ")), bstack111lll1l_opy_ (u"࠭࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠭ଋ"), bstack111lll1l_opy_ (u"ࠧ࠯ࡤࡸ࡭ࡱࡪ࠭࡯ࡣࡰࡩ࠲ࡩࡡࡤࡪࡨ࠲࡯ࡹ࡯࡯ࠩଌ"))
    if not os.path.isfile(file_path):
      with open(file_path, bstack111lll1l_opy_ (u"ࠨࡹࠪ଍")):
        pass
      with open(file_path, bstack111lll1l_opy_ (u"ࠤࡺ࠯ࠧ଎")) as outfile:
        json.dump({}, outfile)
    with open(file_path, bstack111lll1l_opy_ (u"ࠪࡶࠬଏ")) as bstack1ll111l1_opy_:
      bstack1llll1lll_opy_ = json.load(bstack1ll111l1_opy_)
    if bstack11lll11l_opy_ in bstack1llll1lll_opy_:
      bstack1lll1lll_opy_ = bstack1llll1lll_opy_[bstack11lll11l_opy_][bstack111lll1l_opy_ (u"ࠫ࡮ࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨଐ")]
      bstack11lllll1_opy_ = int(bstack1lll1lll_opy_) + 1
      bstack1111ll1l1_opy_(bstack11lll11l_opy_, bstack11lllll1_opy_, file_path)
      return bstack11lllll1_opy_
    else:
      bstack1111ll1l1_opy_(bstack11lll11l_opy_, 1, file_path)
      return 1
  except Exception as e:
    logger.warn(bstack1l1ll_opy_.format(str(e)))
    return -1
def bstack1111llll_opy_(config):
  if not config[bstack111lll1l_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧ଑")] or not config[bstack111lll1l_opy_ (u"࠭ࡡࡤࡥࡨࡷࡸࡑࡥࡺࠩ଒")]:
    return True
  else:
    return False
def bstack1llllll_opy_(config):
  if bstack111lll1l_opy_ (u"ࠧࡪࡵࡓࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹ࠭ଓ") in config:
    del(config[bstack111lll1l_opy_ (u"ࠨ࡫ࡶࡔࡱࡧࡹࡸࡴ࡬࡫࡭ࡺࠧଔ")])
    return False
  if bstack1l111lll_opy_() < version.parse(bstack111lll1l_opy_ (u"ࠩ࠶࠲࠹࠴࠰ࠨକ")):
    return False
  if bstack1l111lll_opy_() >= version.parse(bstack111lll1l_opy_ (u"ࠪ࠸࠳࠷࠮࠶ࠩଖ")):
    return True
  if bstack111lll1l_opy_ (u"ࠫࡺࡹࡥࡘ࠵ࡆࠫଗ") in config and config[bstack111lll1l_opy_ (u"ࠬࡻࡳࡦ࡙࠶ࡇࠬଘ")] == False:
    return False
  else:
    return True
def bstack1l11ll_opy_(config, index = 0):
  global bstack111llll11_opy_
  bstack11ll111l1_opy_ = {}
  caps = bstack11lll1l11_opy_ + bstack1ll111111_opy_
  if bstack111llll11_opy_:
    caps += bstack1ll1llll_opy_
  for key in config:
    if key in caps + [bstack111lll1l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩଙ")]:
      continue
    bstack11ll111l1_opy_[key] = config[key]
  if bstack111lll1l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪଚ") in config:
    for bstack111l11_opy_ in config[bstack111lll1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫଛ")][index]:
      if bstack111l11_opy_ in caps + [bstack111lll1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧଜ"), bstack111lll1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵ࡚ࡪࡸࡳࡪࡱࡱࠫଝ")]:
        continue
      bstack11ll111l1_opy_[bstack111l11_opy_] = config[bstack111lll1l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧଞ")][index][bstack111l11_opy_]
  bstack11ll111l1_opy_[bstack111lll1l_opy_ (u"ࠬ࡮࡯ࡴࡶࡑࡥࡲ࡫ࠧଟ")] = socket.gethostname()
  if bstack111lll1l_opy_ (u"࠭ࡶࡦࡴࡶ࡭ࡴࡴࠧଠ") in bstack11ll111l1_opy_:
    del(bstack11ll111l1_opy_[bstack111lll1l_opy_ (u"ࠧࡷࡧࡵࡷ࡮ࡵ࡮ࠨଡ")])
  return bstack11ll111l1_opy_
def bstack1lllll1ll_opy_(config):
  global bstack111llll11_opy_
  bstack1llllllll_opy_ = {}
  caps = bstack1ll111111_opy_
  if bstack111llll11_opy_:
    caps+= bstack1ll1llll_opy_
  for key in caps:
    if key in config:
      bstack1llllllll_opy_[key] = config[key]
  return bstack1llllllll_opy_
def bstack1ll1l1l1_opy_(bstack11ll111l1_opy_, bstack1llllllll_opy_):
  bstack1l111ll_opy_ = {}
  for key in bstack11ll111l1_opy_.keys():
    if key in bstack1llll1l11_opy_:
      bstack1l111ll_opy_[bstack1llll1l11_opy_[key]] = bstack11ll111l1_opy_[key]
    else:
      bstack1l111ll_opy_[key] = bstack11ll111l1_opy_[key]
  for key in bstack1llllllll_opy_:
    if key in bstack1llll1l11_opy_:
      bstack1l111ll_opy_[bstack1llll1l11_opy_[key]] = bstack1llllllll_opy_[key]
    else:
      bstack1l111ll_opy_[key] = bstack1llllllll_opy_[key]
  return bstack1l111ll_opy_
def bstack11l1111ll_opy_(config, index = 0):
  global bstack111llll11_opy_
  config = copy.deepcopy(config)
  caps = {}
  bstack1llllllll_opy_ = bstack1lllll1ll_opy_(config)
  bstack1ll1lll11_opy_ = bstack1ll111111_opy_
  bstack1ll1lll11_opy_ += bstack1l111l1_opy_
  if bstack111llll11_opy_:
    bstack1ll1lll11_opy_ += bstack1ll1llll_opy_
  if bstack111lll1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫଢ") in config:
    if bstack111lll1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧଣ") in config[bstack111lll1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ତ")][index]:
      caps[bstack111lll1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩଥ")] = config[bstack111lll1l_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨଦ")][index][bstack111lll1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫଧ")]
    if bstack111lll1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨନ") in config[bstack111lll1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ଩")][index]:
      caps[bstack111lll1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪପ")] = str(config[bstack111lll1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ଫ")][index][bstack111lll1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶ࡛࡫ࡲࡴ࡫ࡲࡲࠬବ")])
    bstack11ll1lll1_opy_ = {}
    for bstack111l1ll1l_opy_ in bstack1ll1lll11_opy_:
      if bstack111l1ll1l_opy_ in config[bstack111lll1l_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨଭ")][index]:
        if bstack111l1ll1l_opy_ == bstack111lll1l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡗࡧࡵࡷ࡮ࡵ࡮ࠨମ"):
          try:
            bstack11ll1lll1_opy_[bstack111l1ll1l_opy_] = str(config[bstack111lll1l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡵࠪଯ")][index][bstack111l1ll1l_opy_] * 1.0)
          except:
            bstack11ll1lll1_opy_[bstack111l1ll1l_opy_] = str(config[bstack111lll1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫର")][index][bstack111l1ll1l_opy_])
        else:
          bstack11ll1lll1_opy_[bstack111l1ll1l_opy_] = config[bstack111lll1l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ଱")][index][bstack111l1ll1l_opy_]
        del(config[bstack111lll1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ଲ")][index][bstack111l1ll1l_opy_])
    bstack1llllllll_opy_ = update(bstack1llllllll_opy_, bstack11ll1lll1_opy_)
  bstack11ll111l1_opy_ = bstack1l11ll_opy_(config, index)
  for bstack111l1l11l_opy_ in bstack1ll111111_opy_ + [bstack111lll1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩଳ"), bstack111lll1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡜ࡥࡳࡵ࡬ࡳࡳ࠭଴")]:
    if bstack111l1l11l_opy_ in bstack11ll111l1_opy_:
      bstack1llllllll_opy_[bstack111l1l11l_opy_] = bstack11ll111l1_opy_[bstack111l1l11l_opy_]
      del(bstack11ll111l1_opy_[bstack111l1l11l_opy_])
  if bstack1llllll_opy_(config):
    bstack11ll111l1_opy_[bstack111lll1l_opy_ (u"࠭ࡵࡴࡧ࡚࠷ࡈ࠭ଵ")] = True
    caps.update(bstack1llllllll_opy_)
    caps[bstack111lll1l_opy_ (u"ࠧࡣࡵࡷࡥࡨࡱ࠺ࡰࡲࡷ࡭ࡴࡴࡳࠨଶ")] = bstack11ll111l1_opy_
  else:
    bstack11ll111l1_opy_[bstack111lll1l_opy_ (u"ࠨࡷࡶࡩ࡜࠹ࡃࠨଷ")] = False
    caps.update(bstack1ll1l1l1_opy_(bstack11ll111l1_opy_, bstack1llllllll_opy_))
    if bstack111lll1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡑࡥࡲ࡫ࠧସ") in caps:
      caps[bstack111lll1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࠫହ")] = caps[bstack111lll1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩ଺")]
      del(caps[bstack111lll1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪ଻")])
    if bstack111lll1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴ଼ࠧ") in caps:
      caps[bstack111lll1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡠࡸࡨࡶࡸ࡯࡯࡯ࠩଽ")] = caps[bstack111lll1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡘࡨࡶࡸ࡯࡯࡯ࠩା")]
      del(caps[bstack111lll1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴ࡙ࡩࡷࡹࡩࡰࡰࠪି")])
  return caps
def bstack11l1l1l_opy_():
  global bstack1l111ll1_opy_
  if bstack1l111lll_opy_() <= version.parse(bstack111lll1l_opy_ (u"ࠪ࠷࠳࠷࠳࠯࠲ࠪୀ")):
    if bstack1l111ll1_opy_ != bstack111lll1l_opy_ (u"ࠫࠬୁ"):
      return bstack111lll1l_opy_ (u"ࠧ࡮ࡴࡵࡲ࠽࠳࠴ࠨୂ") + bstack1l111ll1_opy_ + bstack111lll1l_opy_ (u"ࠨ࠺࠹࠲࠲ࡻࡩ࠵ࡨࡶࡤࠥୃ")
    return bstack1l111l1l1_opy_
  if  bstack1l111ll1_opy_ != bstack111lll1l_opy_ (u"ࠧࠨୄ"):
    return bstack111lll1l_opy_ (u"ࠣࡪࡷࡸࡵࡹ࠺࠰࠱ࠥ୅") + bstack1l111ll1_opy_ + bstack111lll1l_opy_ (u"ࠤ࠲ࡻࡩ࠵ࡨࡶࡤࠥ୆")
  return bstack1l11l11l_opy_
def bstack1ll11l1_opy_(options):
  return hasattr(options, bstack111lll1l_opy_ (u"ࠪࡷࡪࡺ࡟ࡤࡣࡳࡥࡧ࡯࡬ࡪࡶࡼࠫେ"))
def update(d, u):
  for k, v in u.items():
    if isinstance(v, collections.abc.Mapping):
      d[k] = update(d.get(k, {}), v)
    else:
      if isinstance(v, list):
        d[k] = d.get(k, []) + v
      else:
        d[k] = v
  return d
def bstack1ll11111_opy_(options, bstack11llll1ll_opy_):
  for bstack111ll11ll_opy_ in bstack11llll1ll_opy_:
    if bstack111ll11ll_opy_ in [bstack111lll1l_opy_ (u"ࠫࡦࡸࡧࡴࠩୈ"), bstack111lll1l_opy_ (u"ࠬ࡫ࡸࡵࡧࡱࡷ࡮ࡵ࡮ࡴࠩ୉")]:
      next
    if bstack111ll11ll_opy_ in options._experimental_options:
      options._experimental_options[bstack111ll11ll_opy_]= update(options._experimental_options[bstack111ll11ll_opy_], bstack11llll1ll_opy_[bstack111ll11ll_opy_])
    else:
      options.add_experimental_option(bstack111ll11ll_opy_, bstack11llll1ll_opy_[bstack111ll11ll_opy_])
  if bstack111lll1l_opy_ (u"࠭ࡡࡳࡩࡶࠫ୊") in bstack11llll1ll_opy_:
    for arg in bstack11llll1ll_opy_[bstack111lll1l_opy_ (u"ࠧࡢࡴࡪࡷࠬୋ")]:
      options.add_argument(arg)
    del(bstack11llll1ll_opy_[bstack111lll1l_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭ୌ")])
  if bstack111lll1l_opy_ (u"ࠩࡨࡼࡹ࡫࡮ࡴ࡫ࡲࡲࡸ୍࠭") in bstack11llll1ll_opy_:
    for ext in bstack11llll1ll_opy_[bstack111lll1l_opy_ (u"ࠪࡩࡽࡺࡥ࡯ࡵ࡬ࡳࡳࡹࠧ୎")]:
      options.add_extension(ext)
    del(bstack11llll1ll_opy_[bstack111lll1l_opy_ (u"ࠫࡪࡾࡴࡦࡰࡶ࡭ࡴࡴࡳࠨ୏")])
def bstack11ll1111_opy_(options, bstack111l1llll_opy_):
  if bstack111lll1l_opy_ (u"ࠬࡶࡲࡦࡨࡶࠫ୐") in bstack111l1llll_opy_:
    for bstack11l11l1l1_opy_ in bstack111l1llll_opy_[bstack111lll1l_opy_ (u"࠭ࡰࡳࡧࡩࡷࠬ୑")]:
      if bstack11l11l1l1_opy_ in options._preferences:
        options._preferences[bstack11l11l1l1_opy_] = update(options._preferences[bstack11l11l1l1_opy_], bstack111l1llll_opy_[bstack111lll1l_opy_ (u"ࠧࡱࡴࡨࡪࡸ࠭୒")][bstack11l11l1l1_opy_])
      else:
        options.set_preference(bstack11l11l1l1_opy_, bstack111l1llll_opy_[bstack111lll1l_opy_ (u"ࠨࡲࡵࡩ࡫ࡹࠧ୓")][bstack11l11l1l1_opy_])
  if bstack111lll1l_opy_ (u"ࠩࡤࡶ࡬ࡹࠧ୔") in bstack111l1llll_opy_:
    for arg in bstack111l1llll_opy_[bstack111lll1l_opy_ (u"ࠪࡥࡷ࡭ࡳࠨ୕")]:
      options.add_argument(arg)
def bstack1ll111ll1_opy_(options, bstack1l11lll1l_opy_):
  if bstack111lll1l_opy_ (u"ࠫࡼ࡫ࡢࡷ࡫ࡨࡻࠬୖ") in bstack1l11lll1l_opy_:
    options.use_webview(bool(bstack1l11lll1l_opy_[bstack111lll1l_opy_ (u"ࠬࡽࡥࡣࡸ࡬ࡩࡼ࠭ୗ")]))
  bstack1ll11111_opy_(options, bstack1l11lll1l_opy_)
def bstack1l11l1ll_opy_(options, bstack111l11l11_opy_):
  for bstack11l1llll_opy_ in bstack111l11l11_opy_:
    if bstack11l1llll_opy_ in [bstack111lll1l_opy_ (u"࠭ࡴࡦࡥ࡫ࡲࡴࡲ࡯ࡨࡻࡓࡶࡪࡼࡩࡦࡹࠪ୘"), bstack111lll1l_opy_ (u"ࠧࡢࡴࡪࡷࠬ୙")]:
      next
    options.set_capability(bstack11l1llll_opy_, bstack111l11l11_opy_[bstack11l1llll_opy_])
  if bstack111lll1l_opy_ (u"ࠨࡣࡵ࡫ࡸ࠭୚") in bstack111l11l11_opy_:
    for arg in bstack111l11l11_opy_[bstack111lll1l_opy_ (u"ࠩࡤࡶ࡬ࡹࠧ୛")]:
      options.add_argument(arg)
  if bstack111lll1l_opy_ (u"ࠪࡸࡪࡩࡨ࡯ࡱ࡯ࡳ࡬ࡿࡐࡳࡧࡹ࡭ࡪࡽࠧଡ଼") in bstack111l11l11_opy_:
    options.bstack1l111111l_opy_(bool(bstack111l11l11_opy_[bstack111lll1l_opy_ (u"ࠫࡹ࡫ࡣࡩࡰࡲࡰࡴ࡭ࡹࡑࡴࡨࡺ࡮࡫ࡷࠨଢ଼")]))
def bstack1lll11l1l_opy_(options, bstack11lll111l_opy_):
  for bstack1ll11ll1_opy_ in bstack11lll111l_opy_:
    if bstack1ll11ll1_opy_ in [bstack111lll1l_opy_ (u"ࠬࡧࡤࡥ࡫ࡷ࡭ࡴࡴࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩ୞"), bstack111lll1l_opy_ (u"࠭ࡡࡳࡩࡶࠫୟ")]:
      next
    options._options[bstack1ll11ll1_opy_] = bstack11lll111l_opy_[bstack1ll11ll1_opy_]
  if bstack111lll1l_opy_ (u"ࠧࡢࡦࡧ࡭ࡹ࡯࡯࡯ࡣ࡯ࡓࡵࡺࡩࡰࡰࡶࠫୠ") in bstack11lll111l_opy_:
    for bstack111ll111_opy_ in bstack11lll111l_opy_[bstack111lll1l_opy_ (u"ࠨࡣࡧࡨ࡮ࡺࡩࡰࡰࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬୡ")]:
      options.bstack11l1l111l_opy_(
          bstack111ll111_opy_, bstack11lll111l_opy_[bstack111lll1l_opy_ (u"ࠩࡤࡨࡩ࡯ࡴࡪࡱࡱࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ୢ")][bstack111ll111_opy_])
  if bstack111lll1l_opy_ (u"ࠪࡥࡷ࡭ࡳࠨୣ") in bstack11lll111l_opy_:
    for arg in bstack11lll111l_opy_[bstack111lll1l_opy_ (u"ࠫࡦࡸࡧࡴࠩ୤")]:
      options.add_argument(arg)
def bstack1l1111ll1_opy_(options, caps):
  if not hasattr(options, bstack111lll1l_opy_ (u"ࠬࡑࡅ࡚ࠩ୥")):
    return
  if options.KEY == bstack111lll1l_opy_ (u"࠭ࡧࡰࡱࡪ࠾ࡨ࡮ࡲࡰ࡯ࡨࡓࡵࡺࡩࡰࡰࡶࠫ୦") and options.KEY in caps:
    bstack1ll11111_opy_(options, caps[bstack111lll1l_opy_ (u"ࠧࡨࡱࡲ࡫࠿ࡩࡨࡳࡱࡰࡩࡔࡶࡴࡪࡱࡱࡷࠬ୧")])
  elif options.KEY == bstack111lll1l_opy_ (u"ࠨ࡯ࡲࡾ࠿࡬ࡩࡳࡧࡩࡳࡽࡕࡰࡵ࡫ࡲࡲࡸ࠭୨") and options.KEY in caps:
    bstack11ll1111_opy_(options, caps[bstack111lll1l_opy_ (u"ࠩࡰࡳࡿࡀࡦࡪࡴࡨࡪࡴࡾࡏࡱࡶ࡬ࡳࡳࡹࠧ୩")])
  elif options.KEY == bstack111lll1l_opy_ (u"ࠪࡷࡦ࡬ࡡࡳ࡫࠱ࡳࡵࡺࡩࡰࡰࡶࠫ୪") and options.KEY in caps:
    bstack1l11l1ll_opy_(options, caps[bstack111lll1l_opy_ (u"ࠫࡸࡧࡦࡢࡴ࡬࠲ࡴࡶࡴࡪࡱࡱࡷࠬ୫")])
  elif options.KEY == bstack111lll1l_opy_ (u"ࠬࡳࡳ࠻ࡧࡧ࡫ࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭୬") and options.KEY in caps:
    bstack1ll111ll1_opy_(options, caps[bstack111lll1l_opy_ (u"࠭࡭ࡴ࠼ࡨࡨ࡬࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ୭")])
  elif options.KEY == bstack111lll1l_opy_ (u"ࠧࡴࡧ࠽࡭ࡪࡕࡰࡵ࡫ࡲࡲࡸ࠭୮") and options.KEY in caps:
    bstack1lll11l1l_opy_(options, caps[bstack111lll1l_opy_ (u"ࠨࡵࡨ࠾࡮࡫ࡏࡱࡶ࡬ࡳࡳࡹࠧ୯")])
def bstack111l111l_opy_(caps):
  global bstack111llll11_opy_
  if bstack111llll11_opy_:
    if bstack1l1l11111_opy_() < version.parse(bstack111lll1l_opy_ (u"ࠩ࠵࠲࠸࠴࠰ࠨ୰")):
      return None
    else:
      from appium.options.common.base import AppiumOptions
      options = AppiumOptions().load_capabilities(caps)
      return options
  else:
    browser = bstack111lll1l_opy_ (u"ࠪࡧ࡭ࡸ࡯࡮ࡧࠪୱ")
    if bstack111lll1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩ୲") in caps:
      browser = caps[bstack111lll1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡔࡡ࡮ࡧࠪ୳")]
    elif bstack111lll1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࠧ୴") in caps:
      browser = caps[bstack111lll1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࠨ୵")]
    browser = str(browser).lower()
    if browser == bstack111lll1l_opy_ (u"ࠨ࡫ࡳ࡬ࡴࡴࡥࠨ୶") or browser == bstack111lll1l_opy_ (u"ࠩ࡬ࡴࡦࡪࠧ୷"):
      browser = bstack111lll1l_opy_ (u"ࠪࡷࡦ࡬ࡡࡳ࡫ࠪ୸")
    if browser == bstack111lll1l_opy_ (u"ࠫࡸࡧ࡭ࡴࡷࡱ࡫ࠬ୹"):
      browser = bstack111lll1l_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࠬ୺")
    if browser not in [bstack111lll1l_opy_ (u"࠭ࡣࡩࡴࡲࡱࡪ࠭୻"), bstack111lll1l_opy_ (u"ࠧࡦࡦࡪࡩࠬ୼"), bstack111lll1l_opy_ (u"ࠨ࡫ࡨࠫ୽"), bstack111lll1l_opy_ (u"ࠩࡶࡥ࡫ࡧࡲࡪࠩ୾"), bstack111lll1l_opy_ (u"ࠪࡪ࡮ࡸࡥࡧࡱࡻࠫ୿")]:
      return None
    try:
      package = bstack111lll1l_opy_ (u"ࠫࡸ࡫࡬ࡦࡰ࡬ࡹࡲ࠴ࡷࡦࡤࡧࡶ࡮ࡼࡥࡳ࠰ࡾࢁ࠳ࡵࡰࡵ࡫ࡲࡲࡸ࠭஀").format(browser)
      name = bstack111lll1l_opy_ (u"ࠬࡕࡰࡵ࡫ࡲࡲࡸ࠭஁")
      browser_options = getattr(__import__(package, fromlist=[name]), name)
      options = browser_options()
      if not bstack1ll11l1_opy_(options):
        return None
      for bstack111l1l11l_opy_ in caps.keys():
        options.set_capability(bstack111l1l11l_opy_, caps[bstack111l1l11l_opy_])
      bstack1l1111ll1_opy_(options, caps)
      return options
    except Exception as e:
      logger.debug(str(e))
      return None
def bstack1l11ll111_opy_(options, bstack11l111l1l_opy_):
  if not bstack1ll11l1_opy_(options):
    return
  for bstack111l1l11l_opy_ in bstack11l111l1l_opy_.keys():
    if bstack111l1l11l_opy_ in bstack1l111l1_opy_:
      next
    if bstack111l1l11l_opy_ in options._caps and type(options._caps[bstack111l1l11l_opy_]) in [dict, list]:
      options._caps[bstack111l1l11l_opy_] = update(options._caps[bstack111l1l11l_opy_], bstack11l111l1l_opy_[bstack111l1l11l_opy_])
    else:
      options.set_capability(bstack111l1l11l_opy_, bstack11l111l1l_opy_[bstack111l1l11l_opy_])
  bstack1l1111ll1_opy_(options, bstack11l111l1l_opy_)
  if bstack111lll1l_opy_ (u"࠭࡭ࡰࡼ࠽ࡨࡪࡨࡵࡨࡩࡨࡶࡆࡪࡤࡳࡧࡶࡷࠬஂ") in options._caps:
    if options._caps[bstack111lll1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡏࡣࡰࡩࠬஃ")] and options._caps[bstack111lll1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡐࡤࡱࡪ࠭஄")].lower() != bstack111lll1l_opy_ (u"ࠩࡩ࡭ࡷ࡫ࡦࡰࡺࠪஅ"):
      del options._caps[bstack111lll1l_opy_ (u"ࠪࡱࡴࢀ࠺ࡥࡧࡥࡹ࡬࡭ࡥࡳࡃࡧࡨࡷ࡫ࡳࡴࠩஆ")]
def bstack1l11l1l11_opy_(proxy_config):
  if bstack111lll1l_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠨஇ") in proxy_config:
    proxy_config[bstack111lll1l_opy_ (u"ࠬࡹࡳ࡭ࡒࡵࡳࡽࡿࠧஈ")] = proxy_config[bstack111lll1l_opy_ (u"࠭ࡨࡵࡶࡳࡷࡕࡸ࡯ࡹࡻࠪஉ")]
    del(proxy_config[bstack111lll1l_opy_ (u"ࠧࡩࡶࡷࡴࡸࡖࡲࡰࡺࡼࠫஊ")])
  if bstack111lll1l_opy_ (u"ࠨࡲࡵࡳࡽࡿࡔࡺࡲࡨࠫ஋") in proxy_config and proxy_config[bstack111lll1l_opy_ (u"ࠩࡳࡶࡴࡾࡹࡕࡻࡳࡩࠬ஌")].lower() != bstack111lll1l_opy_ (u"ࠪࡨ࡮ࡸࡥࡤࡶࠪ஍"):
    proxy_config[bstack111lll1l_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࡗࡽࡵ࡫ࠧஎ")] = bstack111lll1l_opy_ (u"ࠬࡳࡡ࡯ࡷࡤࡰࠬஏ")
  if bstack111lll1l_opy_ (u"࠭ࡰࡳࡱࡻࡽࡆࡻࡴࡰࡥࡲࡲ࡫࡯ࡧࡖࡴ࡯ࠫஐ") in proxy_config:
    proxy_config[bstack111lll1l_opy_ (u"ࠧࡱࡴࡲࡼࡾ࡚ࡹࡱࡧࠪ஑")] = bstack111lll1l_opy_ (u"ࠨࡲࡤࡧࠬஒ")
  return proxy_config
def bstack1lllll1_opy_(config, proxy):
  from selenium.webdriver.common.proxy import Proxy
  if not bstack111lll1l_opy_ (u"ࠩࡳࡶࡴࡾࡹࠨஓ") in config:
    return proxy
  config[bstack111lll1l_opy_ (u"ࠪࡴࡷࡵࡸࡺࠩஔ")] = bstack1l11l1l11_opy_(config[bstack111lll1l_opy_ (u"ࠫࡵࡸ࡯ࡹࡻࠪக")])
  if proxy == None:
    proxy = Proxy(config[bstack111lll1l_opy_ (u"ࠬࡶࡲࡰࡺࡼࠫ஖")])
  return proxy
def bstack11l1ll1_opy_(self):
  global CONFIG
  global bstack1ll1l1ll_opy_
  try:
    proxy = bstack1ll11ll_opy_(CONFIG)
    if proxy:
      if proxy.endswith(bstack111lll1l_opy_ (u"࠭࠮ࡱࡣࡦࠫ஗")):
        proxies = bstack1lll1_opy_(proxy, bstack11l1l1l_opy_())
        if len(proxies) > 0:
          protocol, bstack1l11l111l_opy_ = proxies.popitem()
          if bstack111lll1l_opy_ (u"ࠢ࠻࠱࠲ࠦ஘") in bstack1l11l111l_opy_:
            return bstack1l11l111l_opy_
          else:
            return bstack111lll1l_opy_ (u"ࠣࡪࡷࡸࡵࡀ࠯࠰ࠤங") + bstack1l11l111l_opy_
      else:
        return proxy
  except Exception as e:
    logger.error(bstack111lll1l_opy_ (u"ࠤࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡸ࡫ࡴࡵ࡫ࡱ࡫ࠥࡶࡲࡰࡺࡼࠤࡺࡸ࡬ࠡ࠼ࠣࡿࢂࠨச").format(str(e)))
  return bstack1ll1l1ll_opy_(self)
def bstack11lll1ll_opy_():
  global CONFIG
  return bstack111lll1l_opy_ (u"ࠪ࡬ࡹࡺࡰࡑࡴࡲࡼࡾ࠭஛") in CONFIG or bstack111lll1l_opy_ (u"ࠫ࡭ࡺࡴࡱࡵࡓࡶࡴࡾࡹࠨஜ") in CONFIG
def bstack1ll11ll_opy_(config):
  if not bstack11lll1ll_opy_():
    return
  if config.get(bstack111lll1l_opy_ (u"ࠬ࡮ࡴࡵࡲࡓࡶࡴࡾࡹࠨ஝")):
    return config.get(bstack111lll1l_opy_ (u"࠭ࡨࡵࡶࡳࡔࡷࡵࡸࡺࠩஞ"))
  if config.get(bstack111lll1l_opy_ (u"ࠧࡩࡶࡷࡴࡸࡖࡲࡰࡺࡼࠫட")):
    return config.get(bstack111lll1l_opy_ (u"ࠨࡪࡷࡸࡵࡹࡐࡳࡱࡻࡽࠬ஠"))
def bstack1llllll1l_opy_(url):
  try:
      result = urlparse(url)
      return all([result.scheme, result.netloc])
  except:
      return False
def bstack1l11l11_opy_(bstack1l1ll1l1_opy_, bstack11lll11ll_opy_):
  from pypac import get_pac
  from pypac import PACSession
  from pypac.parser import PACFile
  import socket
  if os.path.isfile(bstack1l1ll1l1_opy_):
    with open(bstack1l1ll1l1_opy_) as f:
      pac = PACFile(f.read())
  elif bstack1llllll1l_opy_(bstack1l1ll1l1_opy_):
    pac = get_pac(url=bstack1l1ll1l1_opy_)
  else:
    raise Exception(bstack111lll1l_opy_ (u"ࠩࡓࡥࡨࠦࡦࡪ࡮ࡨࠤࡩࡵࡥࡴࠢࡱࡳࡹࠦࡥࡹ࡫ࡶࡸ࠿ࠦࡻࡾࠩ஡").format(bstack1l1ll1l1_opy_))
  session = PACSession(pac)
  try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((bstack111lll1l_opy_ (u"ࠥ࠼࠳࠾࠮࠹࠰࠻ࠦ஢"), 80))
    bstack1ll11l11l_opy_ = s.getsockname()[0]
    s.close()
  except:
    bstack1ll11l11l_opy_ = bstack111lll1l_opy_ (u"ࠫ࠵࠴࠰࠯࠲࠱࠴ࠬண")
  proxy_url = session.get_pac().find_proxy_for_url(bstack11lll11ll_opy_, bstack1ll11l11l_opy_)
  return proxy_url
def bstack1lll1_opy_(bstack1l1ll1l1_opy_, bstack11lll11ll_opy_):
  proxies = {}
  global bstack1ll111_opy_
  if bstack111lll1l_opy_ (u"ࠬࡖࡁࡄࡡࡓࡖࡔ࡞࡙ࠨத") in globals():
    return bstack1ll111_opy_
  try:
    proxy = bstack1l11l11_opy_(bstack1l1ll1l1_opy_,bstack11lll11ll_opy_)
    if bstack111lll1l_opy_ (u"ࠨࡄࡊࡔࡈࡇ࡙ࠨ஥") in proxy:
      proxies = {}
    elif bstack111lll1l_opy_ (u"ࠢࡉࡖࡗࡔࠧ஦") in proxy or bstack111lll1l_opy_ (u"ࠣࡊࡗࡘࡕ࡙ࠢ஧") in proxy or bstack111lll1l_opy_ (u"ࠤࡖࡓࡈࡑࡓࠣந") in proxy:
      bstack11ll1ll1_opy_ = proxy.split(bstack111lll1l_opy_ (u"ࠥࠤࠧன"))
      if bstack111lll1l_opy_ (u"ࠦ࠿࠵࠯ࠣப") in bstack111lll1l_opy_ (u"ࠧࠨ஫").join(bstack11ll1ll1_opy_[1:]):
        proxies = {
          bstack111lll1l_opy_ (u"࠭ࡨࡵࡶࡳࡷࠬ஬"): bstack111lll1l_opy_ (u"ࠢࠣ஭").join(bstack11ll1ll1_opy_[1:])
        }
      else:
        proxies = {
          bstack111lll1l_opy_ (u"ࠨࡪࡷࡸࡵࡹࠧம") : str(bstack11ll1ll1_opy_[0]).lower()+ bstack111lll1l_opy_ (u"ࠤ࠽࠳࠴ࠨய") + bstack111lll1l_opy_ (u"ࠥࠦர").join(bstack11ll1ll1_opy_[1:])
        }
    elif bstack111lll1l_opy_ (u"ࠦࡕࡘࡏ࡙࡛ࠥற") in proxy:
      bstack11ll1ll1_opy_ = proxy.split(bstack111lll1l_opy_ (u"ࠧࠦࠢல"))
      if bstack111lll1l_opy_ (u"ࠨ࠺࠰࠱ࠥள") in bstack111lll1l_opy_ (u"ࠢࠣழ").join(bstack11ll1ll1_opy_[1:]):
        proxies = {
          bstack111lll1l_opy_ (u"ࠨࡪࡷࡸࡵࡹࠧவ"): bstack111lll1l_opy_ (u"ࠤࠥஶ").join(bstack11ll1ll1_opy_[1:])
        }
      else:
        proxies = {
          bstack111lll1l_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࠩஷ"): bstack111lll1l_opy_ (u"ࠦ࡭ࡺࡴࡱ࠼࠲࠳ࠧஸ") + bstack111lll1l_opy_ (u"ࠧࠨஹ").join(bstack11ll1ll1_opy_[1:])
        }
    else:
      proxies = {
        bstack111lll1l_opy_ (u"࠭ࡨࡵࡶࡳࡷࠬ஺"): proxy
      }
  except Exception as e:
    logger.error(bstack11ll1l1l_opy_.format(bstack1l1ll1l1_opy_, str(e)))
  bstack1ll111_opy_ = proxies
  return proxies
def bstack1l11111l_opy_(config, bstack11lll11ll_opy_):
  proxy = bstack1ll11ll_opy_(config)
  proxies = {}
  if config.get(bstack111lll1l_opy_ (u"ࠧࡩࡶࡷࡴࡕࡸ࡯ࡹࡻࠪ஻")) or config.get(bstack111lll1l_opy_ (u"ࠨࡪࡷࡸࡵࡹࡐࡳࡱࡻࡽࠬ஼")):
    if proxy.endswith(bstack111lll1l_opy_ (u"ࠩ࠱ࡴࡦࡩࠧ஽")):
      proxies = bstack1lll1_opy_(proxy,bstack11lll11ll_opy_)
    else:
      proxies = {
        bstack111lll1l_opy_ (u"ࠪ࡬ࡹࡺࡰࡴࠩா"): proxy
      }
  return proxies
def bstack1ll1ll111_opy_():
  return bstack11lll1ll_opy_() and bstack1l111lll_opy_() >= version.parse(bstack1l1lll1ll_opy_)
def bstack111ll1l11_opy_(config):
  bstack111l111ll_opy_ = {}
  if bstack111lll1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࡐࡲࡷ࡭ࡴࡴࡳࠨி") in config:
    bstack111l111ll_opy_ =  config[bstack111lll1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࡙ࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࡑࡳࡸ࡮ࡵ࡮ࡴࠩீ")]
  if bstack111lll1l_opy_ (u"࠭࡬ࡰࡥࡤࡰࡔࡶࡴࡪࡱࡱࡷࠬு") in config:
    bstack111l111ll_opy_ = config[bstack111lll1l_opy_ (u"ࠧ࡭ࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭ூ")]
  proxy = bstack1ll11ll_opy_(config)
  if proxy:
    if proxy.endswith(bstack111lll1l_opy_ (u"ࠨ࠰ࡳࡥࡨ࠭௃")) and os.path.isfile(proxy):
      bstack111l111ll_opy_[bstack111lll1l_opy_ (u"ࠩ࠰ࡴࡦࡩ࠭ࡧ࡫࡯ࡩࠬ௄")] = proxy
    else:
      parsed_url = None
      if proxy.endswith(bstack111lll1l_opy_ (u"ࠪ࠲ࡵࡧࡣࠨ௅")):
        proxies = bstack1l11111l_opy_(config, bstack11l1l1l_opy_())
        if len(proxies) > 0:
          protocol, bstack1l11l111l_opy_ = proxies.popitem()
          if bstack111lll1l_opy_ (u"ࠦ࠿࠵࠯ࠣெ") in bstack1l11l111l_opy_:
            parsed_url = urlparse(bstack1l11l111l_opy_)
          else:
            parsed_url = urlparse(protocol + bstack111lll1l_opy_ (u"ࠧࡀ࠯࠰ࠤே") + bstack1l11l111l_opy_)
      else:
        parsed_url = urlparse(proxy)
      if parsed_url and parsed_url.hostname: bstack111l111ll_opy_[bstack111lll1l_opy_ (u"࠭ࡰࡳࡱࡻࡽࡍࡵࡳࡵࠩை")] = str(parsed_url.hostname)
      if parsed_url and parsed_url.port: bstack111l111ll_opy_[bstack111lll1l_opy_ (u"ࠧࡱࡴࡲࡼࡾࡖ࡯ࡳࡶࠪ௉")] = str(parsed_url.port)
      if parsed_url and parsed_url.username: bstack111l111ll_opy_[bstack111lll1l_opy_ (u"ࠨࡲࡵࡳࡽࡿࡕࡴࡧࡵࠫொ")] = str(parsed_url.username)
      if parsed_url and parsed_url.password: bstack111l111ll_opy_[bstack111lll1l_opy_ (u"ࠩࡳࡶࡴࡾࡹࡑࡣࡶࡷࠬோ")] = str(parsed_url.password)
  return bstack111l111ll_opy_
def bstack11lllll11_opy_(config):
  if bstack111lll1l_opy_ (u"ࠪࡸࡪࡹࡴࡄࡱࡱࡸࡪࡾࡴࡐࡲࡷ࡭ࡴࡴࡳࠨௌ") in config:
    return config[bstack111lll1l_opy_ (u"ࠫࡹ࡫ࡳࡵࡅࡲࡲࡹ࡫ࡸࡵࡑࡳࡸ࡮ࡵ࡮ࡴ்ࠩ")]
  return {}
def bstack111llll1_opy_(caps):
  global bstack111l1ll1_opy_
  if bstack111lll1l_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯࠿ࡵࡰࡵ࡫ࡲࡲࡸ࠭௎") in caps:
    caps[bstack111lll1l_opy_ (u"࠭ࡢࡴࡶࡤࡧࡰࡀ࡯ࡱࡶ࡬ࡳࡳࡹࠧ௏")][bstack111lll1l_opy_ (u"ࠧ࡭ࡱࡦࡥࡱ࠭ௐ")] = True
    if bstack111l1ll1_opy_:
      caps[bstack111lll1l_opy_ (u"ࠨࡤࡶࡸࡦࡩ࡫࠻ࡱࡳࡸ࡮ࡵ࡮ࡴࠩ௑")][bstack111lll1l_opy_ (u"ࠩ࡯ࡳࡨࡧ࡬ࡊࡦࡨࡲࡹ࡯ࡦࡪࡧࡵࠫ௒")] = bstack111l1ll1_opy_
  else:
    caps[bstack111lll1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬࠰࡯ࡳࡨࡧ࡬ࠨ௓")] = True
    if bstack111l1ll1_opy_:
      caps[bstack111lll1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠱ࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ௔")] = bstack111l1ll1_opy_
def bstack1lll1111_opy_():
  global CONFIG
  if bstack111lll1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩ௕") in CONFIG and CONFIG[bstack111lll1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪ௖")]:
    bstack111l111ll_opy_ = bstack111ll1l11_opy_(CONFIG)
    bstack11ll1ll1l_opy_(CONFIG[bstack111lll1l_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪௗ")], bstack111l111ll_opy_)
def bstack11ll1ll1l_opy_(key, bstack111l111ll_opy_):
  global bstack111ll1111_opy_
  logger.info(bstack111l1lll_opy_)
  try:
    bstack111ll1111_opy_ = Local()
    bstack1ll1lll1_opy_ = {bstack111lll1l_opy_ (u"ࠨ࡭ࡨࡽࠬ௘"): key}
    bstack1ll1lll1_opy_.update(bstack111l111ll_opy_)
    logger.debug(bstack1l1ll1111_opy_.format(str(bstack1ll1lll1_opy_)))
    bstack111ll1111_opy_.start(**bstack1ll1lll1_opy_)
    if bstack111ll1111_opy_.isRunning():
      logger.info(bstack11llllll_opy_)
  except Exception as e:
    bstack1l11ll1l_opy_(bstack1111ll1_opy_.format(str(e)))
def bstack11l1l1_opy_():
  global bstack111ll1111_opy_
  if bstack111ll1111_opy_.isRunning():
    logger.info(bstack111lllll1_opy_)
    bstack111ll1111_opy_.stop()
  bstack111ll1111_opy_ = None
def bstack1l11lll1_opy_(bstack1l1l1ll_opy_=[]):
  global CONFIG
  bstack1lll1l1l_opy_ = []
  bstack11111111_opy_ = [bstack111lll1l_opy_ (u"ࠩࡲࡷࠬ௙"), bstack111lll1l_opy_ (u"ࠪࡳࡸ࡜ࡥࡳࡵ࡬ࡳࡳ࠭௚"), bstack111lll1l_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࡒࡦࡳࡥࠨ௛"), bstack111lll1l_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡖࡦࡴࡶ࡭ࡴࡴࠧ௜"), bstack111lll1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡎࡢ࡯ࡨࠫ௝"), bstack111lll1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨ௞")]
  try:
    for err in bstack1l1l1ll_opy_:
      bstack1llll1l1_opy_ = {}
      for k in bstack11111111_opy_:
        val = CONFIG[bstack111lll1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ௟")][int(err[bstack111lll1l_opy_ (u"ࠩ࡬ࡲࡩ࡫ࡸࠨ௠")])].get(k)
        if val:
          bstack1llll1l1_opy_[k] = val
      bstack1llll1l1_opy_[bstack111lll1l_opy_ (u"ࠪࡸࡪࡹࡴࡴࠩ௡")] = {
        err[bstack111lll1l_opy_ (u"ࠫࡳࡧ࡭ࡦࠩ௢")]: err[bstack111lll1l_opy_ (u"ࠬ࡫ࡲࡳࡱࡵࠫ௣")]
      }
      bstack1lll1l1l_opy_.append(bstack1llll1l1_opy_)
  except Exception as e:
    logger.debug(bstack111lll1l_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡨࡲࡶࡲࡧࡴࡵ࡫ࡱ࡫ࠥࡪࡡࡵࡣࠣࡪࡴࡸࠠࡦࡸࡨࡲࡹࡀࠠࠨ௤") +str(e))
  finally:
    return bstack1lll1l1l_opy_
def bstack1ll1l11l_opy_():
  global bstack1l111ll11_opy_
  global bstack1lll_opy_
  global bstack1111l11l_opy_
  if bstack1l111ll11_opy_:
    logger.warning(bstack111111_opy_.format(str(bstack1l111ll11_opy_)))
  logger.info(bstack1ll11lll1_opy_)
  global bstack111ll1111_opy_
  if bstack111ll1111_opy_:
    bstack11l1l1_opy_()
  try:
    for driver in bstack1lll_opy_:
      driver.quit()
  except Exception as e:
    pass
  logger.info(bstack111lllll_opy_)
  bstack1ll1l1l_opy_()
  if len(bstack1111l11l_opy_) > 0:
    message = bstack1l11lll1_opy_(bstack1111l11l_opy_)
    bstack1ll1l1l_opy_(message)
  else:
    bstack1ll1l1l_opy_()
def bstack11ll11l_opy_(self, *args):
  logger.error(bstack1l1lll1l_opy_)
  bstack1ll1l11l_opy_()
  sys.exit(1)
def bstack1l11ll1l_opy_(err):
  logger.critical(bstack1lll1l1l1_opy_.format(str(err)))
  bstack1ll1l1l_opy_(bstack1lll1l1l1_opy_.format(str(err)))
  atexit.unregister(bstack1ll1l11l_opy_)
  sys.exit(1)
def bstack1ll1111l_opy_(error, message):
  logger.critical(str(error))
  logger.critical(message)
  bstack1ll1l1l_opy_(message)
  atexit.unregister(bstack1ll1l11l_opy_)
  sys.exit(1)
def bstack1l1l111_opy_():
  global CONFIG
  global bstack1l1ll1ll_opy_
  global bstack1ll11l1l_opy_
  global bstack1lllll111_opy_
  CONFIG = bstack11ll1111l_opy_()
  bstack11l111l_opy_()
  bstack11l1lll_opy_()
  CONFIG = bstack1ll111l11_opy_(CONFIG)
  update(CONFIG, bstack1ll11l1l_opy_)
  update(CONFIG, bstack1l1ll1ll_opy_)
  CONFIG = bstack1ll1lll1l_opy_(CONFIG)
  if bstack111lll1l_opy_ (u"ࠧࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࠫ௥") in CONFIG and str(CONFIG[bstack111lll1l_opy_ (u"ࠨࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࠬ௦")]).lower() == bstack111lll1l_opy_ (u"ࠩࡩࡥࡱࡹࡥࠨ௧"):
    bstack1lllll111_opy_ = False
  if (bstack111lll1l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭௨") in CONFIG and bstack111lll1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡑࡥࡲ࡫ࠧ௩") in bstack1l1ll1ll_opy_) or (bstack111lll1l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨ௪") in CONFIG and bstack111lll1l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩ௫") not in bstack1ll11l1l_opy_):
    if os.getenv(bstack111lll1l_opy_ (u"ࠧࡃࡕࡗࡅࡈࡑ࡟ࡄࡑࡐࡆࡎࡔࡅࡅࡡࡅ࡙ࡎࡒࡄࡠࡋࡇࠫ௬")):
      CONFIG[bstack111lll1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪ௭")] = os.getenv(bstack111lll1l_opy_ (u"ࠩࡅࡗ࡙ࡇࡃࡌࡡࡆࡓࡒࡈࡉࡏࡇࡇࡣࡇ࡛ࡉࡍࡆࡢࡍࡉ࠭௮"))
    else:
      bstack1111l1_opy_()
  elif (bstack111lll1l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭௯") not in CONFIG and bstack111lll1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭௰") in CONFIG) or (bstack111lll1l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨ௱") in bstack1ll11l1l_opy_ and bstack111lll1l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦࠩ௲") not in bstack1l1ll1ll_opy_):
    del(CONFIG[bstack111lll1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩ௳")])
  if bstack1111llll_opy_(CONFIG):
    bstack1l11ll1l_opy_(bstack1ll1l111_opy_)
  bstack1ll1l1_opy_()
  bstack1lll1ll11_opy_()
  if bstack111llll11_opy_:
    CONFIG[bstack111lll1l_opy_ (u"ࠨࡣࡳࡴࠬ௴")] = bstack1111l111_opy_(CONFIG)
    logger.info(bstack11l1lll1l_opy_.format(CONFIG[bstack111lll1l_opy_ (u"ࠩࡤࡴࡵ࠭௵")]))
def bstack1lll1ll11_opy_():
  global CONFIG
  global bstack111llll11_opy_
  if bstack111lll1l_opy_ (u"ࠪࡥࡵࡶࠧ௶") in CONFIG:
    try:
      from appium import version
    except Exception as e:
      bstack1ll1111l_opy_(e, bstack1l1lllll_opy_)
    bstack111llll11_opy_ = True
def bstack1111l111_opy_(config):
  bstack1ll1_opy_ = bstack111lll1l_opy_ (u"ࠫࠬ௷")
  app = config[bstack111lll1l_opy_ (u"ࠬࡧࡰࡱࠩ௸")]
  if isinstance(app, str):
    if os.path.splitext(app)[1] in bstack1l1ll1l1l_opy_:
      if os.path.exists(app):
        bstack1ll1_opy_ = bstack1l11111l1_opy_(config, app)
      elif bstack11llll1l_opy_(app):
        bstack1ll1_opy_ = app
      else:
        bstack1l11ll1l_opy_(bstack1ll11l1l1_opy_.format(app))
    else:
      if bstack11llll1l_opy_(app):
        bstack1ll1_opy_ = app
      elif os.path.exists(app):
        bstack1ll1_opy_ = bstack1l11111l1_opy_(app)
      else:
        bstack1l11ll1l_opy_(bstack11lll1_opy_)
  else:
    if len(app) > 2:
      bstack1l11ll1l_opy_(bstack1ll1l111l_opy_)
    elif len(app) == 2:
      if bstack111lll1l_opy_ (u"࠭ࡰࡢࡶ࡫ࠫ௹") in app and bstack111lll1l_opy_ (u"ࠧࡤࡷࡶࡸࡴࡳ࡟ࡪࡦࠪ௺") in app:
        if os.path.exists(app[bstack111lll1l_opy_ (u"ࠨࡲࡤࡸ࡭࠭௻")]):
          bstack1ll1_opy_ = bstack1l11111l1_opy_(config, app[bstack111lll1l_opy_ (u"ࠩࡳࡥࡹ࡮ࠧ௼")], app[bstack111lll1l_opy_ (u"ࠪࡧࡺࡹࡴࡰ࡯ࡢ࡭ࡩ࠭௽")])
        else:
          bstack1l11ll1l_opy_(bstack1ll11l1l1_opy_.format(app))
      else:
        bstack1l11ll1l_opy_(bstack1ll1l111l_opy_)
    else:
      for key in app:
        if key in bstack1ll1l11l1_opy_:
          if key == bstack111lll1l_opy_ (u"ࠫࡵࡧࡴࡩࠩ௾"):
            if os.path.exists(app[key]):
              bstack1ll1_opy_ = bstack1l11111l1_opy_(config, app[key])
            else:
              bstack1l11ll1l_opy_(bstack1ll11l1l1_opy_.format(app))
          else:
            bstack1ll1_opy_ = app[key]
        else:
          bstack1l11ll1l_opy_(bstack1l1l11l11_opy_)
  return bstack1ll1_opy_
def bstack11llll1l_opy_(bstack1ll1_opy_):
  import re
  bstack11lll1lll_opy_ = re.compile(bstack111lll1l_opy_ (u"ࡷࠨ࡞࡜ࡣ࠰ࡾࡆ࠳࡚࠱࠯࠼ࡠࡤ࠴࡜࠮࡟࠭ࠨࠧ௿"))
  bstack1lll11l_opy_ = re.compile(bstack111lll1l_opy_ (u"ࡸࠢ࡟࡝ࡤ࠱ࡿࡇ࡛࠭࠲࠰࠽ࡡࡥ࠮࡝࠯ࡠ࠮࠴ࡡࡡ࠮ࡼࡄ࠱࡟࠶࠭࠺࡞ࡢ࠲ࡡ࠳࡝ࠫࠦࠥఀ"))
  if bstack111lll1l_opy_ (u"ࠧࡣࡵ࠽࠳࠴࠭ఁ") in bstack1ll1_opy_ or re.fullmatch(bstack11lll1lll_opy_, bstack1ll1_opy_) or re.fullmatch(bstack1lll11l_opy_, bstack1ll1_opy_):
    return True
  else:
    return False
def bstack1l11111l1_opy_(config, path, bstack1111l11_opy_=None):
  import requests
  from requests_toolbelt.multipart.encoder import MultipartEncoder
  import hashlib
  md5_hash = hashlib.md5(open(os.path.abspath(path), bstack111lll1l_opy_ (u"ࠨࡴࡥࠫం")).read()).hexdigest()
  bstack111ll1l1l_opy_ = bstack11ll1ll11_opy_(md5_hash)
  bstack1ll1_opy_ = None
  if bstack111ll1l1l_opy_:
    logger.info(bstack1l11l111_opy_.format(bstack111ll1l1l_opy_, md5_hash))
    return bstack111ll1l1l_opy_
  bstack111l1_opy_ = MultipartEncoder(
    fields={
        bstack111lll1l_opy_ (u"ࠩࡩ࡭ࡱ࡫ࠧః"): (os.path.basename(path), open(os.path.abspath(path), bstack111lll1l_opy_ (u"ࠪࡶࡧ࠭ఄ")), bstack111lll1l_opy_ (u"ࠫࡹ࡫ࡸࡵ࠱ࡳࡰࡦ࡯࡮ࠨఅ")),
        bstack111lll1l_opy_ (u"ࠬࡩࡵࡴࡶࡲࡱࡤ࡯ࡤࠨఆ"): bstack1111l11_opy_
    }
  )
  response = requests.post(bstack11l1lll1_opy_, data=bstack111l1_opy_,
                         headers={bstack111lll1l_opy_ (u"࠭ࡃࡰࡰࡷࡩࡳࡺ࠭ࡕࡻࡳࡩࠬఇ"): bstack111l1_opy_.content_type}, auth=(config[bstack111lll1l_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩఈ")], config[bstack111lll1l_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫఉ")]))
  try:
    res = json.loads(response.text)
    bstack1ll1_opy_ = res[bstack111lll1l_opy_ (u"ࠩࡤࡴࡵࡥࡵࡳ࡮ࠪఊ")]
    logger.info(bstack1lll1llll_opy_.format(bstack1ll1_opy_))
    bstack1111ll11_opy_(md5_hash, bstack1ll1_opy_)
  except ValueError as err:
    bstack1l11ll1l_opy_(bstack1l11l1l_opy_.format(str(err)))
  return bstack1ll1_opy_
def bstack1ll1l1_opy_():
  global CONFIG
  global bstack1l1lll1_opy_
  bstack11l11llll_opy_ = 0
  bstack1lllllll_opy_ = 1
  if bstack111lll1l_opy_ (u"ࠪࡴࡦࡸࡡ࡭࡮ࡨࡰࡸࡖࡥࡳࡒ࡯ࡥࡹ࡬࡯ࡳ࡯ࠪఋ") in CONFIG:
    bstack1lllllll_opy_ = CONFIG[bstack111lll1l_opy_ (u"ࠫࡵࡧࡲࡢ࡮࡯ࡩࡱࡹࡐࡦࡴࡓࡰࡦࡺࡦࡰࡴࡰࠫఌ")]
  if bstack111lll1l_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ఍") in CONFIG:
    bstack11l11llll_opy_ = len(CONFIG[bstack111lll1l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩఎ")])
  bstack1l1lll1_opy_ = int(bstack1lllllll_opy_) * int(bstack11l11llll_opy_)
def bstack11ll1ll11_opy_(md5_hash):
  bstack11l11ll_opy_ = os.path.join(os.path.expanduser(bstack111lll1l_opy_ (u"ࠧࡿࠩఏ")), bstack111lll1l_opy_ (u"ࠨ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࠨఐ"), bstack111lll1l_opy_ (u"ࠩࡤࡴࡵ࡛ࡰ࡭ࡱࡤࡨࡒࡊ࠵ࡉࡣࡶ࡬࠳ࡰࡳࡰࡰࠪ఑"))
  if os.path.exists(bstack11l11ll_opy_):
    bstack1lll11ll1_opy_ = json.load(open(bstack11l11ll_opy_,bstack111lll1l_opy_ (u"ࠪࡶࡧ࠭ఒ")))
    if md5_hash in bstack1lll11ll1_opy_:
      bstack1l111l11l_opy_ = bstack1lll11ll1_opy_[md5_hash]
      bstack11111l1_opy_ = datetime.datetime.now()
      bstack1l1l1l11_opy_ = datetime.datetime.strptime(bstack1l111l11l_opy_[bstack111lll1l_opy_ (u"ࠫࡹ࡯࡭ࡦࡵࡷࡥࡲࡶࠧఓ")], bstack111lll1l_opy_ (u"ࠬࠫࡤ࠰ࠧࡰ࠳ࠪ࡟ࠠࠦࡊ࠽ࠩࡒࡀࠥࡔࠩఔ"))
      if (bstack11111l1_opy_ - bstack1l1l1l11_opy_).days > 60:
        return None
      elif version.parse(str(__version__)) > version.parse(bstack1l111l11l_opy_[bstack111lll1l_opy_ (u"࠭ࡳࡥ࡭ࡢࡺࡪࡸࡳࡪࡱࡱࠫక")]):
        return None
      return bstack1l111l11l_opy_[bstack111lll1l_opy_ (u"ࠧࡪࡦࠪఖ")]
  else:
    return None
def bstack1111ll11_opy_(md5_hash, bstack1ll1_opy_):
  bstack1ll111ll_opy_ = os.path.join(os.path.expanduser(bstack111lll1l_opy_ (u"ࠨࢀࠪగ")), bstack111lll1l_opy_ (u"ࠩ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠩఘ"))
  if not os.path.exists(bstack1ll111ll_opy_):
    os.makedirs(bstack1ll111ll_opy_)
  bstack11l11ll_opy_ = os.path.join(os.path.expanduser(bstack111lll1l_opy_ (u"ࠪࢂࠬఙ")), bstack111lll1l_opy_ (u"ࠫ࠳ࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࠫచ"), bstack111lll1l_opy_ (u"ࠬࡧࡰࡱࡗࡳࡰࡴࡧࡤࡎࡆ࠸ࡌࡦࡹࡨ࠯࡬ࡶࡳࡳ࠭ఛ"))
  bstack1l1llll11_opy_ = {
    bstack111lll1l_opy_ (u"࠭ࡩࡥࠩజ"): bstack1ll1_opy_,
    bstack111lll1l_opy_ (u"ࠧࡵ࡫ࡰࡩࡸࡺࡡ࡮ࡲࠪఝ"): datetime.datetime.strftime(datetime.datetime.now(), bstack111lll1l_opy_ (u"ࠨࠧࡧ࠳ࠪࡳ࠯࡛ࠦࠣࠩࡍࡀࠥࡎ࠼ࠨࡗࠬఞ")),
    bstack111lll1l_opy_ (u"ࠩࡶࡨࡰࡥࡶࡦࡴࡶ࡭ࡴࡴࠧట"): str(__version__)
  }
  if os.path.exists(bstack11l11ll_opy_):
    bstack1lll11ll1_opy_ = json.load(open(bstack11l11ll_opy_,bstack111lll1l_opy_ (u"ࠪࡶࡧ࠭ఠ")))
  else:
    bstack1lll11ll1_opy_ = {}
  bstack1lll11ll1_opy_[md5_hash] = bstack1l1llll11_opy_
  with open(bstack11l11ll_opy_, bstack111lll1l_opy_ (u"ࠦࡼ࠱ࠢడ")) as outfile:
    json.dump(bstack1lll11ll1_opy_, outfile)
def bstack1ll11ll11_opy_(self):
  return
def bstack1l1lll11l_opy_(self):
  return
def bstack1l1ll1l11_opy_(self):
  from selenium.webdriver.remote.webdriver import WebDriver
  WebDriver.quit(self)
def bstack11ll1l11_opy_(self):
  global bstack1lll1l11l_opy_
  global bstack11l11l111_opy_
  global bstack1llll1l1l_opy_
  try:
    if bstack111lll1l_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬఢ") in bstack1lll1l11l_opy_ and self.session_id != None:
      bstack111ll1l1_opy_ = bstack111lll1l_opy_ (u"࠭ࡰࡢࡵࡶࡩࡩ࠭ణ") if len(threading.current_thread().bstackTestErrorMessages) == 0 else bstack111lll1l_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧత")
      bstack1l1l1111l_opy_ = bstack1l1111lll_opy_(bstack111lll1l_opy_ (u"ࠨࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠫథ"), bstack111lll1l_opy_ (u"ࠩࠪద"), bstack111ll1l1_opy_, bstack111lll1l_opy_ (u"ࠪ࠰ࠥ࠭ధ").join(threading.current_thread().bstackTestErrorMessages), bstack111lll1l_opy_ (u"ࠫࠬన"), bstack111lll1l_opy_ (u"ࠬ࠭఩"))
      if self != None:
        self.execute_script(bstack1l1l1111l_opy_)
  except Exception as e:
    logger.debug(bstack111lll1l_opy_ (u"ࠨࡅࡳࡴࡲࡶࠥࡽࡨࡪ࡮ࡨࠤࡲࡧࡲ࡬࡫ࡱ࡫ࠥࡹࡴࡢࡶࡸࡷ࠿ࠦࠢప") + str(e))
  bstack1llll1l1l_opy_(self)
  self.session_id = None
def bstack1_opy_(self, command_executor,
        desired_capabilities=None, browser_profile=None, proxy=None,
        keep_alive=True, file_detector=None, options=None):
  global CONFIG
  global bstack11l11l111_opy_
  global bstack1l1l1111_opy_
  global bstack11ll1llll_opy_
  global bstack111l1ll11_opy_
  global bstack1lll1l1ll_opy_
  global bstack1lll1l11l_opy_
  global bstack111l111_opy_
  global bstack1lll_opy_
  global bstack11111l11_opy_
  CONFIG[bstack111lll1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࡙ࡄࡌࠩఫ")] = str(bstack1lll1l11l_opy_) + str(__version__)
  command_executor = bstack11l1l1l_opy_()
  logger.debug(bstack11ll1ll_opy_.format(command_executor))
  proxy = bstack1lllll1_opy_(CONFIG, proxy)
  bstack1111l1ll_opy_ = 0 if bstack1l1l1111_opy_ < 0 else bstack1l1l1111_opy_
  try:
    if bstack111l1ll11_opy_ is True:
      bstack1111l1ll_opy_ = int(multiprocessing.current_process().name)
    elif bstack1lll1l1ll_opy_ is True:
      bstack1111l1ll_opy_ = int(threading.current_thread().name)
  except:
    bstack1111l1ll_opy_ = 0
  bstack11l111l1l_opy_ = bstack11l1111ll_opy_(CONFIG, bstack1111l1ll_opy_)
  logger.debug(bstack11ll11lll_opy_.format(str(bstack11l111l1l_opy_)))
  if bstack111lll1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࡌࡰࡥࡤࡰࠬబ") in CONFIG and CONFIG[bstack111lll1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡍࡱࡦࡥࡱ࠭భ")]:
    bstack111llll1_opy_(bstack11l111l1l_opy_)
  if desired_capabilities:
    bstack1ll11lll_opy_ = bstack1ll111l11_opy_(desired_capabilities)
    bstack1ll11lll_opy_[bstack111lll1l_opy_ (u"ࠪࡹࡸ࡫ࡗ࠴ࡅࠪమ")] = bstack1llllll_opy_(CONFIG)
    bstack1111l_opy_ = bstack11l1111ll_opy_(bstack1ll11lll_opy_)
    if bstack1111l_opy_:
      bstack11l111l1l_opy_ = update(bstack1111l_opy_, bstack11l111l1l_opy_)
    desired_capabilities = None
  if options:
    bstack1l11ll111_opy_(options, bstack11l111l1l_opy_)
  if not options:
    options = bstack111l111l_opy_(bstack11l111l1l_opy_)
  if proxy and bstack1l111lll_opy_() >= version.parse(bstack111lll1l_opy_ (u"ࠫ࠹࠴࠱࠱࠰࠳ࠫయ")):
    options.proxy(proxy)
  if options and bstack1l111lll_opy_() >= version.parse(bstack111lll1l_opy_ (u"ࠬ࠹࠮࠹࠰࠳ࠫర")):
    desired_capabilities = None
  if (
      not options and not desired_capabilities
  ) or (
      bstack1l111lll_opy_() < version.parse(bstack111lll1l_opy_ (u"࠭࠳࠯࠺࠱࠴ࠬఱ")) and not desired_capabilities
  ):
    desired_capabilities = {}
    desired_capabilities.update(bstack11l111l1l_opy_)
  logger.info(bstack1l1lll11_opy_)
  if bstack1l111lll_opy_() >= version.parse(bstack111lll1l_opy_ (u"ࠧ࠵࠰࠴࠴࠳࠶ࠧల")):
    bstack111l111_opy_(self, command_executor=command_executor,
          options=options, keep_alive=keep_alive, file_detector=file_detector)
  elif bstack1l111lll_opy_() >= version.parse(bstack111lll1l_opy_ (u"ࠨ࠵࠱࠼࠳࠶ࠧళ")):
    bstack111l111_opy_(self, command_executor=command_executor,
          desired_capabilities=desired_capabilities, options=options,
          browser_profile=browser_profile, proxy=proxy,
          keep_alive=keep_alive, file_detector=file_detector)
  elif bstack1l111lll_opy_() >= version.parse(bstack111lll1l_opy_ (u"ࠩ࠵࠲࠺࠹࠮࠱ࠩఴ")):
    bstack111l111_opy_(self, command_executor=command_executor,
          desired_capabilities=desired_capabilities,
          browser_profile=browser_profile, proxy=proxy,
          keep_alive=keep_alive, file_detector=file_detector)
  else:
    bstack111l111_opy_(self, command_executor=command_executor,
          desired_capabilities=desired_capabilities,
          browser_profile=browser_profile, proxy=proxy,
          keep_alive=keep_alive)
  try:
    bstack1l111l1ll_opy_ = bstack111lll1l_opy_ (u"ࠪࠫవ")
    if bstack1l111lll_opy_() >= version.parse(bstack111lll1l_opy_ (u"ࠫ࠹࠴࠰࠯࠲ࡥ࠵ࠬశ")):
      bstack1l111l1ll_opy_ = self.caps.get(bstack111lll1l_opy_ (u"ࠧࡵࡰࡵ࡫ࡰࡥࡱࡎࡵࡣࡗࡵࡰࠧష"))
    else:
      bstack1l111l1ll_opy_ = self.capabilities.get(bstack111lll1l_opy_ (u"ࠨ࡯ࡱࡶ࡬ࡱࡦࡲࡈࡶࡤࡘࡶࡱࠨస"))
    if bstack1l111l1ll_opy_:
      if bstack1l111lll_opy_() <= version.parse(bstack111lll1l_opy_ (u"ࠧ࠴࠰࠴࠷࠳࠶ࠧహ")):
        self.command_executor._url = bstack111lll1l_opy_ (u"ࠣࡪࡷࡸࡵࡀ࠯࠰ࠤ఺") + bstack1l111ll1_opy_ + bstack111lll1l_opy_ (u"ࠤ࠽࠼࠵࠵ࡷࡥ࠱࡫ࡹࡧࠨ఻")
      else:
        self.command_executor._url = bstack111lll1l_opy_ (u"ࠥ࡬ࡹࡺࡰࡴ࠼࠲࠳఼ࠧ") + bstack1l111l1ll_opy_ + bstack111lll1l_opy_ (u"ࠦ࠴ࡽࡤ࠰ࡪࡸࡦࠧఽ")
      logger.debug(bstack1111l1l1_opy_.format(bstack1l111l1ll_opy_))
    else:
      logger.debug(bstack1ll1111_opy_.format(bstack111lll1l_opy_ (u"ࠧࡕࡰࡵ࡫ࡰࡥࡱࠦࡈࡶࡤࠣࡲࡴࡺࠠࡧࡱࡸࡲࡩࠨా")))
  except Exception as e:
    logger.debug(bstack1ll1111_opy_.format(e))
  if bstack111lll1l_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬి") in bstack1lll1l11l_opy_:
    bstack1lll11ll_opy_(bstack1l1l1111_opy_, bstack11111l11_opy_)
  bstack11l11l111_opy_ = self.session_id
  if bstack111lll1l_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧీ") in bstack1lll1l11l_opy_ or bstack111lll1l_opy_ (u"ࠨࡤࡨ࡬ࡦࡼࡥࠨు") in bstack1lll1l11l_opy_:
    threading.current_thread().bstack1l1l11ll1_opy_ = self.session_id
    threading.current_thread().bstackSessionDriver = self
    threading.current_thread().bstackTestErrorMessages = []
  bstack1lll_opy_.append(self)
  if bstack111lll1l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬూ") in CONFIG and bstack111lll1l_opy_ (u"ࠪࡷࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨృ") in CONFIG[bstack111lll1l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧౄ")][bstack1111l1ll_opy_]:
    bstack11ll1llll_opy_ = CONFIG[bstack111lll1l_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨ౅")][bstack1111l1ll_opy_][bstack111lll1l_opy_ (u"࠭ࡳࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫె")]
  logger.debug(bstack1lll11lll_opy_.format(bstack11l11l111_opy_))
try:
  try:
    import Browser
    from subprocess import Popen
    def bstack1l111_opy_(self, args, bufsize=-1, executable=None,
              stdin=None, stdout=None, stderr=None,
              preexec_fn=None, close_fds=True,
              shell=False, cwd=None, env=None, universal_newlines=None,
              startupinfo=None, creationflags=0,
              restore_signals=True, start_new_session=False,
              pass_fds=(), *, user=None, group=None, extra_groups=None,
              encoding=None, errors=None, text=None, umask=-1, pipesize=-1):
      global CONFIG
      global bstack1l1111l1_opy_
      if(bstack111lll1l_opy_ (u"ࠢࡪࡰࡧࡩࡽ࠴ࡪࡴࠤే") in args[1]):
        with open(os.path.join(os.path.expanduser(bstack111lll1l_opy_ (u"ࠨࢀࠪై")), bstack111lll1l_opy_ (u"ࠩ࠱ࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠩ౉"), bstack111lll1l_opy_ (u"ࠪ࠲ࡸ࡫ࡳࡴ࡫ࡲࡲ࡮ࡪࡳ࠯ࡶࡻࡸࠬొ")), bstack111lll1l_opy_ (u"ࠫࡼ࠭ో")) as fp:
          fp.write(bstack111lll1l_opy_ (u"ࠧࠨౌ"))
        if(not os.path.exists(os.path.join(os.path.dirname(args[1]), bstack111lll1l_opy_ (u"ࠨࡩ࡯ࡦࡨࡼࡤࡨࡳࡵࡣࡦ࡯࠳ࡰࡳ్ࠣ")))):
          with open(args[1], bstack111lll1l_opy_ (u"ࠧࡳࠩ౎")) as f:
            lines = f.readlines()
            index = next((i for i, line in enumerate(lines) if bstack111lll1l_opy_ (u"ࠨࡣࡶࡽࡳࡩࠠࡧࡷࡱࡧࡹ࡯࡯࡯ࠢࡢࡲࡪࡽࡐࡢࡩࡨࠬࡨࡵ࡮ࡵࡧࡻࡸ࠱ࠦࡰࡢࡩࡨࠤࡂࠦࡶࡰ࡫ࡧࠤ࠵࠯ࠧ౏") in line), None)
            if index is not None:
                lines.insert(index+2, bstackl_opy_)
            lines.insert(1, bstack111_opy_)
            f.seek(0)
            with open(os.path.join(os.path.dirname(args[1]), bstack111lll1l_opy_ (u"ࠤ࡬ࡲࡩ࡫ࡸࡠࡤࡶࡸࡦࡩ࡫࠯࡬ࡶࠦ౐")), bstack111lll1l_opy_ (u"ࠪࡻࠬ౑")) as bstack1111lllll_opy_:
              bstack1111lllll_opy_.writelines(lines)
        CONFIG[bstack111lll1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡖࡈࡐ࠭౒")] = str(bstack1lll1l11l_opy_) + str(__version__)
        bstack1111l1ll_opy_ = 0 if bstack1l1l1111_opy_ < 0 else bstack1l1l1111_opy_
        if bstack111l1ll11_opy_ is True:
          bstack1111l1ll_opy_ = int(threading.current_thread().getName())
        CONFIG[bstack111lll1l_opy_ (u"ࠧࡻࡳࡦ࡙࠶ࡇࠧ౓")] = False
        CONFIG[bstack111lll1l_opy_ (u"ࠨࡩࡴࡒ࡯ࡥࡾࡽࡲࡪࡩ࡫ࡸࠧ౔")] = True
        bstack11l111l1l_opy_ = bstack11l1111ll_opy_(CONFIG, bstack1111l1ll_opy_)
        logger.debug(bstack11ll11lll_opy_.format(str(bstack11l111l1l_opy_)))
        if CONFIG[bstack111lll1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡒ࡯ࡤࡣ࡯ౕࠫ")]:
          bstack111llll1_opy_(bstack11l111l1l_opy_)
        if bstack111lll1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶౖࠫ") in CONFIG and bstack111lll1l_opy_ (u"ࠩࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠧ౗") in CONFIG[bstack111lll1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭ౘ")][bstack1111l1ll_opy_]:
          bstack11ll1llll_opy_ = CONFIG[bstack111lll1l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧౙ")][bstack1111l1ll_opy_][bstack111lll1l_opy_ (u"ࠬࡹࡥࡴࡵ࡬ࡳࡳࡔࡡ࡮ࡧࠪౚ")]
        args.append(os.path.join(os.path.expanduser(bstack111lll1l_opy_ (u"࠭ࡾࠨ౛")), bstack111lll1l_opy_ (u"ࠧ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱࠧ౜"), bstack111lll1l_opy_ (u"ࠨ࠰ࡶࡩࡸࡹࡩࡰࡰ࡬ࡨࡸ࠴ࡴࡹࡶࠪౝ")))
        args.append(str(threading.get_ident()))
        args.append(json.dumps(bstack11l111l1l_opy_))
        args[1] = os.path.join(os.path.dirname(args[1]), bstack111lll1l_opy_ (u"ࠤ࡬ࡲࡩ࡫ࡸࡠࡤࡶࡸࡦࡩ࡫࠯࡬ࡶࠦ౞"))
      bstack1l1111l1_opy_ = True
      return bstack111ll1_opy_(self, args, bufsize=bufsize, executable=executable,
                    stdin=stdin, stdout=stdout, stderr=stderr,
                    preexec_fn=preexec_fn, close_fds=close_fds,
                    shell=shell, cwd=cwd, env=env, universal_newlines=universal_newlines,
                    startupinfo=startupinfo, creationflags=creationflags,
                    restore_signals=restore_signals, start_new_session=start_new_session,
                    pass_fds=pass_fds, user=user, group=group, extra_groups=extra_groups,
                    encoding=encoding, errors=errors, text=text, umask=umask, pipesize=pipesize)
  except Exception as e:
    pass
  import playwright._impl._api_structures
  import playwright._impl._helper
  def bstack1l11l1l1l_opy_(self,
        executablePath = None,
        channel = None,
        args = None,
        ignoreDefaultArgs = None,
        handleSIGINT = None,
        handleSIGTERM = None,
        handleSIGHUP = None,
        timeout = None,
        env = None,
        headless = None,
        devtools = None,
        proxy = None,
        downloadsPath = None,
        slowMo = None,
        tracesDir = None,
        chromiumSandbox = None,
        firefoxUserPrefs = None
        ):
    global CONFIG
    global bstack11l11l111_opy_
    global bstack1l1l1111_opy_
    global bstack11ll1llll_opy_
    global bstack111l1ll11_opy_
    global bstack1lll1l11l_opy_
    global bstack111l111_opy_
    CONFIG[bstack111lll1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡕࡇࡏࠬ౟")] = str(bstack1lll1l11l_opy_) + str(__version__)
    bstack1111l1ll_opy_ = 0 if bstack1l1l1111_opy_ < 0 else bstack1l1l1111_opy_
    if bstack111l1ll11_opy_ is True:
      bstack1111l1ll_opy_ = int(threading.current_thread().getName())
    CONFIG[bstack111lll1l_opy_ (u"ࠦ࡮ࡹࡐ࡭ࡣࡼࡻࡷ࡯ࡧࡩࡶࠥౠ")] = True
    bstack11l111l1l_opy_ = bstack11l1111ll_opy_(CONFIG, bstack1111l1ll_opy_)
    logger.debug(bstack11ll11lll_opy_.format(str(bstack11l111l1l_opy_)))
    if CONFIG[bstack111lll1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩౡ")]:
      bstack111llll1_opy_(bstack11l111l1l_opy_)
    if bstack111lll1l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩౢ") in CONFIG and bstack111lll1l_opy_ (u"ࠧࡴࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠬౣ") in CONFIG[bstack111lll1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ౤")][bstack1111l1ll_opy_]:
      bstack11ll1llll_opy_ = CONFIG[bstack111lll1l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ౥")][bstack1111l1ll_opy_][bstack111lll1l_opy_ (u"ࠪࡷࡪࡹࡳࡪࡱࡱࡒࡦࡳࡥࠨ౦")]
    import urllib
    import json
    bstack11lll1l_opy_ = bstack111lll1l_opy_ (u"ࠫࡼࡹࡳ࠻࠱࠲ࡧࡩࡶ࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰ࡯࠲ࡴࡱࡧࡹࡸࡴ࡬࡫࡭ࡺ࠿ࡤࡣࡳࡷࡂ࠭౧") + urllib.parse.quote(json.dumps(bstack11l111l1l_opy_))
    browser = self.connect(bstack11lll1l_opy_)
    return browser
except Exception as e:
    pass
def bstack11l11l_opy_():
    global bstack1l1111l1_opy_
    try:
        from playwright._impl._browser_type import BrowserType
        BrowserType.launch = bstack1l11l1l1l_opy_
        bstack1l1111l1_opy_ = True
    except Exception as e:
        pass
    try:
      import Browser
      from subprocess import Popen
      Popen.__init__ = bstack1l111_opy_
      bstack1l1111l1_opy_ = True
    except Exception as e:
      pass
def bstack1lllll11_opy_(context, bstack1llll11ll_opy_):
  try:
    context.page.evaluate(bstack111lll1l_opy_ (u"ࠧࡥࠠ࠾ࡀࠣࡿࢂࠨ౨"), bstack111lll1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠢ࠭ࠢࠥࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸࠨ࠺ࠡࡽࠥࡲࡦࡳࡥࠣ࠼ࠪ౩")+ json.dumps(bstack1llll11ll_opy_) + bstack111lll1l_opy_ (u"ࠢࡾࡿࠥ౪"))
  except Exception as e:
    logger.debug(bstack111lll1l_opy_ (u"ࠣࡧࡻࡧࡪࡶࡴࡪࡱࡱࠤ࡮ࡴࠠࡱ࡮ࡤࡽࡼࡸࡩࡨࡪࡷࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡴࡡ࡮ࡧࠣࡿࢂࠨ౫"), e)
def bstack11111ll_opy_(context, message, level):
  try:
    context.page.evaluate(bstack111lll1l_opy_ (u"ࠤࡢࠤࡂࡄࠠࡼࡿࠥ౬"), bstack111lll1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡥࡳࡴ࡯ࡵࡣࡷࡩࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡦࡤࡸࡦࠨ࠺ࠨ౭") + json.dumps(message) + bstack111lll1l_opy_ (u"ࠫ࠱ࠨ࡬ࡦࡸࡨࡰࠧࡀࠧ౮") + json.dumps(level) + bstack111lll1l_opy_ (u"ࠬࢃࡽࠨ౯"))
  except Exception as e:
    logger.debug(bstack111lll1l_opy_ (u"ࠨࡥࡹࡥࡨࡴࡹ࡯࡯࡯ࠢ࡬ࡲࠥࡶ࡬ࡢࡻࡺࡶ࡮࡭ࡨࡵࠢࡤࡲࡳࡵࡴࡢࡶ࡬ࡳࡳࠦࡻࡾࠤ౰"), e)
def bstack11lll111_opy_(context, status, message = bstack111lll1l_opy_ (u"ࠢࠣ౱")):
  try:
    if(status == bstack111lll1l_opy_ (u"ࠣࡨࡤ࡭ࡱ࡫ࡤࠣ౲")):
      context.page.evaluate(bstack111lll1l_opy_ (u"ࠤࡢࠤࡂࡄࠠࡼࡿࠥ౳"), bstack111lll1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡨࡼࡪࡩࡵࡵࡱࡵ࠾ࠥࢁࠢࡢࡥࡷ࡭ࡴࡴࠢ࠻ࠢࠥࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡓࡵࡣࡷࡹࡸࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡵࡩࡦࡹ࡯࡯ࠤ࠽ࠫ౴") + json.dumps(bstack111lll1l_opy_ (u"ࠦࡘࡩࡥ࡯ࡣࡵ࡭ࡴࠦࡦࡢ࡫࡯ࡩࡩࠦࡷࡪࡶ࡫࠾ࠥࠨ౵") + str(message)) + bstack111lll1l_opy_ (u"ࠬ࠲ࠢࡴࡶࡤࡸࡺࡹࠢ࠻ࠩ౶") + json.dumps(status) + bstack111lll1l_opy_ (u"ࠨࡽࡾࠤ౷"))
    else:
      context.page.evaluate(bstack111lll1l_opy_ (u"ࠢࡠࠢࡀࡂࠥࢁࡽࠣ౸"), bstack111lll1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢࡴࡶࡤࡸࡺࡹࠢ࠻ࠩ౹") + json.dumps(status) + bstack111lll1l_opy_ (u"ࠤࢀࢁࠧ౺"))
  except Exception as e:
    logger.debug(bstack111lll1l_opy_ (u"ࠥࡩࡽࡩࡥࡱࡶ࡬ࡳࡳࠦࡩ࡯ࠢࡳࡰࡦࡿࡷࡳ࡫ࡪ࡬ࡹࠦࡳࡦࡶࠣࡷࡪࡹࡳࡪࡱࡱࠤࡸࡺࡡࡵࡷࡶࠤࢀࢃࠢ౻"), e)
def bstack11lll1ll1_opy_(self, url):
  global bstack1111ll1l_opy_
  try:
    bstack1llll1111_opy_(url)
  except Exception as err:
    logger.debug(bstack1l1llll1l_opy_.format(str(err)))
  try:
    bstack1111ll1l_opy_(self, url)
  except Exception as e:
    try:
      bstack1ll1lllll_opy_ = str(e)
      if any(err_msg in bstack1ll1lllll_opy_ for err_msg in bstack11ll1_opy_):
        bstack1llll1111_opy_(url, True)
    except Exception as err:
      logger.debug(bstack1l1llll1l_opy_.format(str(err)))
    raise e
def bstack111l11111_opy_(self):
  global bstack111ll11l_opy_
  bstack111ll11l_opy_ = self
  return
def bstack11l1111l1_opy_(self):
  global bstack1ll11ll1l_opy_
  bstack1ll11ll1l_opy_ = self
  return
def bstack1l1l1l111_opy_(self, test):
  global CONFIG
  global bstack1ll11ll1l_opy_
  global bstack111ll11l_opy_
  global bstack11l11l111_opy_
  global bstack1llll111_opy_
  global bstack11ll1llll_opy_
  global bstack1l1lll_opy_
  global bstack111lll11_opy_
  global bstack1l11ll1_opy_
  global bstack1lll_opy_
  try:
    if not bstack11l11l111_opy_:
      with open(os.path.join(os.path.expanduser(bstack111lll1l_opy_ (u"ࠫࢃ࠭౼")), bstack111lll1l_opy_ (u"ࠬ࠴ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠬ౽"), bstack111lll1l_opy_ (u"࠭࠮ࡴࡧࡶࡷ࡮ࡵ࡮ࡪࡦࡶ࠲ࡹࡾࡴࠨ౾"))) as f:
        bstack1l1l111l1_opy_ = json.loads(bstack111lll1l_opy_ (u"ࠢࡼࠤ౿") + f.read().strip() + bstack111lll1l_opy_ (u"ࠨࠤࡻࠦ࠿ࠦࠢࡺࠤࠪಀ") + bstack111lll1l_opy_ (u"ࠤࢀࠦಁ"))
        bstack11l11l111_opy_ = bstack1l1l111l1_opy_[str(threading.get_ident())]
  except:
    pass
  if bstack1lll_opy_:
    for driver in bstack1lll_opy_:
      if bstack11l11l111_opy_ == driver.session_id:
        if test:
          bstack1l1ll11l1_opy_ = str(test.data)
        if not bstack1ll1ll11_opy_ and bstack1l1ll11l1_opy_:
          bstack11lll1l1l_opy_ = {
            bstack111lll1l_opy_ (u"ࠪࡥࡨࡺࡩࡰࡰࠪಂ"): bstack111lll1l_opy_ (u"ࠫࡸ࡫ࡴࡔࡧࡶࡷ࡮ࡵ࡮ࡏࡣࡰࡩࠬಃ"),
            bstack111lll1l_opy_ (u"ࠬࡧࡲࡨࡷࡰࡩࡳࡺࡳࠨ಄"): {
              bstack111lll1l_opy_ (u"࠭࡮ࡢ࡯ࡨࠫಅ"): bstack1l1ll11l1_opy_
            }
          }
          bstack1l1l1l1ll_opy_ = bstack111lll1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࢁࠬಆ").format(json.dumps(bstack11lll1l1l_opy_))
          driver.execute_script(bstack1l1l1l1ll_opy_)
        if bstack1llll111_opy_:
          bstack1lllll11l_opy_ = {
            bstack111lll1l_opy_ (u"ࠨࡣࡦࡸ࡮ࡵ࡮ࠨಇ"): bstack111lll1l_opy_ (u"ࠩࡤࡲࡳࡵࡴࡢࡶࡨࠫಈ"),
            bstack111lll1l_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭ಉ"): {
              bstack111lll1l_opy_ (u"ࠫࡩࡧࡴࡢࠩಊ"): bstack1l1ll11l1_opy_ + bstack111lll1l_opy_ (u"ࠬࠦࡰࡢࡵࡶࡩࡩࠧࠧಋ"),
              bstack111lll1l_opy_ (u"࠭࡬ࡦࡸࡨࡰࠬಌ"): bstack111lll1l_opy_ (u"ࠧࡪࡰࡩࡳࠬ಍")
            }
          }
          bstack11lll1l1l_opy_ = {
            bstack111lll1l_opy_ (u"ࠨࡣࡦࡸ࡮ࡵ࡮ࠨಎ"): bstack111lll1l_opy_ (u"ࠩࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷࠬಏ"),
            bstack111lll1l_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭ಐ"): {
              bstack111lll1l_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫ಑"): bstack111lll1l_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬಒ")
            }
          }
          if bstack1llll111_opy_.status == bstack111lll1l_opy_ (u"࠭ࡐࡂࡕࡖࠫಓ"):
            bstack1ll1l1l1l_opy_ = bstack111lll1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࢁࠬಔ").format(json.dumps(bstack1lllll11l_opy_))
            driver.execute_script(bstack1ll1l1l1l_opy_)
            bstack1l1l1l1ll_opy_ = bstack111lll1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࢂ࠭ಕ").format(json.dumps(bstack11lll1l1l_opy_))
            driver.execute_script(bstack1l1l1l1ll_opy_)
          elif bstack1llll111_opy_.status == bstack111lll1l_opy_ (u"ࠩࡉࡅࡎࡒࠧಖ"):
            reason = bstack111lll1l_opy_ (u"ࠥࠦಗ")
            bstack11lll11_opy_ = bstack1l1ll11l1_opy_ + bstack111lll1l_opy_ (u"ࠫࠥ࡬ࡡࡪ࡮ࡨࡨࠬಘ")
            if bstack1llll111_opy_.message:
              reason = str(bstack1llll111_opy_.message)
              bstack11lll11_opy_ = bstack11lll11_opy_ + bstack111lll1l_opy_ (u"ࠬࠦࡷࡪࡶ࡫ࠤࡪࡸࡲࡰࡴ࠽ࠤࠬಙ") + reason
            bstack1lllll11l_opy_[bstack111lll1l_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩಚ")] = {
              bstack111lll1l_opy_ (u"ࠧ࡭ࡧࡹࡩࡱ࠭ಛ"): bstack111lll1l_opy_ (u"ࠨࡧࡵࡶࡴࡸࠧಜ"),
              bstack111lll1l_opy_ (u"ࠩࡧࡥࡹࡧࠧಝ"): bstack11lll11_opy_
            }
            bstack11lll1l1l_opy_[bstack111lll1l_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭ಞ")] = {
              bstack111lll1l_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫಟ"): bstack111lll1l_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬಠ"),
              bstack111lll1l_opy_ (u"࠭ࡲࡦࡣࡶࡳࡳ࠭ಡ"): reason
            }
            bstack1ll1l1l1l_opy_ = bstack111lll1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࢁࠬಢ").format(json.dumps(bstack1lllll11l_opy_))
            driver.execute_script(bstack1ll1l1l1l_opy_)
            bstack1l1l1l1ll_opy_ = bstack111lll1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࢂ࠭ಣ").format(json.dumps(bstack11lll1l1l_opy_))
            driver.execute_script(bstack1l1l1l1ll_opy_)
  elif bstack11l11l111_opy_:
    try:
      data = {}
      bstack1l1ll11l1_opy_ = None
      if test:
        bstack1l1ll11l1_opy_ = str(test.data)
      if not bstack1ll1ll11_opy_ and bstack1l1ll11l1_opy_:
        data[bstack111lll1l_opy_ (u"ࠩࡱࡥࡲ࡫ࠧತ")] = bstack1l1ll11l1_opy_
      if bstack1llll111_opy_:
        if bstack1llll111_opy_.status == bstack111lll1l_opy_ (u"ࠪࡔࡆ࡙ࡓࠨಥ"):
          data[bstack111lll1l_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫದ")] = bstack111lll1l_opy_ (u"ࠬࡶࡡࡴࡵࡨࡨࠬಧ")
        elif bstack1llll111_opy_.status == bstack111lll1l_opy_ (u"࠭ࡆࡂࡋࡏࠫನ"):
          data[bstack111lll1l_opy_ (u"ࠧࡴࡶࡤࡸࡺࡹࠧ಩")] = bstack111lll1l_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨಪ")
          if bstack1llll111_opy_.message:
            data[bstack111lll1l_opy_ (u"ࠩࡵࡩࡦࡹ࡯࡯ࠩಫ")] = str(bstack1llll111_opy_.message)
      user = CONFIG[bstack111lll1l_opy_ (u"ࠪࡹࡸ࡫ࡲࡏࡣࡰࡩࠬಬ")]
      key = CONFIG[bstack111lll1l_opy_ (u"ࠫࡦࡩࡣࡦࡵࡶࡏࡪࡿࠧಭ")]
      url = bstack111lll1l_opy_ (u"ࠬ࡮ࡴࡵࡲࡶ࠾࠴࠵ࡻࡾ࠼ࡾࢁࡅࡧࡰࡪ࠰ࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫࠯ࡥࡲࡱ࠴ࡧࡵࡵࡱࡰࡥࡹ࡫࠯ࡴࡧࡶࡷ࡮ࡵ࡮ࡴ࠱ࡾࢁ࠳ࡰࡳࡰࡰࠪಮ").format(user, key, bstack11l11l111_opy_)
      headers = {
        bstack111lll1l_opy_ (u"࠭ࡃࡰࡰࡷࡩࡳࡺ࠭ࡵࡻࡳࡩࠬಯ"): bstack111lll1l_opy_ (u"ࠧࡢࡲࡳࡰ࡮ࡩࡡࡵ࡫ࡲࡲ࠴ࡰࡳࡰࡰࠪರ"),
      }
      if bool(data):
        requests.put(url, json=data, headers=headers)
    except Exception as e:
      logger.error(bstack1ll1l11_opy_.format(str(e)))
  if bstack1ll11ll1l_opy_:
    bstack111lll11_opy_(bstack1ll11ll1l_opy_)
  if bstack111ll11l_opy_:
    bstack1l11ll1_opy_(bstack111ll11l_opy_)
  bstack1l1lll_opy_(self, test)
def bstack111111l1_opy_(self, parent, test, skip_on_failure=None, rpa=False):
  global bstack11l1l111_opy_
  bstack11l1l111_opy_(self, parent, test, skip_on_failure=skip_on_failure, rpa=rpa)
  global bstack1llll111_opy_
  bstack1llll111_opy_ = self._test
def bstack1l11_opy_():
  global bstack1lll1l111_opy_
  try:
    if os.path.exists(bstack1lll1l111_opy_):
      os.remove(bstack1lll1l111_opy_)
  except Exception as e:
    logger.debug(bstack111lll1l_opy_ (u"ࠨࡇࡵࡶࡴࡸࠠࡪࡰࠣࡨࡪࡲࡥࡵ࡫ࡱ࡫ࠥࡸ࡯ࡣࡱࡷࠤࡷ࡫ࡰࡰࡴࡷࠤ࡫࡯࡬ࡦ࠼ࠣࠫಱ") + str(e))
def bstack1111ll_opy_():
  global bstack1lll1l111_opy_
  bstack1l111lll1_opy_ = {}
  try:
    if not os.path.isfile(bstack1lll1l111_opy_):
      with open(bstack1lll1l111_opy_, bstack111lll1l_opy_ (u"ࠩࡺࠫಲ")):
        pass
      with open(bstack1lll1l111_opy_, bstack111lll1l_opy_ (u"ࠥࡻ࠰ࠨಳ")) as outfile:
        json.dump({}, outfile)
    if os.path.exists(bstack1lll1l111_opy_):
      bstack1l111lll1_opy_ = json.load(open(bstack1lll1l111_opy_, bstack111lll1l_opy_ (u"ࠫࡷࡨࠧ಴")))
  except Exception as e:
    logger.debug(bstack111lll1l_opy_ (u"ࠬࡋࡲࡳࡱࡵࠤ࡮ࡴࠠࡳࡧࡤࡨ࡮ࡴࡧࠡࡴࡲࡦࡴࡺࠠࡳࡧࡳࡳࡷࡺࠠࡧ࡫࡯ࡩ࠿ࠦࠧವ") + str(e))
  finally:
    return bstack1l111lll1_opy_
def bstack1lll11ll_opy_(platform_index, item_index):
  global bstack1lll1l111_opy_
  try:
    bstack1l111lll1_opy_ = bstack1111ll_opy_()
    bstack1l111lll1_opy_[item_index] = platform_index
    with open(bstack1lll1l111_opy_, bstack111lll1l_opy_ (u"ࠨࡷࠬࠤಶ")) as outfile:
      json.dump(bstack1l111lll1_opy_, outfile)
  except Exception as e:
    logger.debug(bstack111lll1l_opy_ (u"ࠧࡆࡴࡵࡳࡷࠦࡩ࡯ࠢࡺࡶ࡮ࡺࡩ࡯ࡩࠣࡸࡴࠦࡲࡰࡤࡲࡸࠥࡸࡥࡱࡱࡵࡸࠥ࡬ࡩ࡭ࡧ࠽ࠤࠬಷ") + str(e))
def bstack1l1111l1l_opy_(bstack1l1l1lll_opy_):
  global CONFIG
  bstack1lll1ll1_opy_ = bstack111lll1l_opy_ (u"ࠨࠩಸ")
  if not bstack111lll1l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬಹ") in CONFIG:
    logger.info(bstack111lll1l_opy_ (u"ࠪࡒࡴࠦࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠢࡳࡥࡸࡹࡥࡥࠢࡸࡲࡦࡨ࡬ࡦࠢࡷࡳࠥ࡭ࡥ࡯ࡧࡵࡥࡹ࡫ࠠࡳࡧࡳࡳࡷࡺࠠࡧࡱࡵࠤࡗࡵࡢࡰࡶࠣࡶࡺࡴࠧ಺"))
  try:
    platform = CONFIG[bstack111lll1l_opy_ (u"ࠫࡵࡲࡡࡵࡨࡲࡶࡲࡹࠧ಻")][bstack1l1l1lll_opy_]
    if bstack111lll1l_opy_ (u"ࠬࡵࡳࠨ಼") in platform:
      bstack1lll1ll1_opy_ += str(platform[bstack111lll1l_opy_ (u"࠭࡯ࡴࠩಽ")]) + bstack111lll1l_opy_ (u"ࠧ࠭ࠢࠪಾ")
    if bstack111lll1l_opy_ (u"ࠨࡱࡶ࡚ࡪࡸࡳࡪࡱࡱࠫಿ") in platform:
      bstack1lll1ll1_opy_ += str(platform[bstack111lll1l_opy_ (u"ࠩࡲࡷ࡛࡫ࡲࡴ࡫ࡲࡲࠬೀ")]) + bstack111lll1l_opy_ (u"ࠪ࠰ࠥ࠭ು")
    if bstack111lll1l_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࡒࡦࡳࡥࠨೂ") in platform:
      bstack1lll1ll1_opy_ += str(platform[bstack111lll1l_opy_ (u"ࠬࡪࡥࡷ࡫ࡦࡩࡓࡧ࡭ࡦࠩೃ")]) + bstack111lll1l_opy_ (u"࠭ࠬࠡࠩೄ")
    if bstack111lll1l_opy_ (u"ࠧࡱ࡮ࡤࡸ࡫ࡵࡲ࡮ࡘࡨࡶࡸ࡯࡯࡯ࠩ೅") in platform:
      bstack1lll1ll1_opy_ += str(platform[bstack111lll1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯࡙ࡩࡷࡹࡩࡰࡰࠪೆ")]) + bstack111lll1l_opy_ (u"ࠩ࠯ࠤࠬೇ")
    if bstack111lll1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡒࡦࡳࡥࠨೈ") in platform:
      bstack1lll1ll1_opy_ += str(platform[bstack111lll1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡓࡧ࡭ࡦࠩ೉")]) + bstack111lll1l_opy_ (u"ࠬ࠲ࠠࠨೊ")
    if bstack111lll1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡖࡦࡴࡶ࡭ࡴࡴࠧೋ") in platform:
      bstack1lll1ll1_opy_ += str(platform[bstack111lll1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡗࡧࡵࡷ࡮ࡵ࡮ࠨೌ")]) + bstack111lll1l_opy_ (u"ࠨ࠮್ࠣࠫ")
  except Exception as e:
    logger.debug(bstack111lll1l_opy_ (u"ࠩࡖࡳࡲ࡫ࠠࡦࡴࡵࡳࡷࠦࡩ࡯ࠢࡪࡩࡳ࡫ࡲࡢࡶ࡬ࡲ࡬ࠦࡰ࡭ࡣࡷࡪࡴࡸ࡭ࠡࡵࡷࡶ࡮ࡴࡧࠡࡨࡲࡶࠥࡸࡥࡱࡱࡵࡸࠥ࡭ࡥ࡯ࡧࡵࡥࡹ࡯࡯࡯ࠩ೎") + str(e))
  finally:
    if bstack1lll1ll1_opy_[len(bstack1lll1ll1_opy_) - 2:] == bstack111lll1l_opy_ (u"ࠪ࠰ࠥ࠭೏"):
      bstack1lll1ll1_opy_ = bstack1lll1ll1_opy_[:-2]
    return bstack1lll1ll1_opy_
def bstack111lll1l1_opy_(path, bstack1lll1ll1_opy_):
  try:
    import xml.etree.ElementTree as ET
    bstack111ll1lll_opy_ = ET.parse(path)
    bstack1l1l111l_opy_ = bstack111ll1lll_opy_.getroot()
    bstack1111llll1_opy_ = None
    for suite in bstack1l1l111l_opy_.iter(bstack111lll1l_opy_ (u"ࠫࡸࡻࡩࡵࡧࠪ೐")):
      if bstack111lll1l_opy_ (u"ࠬࡹ࡯ࡶࡴࡦࡩࠬ೑") in suite.attrib:
        suite.attrib[bstack111lll1l_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ೒")] += bstack111lll1l_opy_ (u"ࠧࠡࠩ೓") + bstack1lll1ll1_opy_
        bstack1111llll1_opy_ = suite
    bstack1lll111_opy_ = None
    for robot in bstack1l1l111l_opy_.iter(bstack111lll1l_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧ೔")):
      bstack1lll111_opy_ = robot
    bstack11ll111_opy_ = len(bstack1lll111_opy_.findall(bstack111lll1l_opy_ (u"ࠩࡶࡹ࡮ࡺࡥࠨೕ")))
    if bstack11ll111_opy_ == 1:
      bstack1lll111_opy_.remove(bstack1lll111_opy_.findall(bstack111lll1l_opy_ (u"ࠪࡷࡺ࡯ࡴࡦࠩೖ"))[0])
      bstack1ll11_opy_ = ET.Element(bstack111lll1l_opy_ (u"ࠫࡸࡻࡩࡵࡧࠪ೗"), attrib={bstack111lll1l_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ೘"):bstack111lll1l_opy_ (u"࠭ࡓࡶ࡫ࡷࡩࡸ࠭೙"), bstack111lll1l_opy_ (u"ࠧࡪࡦࠪ೚"):bstack111lll1l_opy_ (u"ࠨࡵ࠳ࠫ೛")})
      bstack1lll111_opy_.insert(1, bstack1ll11_opy_)
      bstack111llll1l_opy_ = None
      for suite in bstack1lll111_opy_.iter(bstack111lll1l_opy_ (u"ࠩࡶࡹ࡮ࡺࡥࠨ೜")):
        bstack111llll1l_opy_ = suite
      bstack111llll1l_opy_.append(bstack1111llll1_opy_)
      bstack1ll1ll11l_opy_ = None
      for status in bstack1111llll1_opy_.iter(bstack111lll1l_opy_ (u"ࠪࡷࡹࡧࡴࡶࡵࠪೝ")):
        bstack1ll1ll11l_opy_ = status
      bstack111llll1l_opy_.append(bstack1ll1ll11l_opy_)
    bstack111ll1lll_opy_.write(path)
  except Exception as e:
    logger.debug(bstack111lll1l_opy_ (u"ࠫࡊࡸࡲࡰࡴࠣ࡭ࡳࠦࡰࡢࡴࡶ࡭ࡳ࡭ࠠࡸࡪ࡬ࡰࡪࠦࡧࡦࡰࡨࡶࡦࡺࡩ࡯ࡩࠣࡶࡴࡨ࡯ࡵࠢࡵࡩࡵࡵࡲࡵࠩೞ") + str(e))
def bstack11lll_opy_(outs_dir, pabot_args, options, start_time_string, tests_root_name):
  global bstack111l11l_opy_
  global CONFIG
  if bstack111lll1l_opy_ (u"ࠧࡶࡹࡵࡪࡲࡲࡵࡧࡴࡩࠤ೟") in options:
    del options[bstack111lll1l_opy_ (u"ࠨࡰࡺࡶ࡫ࡳࡳࡶࡡࡵࡪࠥೠ")]
  bstack1ll1l11ll_opy_ = bstack1111ll_opy_()
  for bstack1l1l_opy_ in bstack1ll1l11ll_opy_.keys():
    path = os.path.join(os.getcwd(), bstack111lll1l_opy_ (u"ࠧࡱࡣࡥࡳࡹࡥࡲࡦࡵࡸࡰࡹࡹࠧೡ"), str(bstack1l1l_opy_), bstack111lll1l_opy_ (u"ࠨࡱࡸࡸࡵࡻࡴ࠯ࡺࡰࡰࠬೢ"))
    bstack111lll1l1_opy_(path, bstack1l1111l1l_opy_(bstack1ll1l11ll_opy_[bstack1l1l_opy_]))
  bstack1l11_opy_()
  return bstack111l11l_opy_(outs_dir, pabot_args, options, start_time_string, tests_root_name)
def bstack11ll1lll_opy_(self, ff_profile_dir):
  global bstack1l11lllll_opy_
  if not ff_profile_dir:
    return None
  return bstack1l11lllll_opy_(self, ff_profile_dir)
def bstack111ll11_opy_(datasources, opts_for_run, outs_dir, pabot_args, suite_group):
  from pabot.pabot import QueueItem
  global CONFIG
  global bstack111l1ll1_opy_
  bstack11l1ll11_opy_ = []
  if bstack111lll1l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬೣ") in CONFIG:
    bstack11l1ll11_opy_ = CONFIG[bstack111lll1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭೤")]
  return [
    QueueItem(
      datasources,
      outs_dir,
      opts_for_run,
      suite,
      pabot_args[bstack111lll1l_opy_ (u"ࠦࡨࡵ࡭࡮ࡣࡱࡨࠧ೥")],
      pabot_args[bstack111lll1l_opy_ (u"ࠧࡼࡥࡳࡤࡲࡷࡪࠨ೦")],
      argfile,
      pabot_args.get(bstack111lll1l_opy_ (u"ࠨࡨࡪࡸࡨࠦ೧")),
      pabot_args[bstack111lll1l_opy_ (u"ࠢࡱࡴࡲࡧࡪࡹࡳࡦࡵࠥ೨")],
      platform[0],
      bstack111l1ll1_opy_
    )
    for suite in suite_group
    for argfile in pabot_args[bstack111lll1l_opy_ (u"ࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡩ࡭ࡱ࡫ࡳࠣ೩")] or [(bstack111lll1l_opy_ (u"ࠤࠥ೪"), None)]
    for platform in enumerate(bstack11l1ll11_opy_)
  ]
def bstack1ll_opy_(self, datasources, outs_dir, options,
  execution_item, command, verbose, argfile,
  hive=None, processes=0,platform_index=0,bstack1ll1llll1_opy_=bstack111lll1l_opy_ (u"ࠪࠫ೫")):
  global bstack111lll11l_opy_
  self.platform_index = platform_index
  self.bstack11llll11l_opy_ = bstack1ll1llll1_opy_
  bstack111lll11l_opy_(self, datasources, outs_dir, options,
    execution_item, command, verbose, argfile, hive, processes)
def bstack11l1l1l11_opy_(caller_id, datasources, is_last, item, outs_dir):
  global bstack111111ll_opy_
  global bstack1ll11l111_opy_
  if not bstack111lll1l_opy_ (u"ࠫࡻࡧࡲࡪࡣࡥࡰࡪ࠭೬") in item.options:
    item.options[bstack111lll1l_opy_ (u"ࠬࡼࡡࡳ࡫ࡤࡦࡱ࡫ࠧ೭")] = []
  for v in item.options[bstack111lll1l_opy_ (u"࠭ࡶࡢࡴ࡬ࡥࡧࡲࡥࠨ೮")]:
    if bstack111lll1l_opy_ (u"ࠧࡃࡕࡗࡅࡈࡑࡐࡍࡃࡗࡊࡔࡘࡍࡊࡐࡇࡉ࡝࠭೯") in v:
      item.options[bstack111lll1l_opy_ (u"ࠨࡸࡤࡶ࡮ࡧࡢ࡭ࡧࠪ೰")].remove(v)
    if bstack111lll1l_opy_ (u"ࠩࡅࡗ࡙ࡇࡃࡌࡅࡏࡍࡆࡘࡇࡔࠩೱ") in v:
      item.options[bstack111lll1l_opy_ (u"ࠪࡺࡦࡸࡩࡢࡤ࡯ࡩࠬೲ")].remove(v)
  item.options[bstack111lll1l_opy_ (u"ࠫࡻࡧࡲࡪࡣࡥࡰࡪ࠭ೳ")].insert(0, bstack111lll1l_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡕࡒࡁࡕࡈࡒࡖࡒࡏࡎࡅࡇ࡛࠾ࢀࢃࠧ೴").format(item.platform_index))
  item.options[bstack111lll1l_opy_ (u"࠭ࡶࡢࡴ࡬ࡥࡧࡲࡥࠨ೵")].insert(0, bstack111lll1l_opy_ (u"ࠧࡃࡕࡗࡅࡈࡑࡄࡆࡈࡏࡓࡈࡇࡌࡊࡆࡈࡒ࡙ࡏࡆࡊࡇࡕ࠾ࢀࢃࠧ೶").format(item.bstack11llll11l_opy_))
  if bstack1ll11l111_opy_:
    item.options[bstack111lll1l_opy_ (u"ࠨࡸࡤࡶ࡮ࡧࡢ࡭ࡧࠪ೷")].insert(0, bstack111lll1l_opy_ (u"ࠩࡅࡗ࡙ࡇࡃࡌࡅࡏࡍࡆࡘࡇࡔ࠼ࡾࢁࠬ೸").format(bstack1ll11l111_opy_))
  return bstack111111ll_opy_(caller_id, datasources, is_last, item, outs_dir)
def bstack11lllllll_opy_(command, item_index):
  global bstack1ll11l111_opy_
  if bstack1ll11l111_opy_:
    command[0] = command[0].replace(bstack111lll1l_opy_ (u"ࠪࡶࡴࡨ࡯ࡵࠩ೹"), bstack111lll1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭࠰ࡷࡩࡱࠠࡳࡱࡥࡳࡹ࠳ࡩ࡯ࡶࡨࡶࡳࡧ࡬ࠡ࠯࠰ࡦࡸࡺࡡࡤ࡭ࡢ࡭ࡹ࡫࡭ࡠ࡫ࡱࡨࡪࡾࠠࠨ೺") + str(item_index) + bstack111lll1l_opy_ (u"ࠬࠦࠧ೻") + bstack1ll11l111_opy_, 1)
  else:
    command[0] = command[0].replace(bstack111lll1l_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬ೼"), bstack111lll1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠳ࡳࡥ࡭ࠣࡶࡴࡨ࡯ࡵ࠯࡬ࡲࡹ࡫ࡲ࡯ࡣ࡯ࠤ࠲࠳ࡢࡴࡶࡤࡧࡰࡥࡩࡵࡧࡰࡣ࡮ࡴࡤࡦࡺࠣࠫ೽") + str(item_index), 1)
def bstack1ll1111l1_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index):
  global bstack1l1llllll_opy_
  bstack11lllllll_opy_(command, item_index)
  return bstack1l1llllll_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index)
def bstack111lll_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir):
  global bstack1l1llllll_opy_
  bstack11lllllll_opy_(command, item_index)
  return bstack1l1llllll_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir)
def bstack11l1l1l1l_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout):
  global bstack1l1llllll_opy_
  bstack11lllllll_opy_(command, item_index)
  return bstack1l1llllll_opy_(command, stderr, stdout, item_name, verbose, pool_id, item_index, outs_dir, process_timeout)
def bstack11l111lll_opy_(self, runner, quiet=False, capture=True):
  global bstack1l111llll_opy_
  bstack11l11ll11_opy_ = bstack1l111llll_opy_(self, runner, quiet=False, capture=True)
  if self.exception:
    if not hasattr(runner, bstack111lll1l_opy_ (u"ࠨࡧࡻࡧࡪࡶࡴࡪࡱࡱࡣࡦࡸࡲࠨ೾")):
      runner.exception_arr = []
    if not hasattr(runner, bstack111lll1l_opy_ (u"ࠩࡨࡼࡨࡥࡴࡳࡣࡦࡩࡧࡧࡣ࡬ࡡࡤࡶࡷ࠭೿")):
      runner.exc_traceback_arr = []
    runner.exception = self.exception
    runner.exc_traceback = self.exc_traceback
    runner.exception_arr.append(self.exception)
    runner.exc_traceback_arr.append(self.exc_traceback)
  return bstack11l11ll11_opy_
def bstack1l1ll1ll1_opy_(self, name, context, *args):
  global bstack11l1l11l1_opy_
  if name == bstack111lll1l_opy_ (u"ࠪࡦࡪ࡬࡯ࡳࡧࡢࡪࡪࡧࡴࡶࡴࡨࠫഀ"):
    bstack11l1l11l1_opy_(self, name, context, *args)
    try:
      if(not bstack1ll1ll11_opy_):
        bstack1l1l1ll1l_opy_ = threading.current_thread().bstackSessionDriver if bstack1l11l1ll1_opy_(bstack111lll1l_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡗࡪࡹࡳࡪࡱࡱࡈࡷ࡯ࡶࡦࡴࠪഁ")) else context.browser
        bstack1llll11ll_opy_ = str(self.feature.name)
        bstack1lllll11_opy_(context, bstack1llll11ll_opy_)
        bstack1l1l1ll1l_opy_.execute_script(bstack111lll1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡱࡥࡲ࡫ࠢ࠻ࠢࠪം") + json.dumps(bstack1llll11ll_opy_) + bstack111lll1l_opy_ (u"࠭ࡽࡾࠩഃ"))
      self.driver_before_scenario = False
    except Exception as e:
      logger.debug(bstack111lll1l_opy_ (u"ࠧࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡪࡺࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡰࡤࡱࡪࠦࡩ࡯ࠢࡥࡩ࡫ࡵࡲࡦࠢࡩࡩࡦࡺࡵࡳࡧ࠽ࠤࢀࢃࠧഄ").format(str(e)))
  elif name == bstack111lll1l_opy_ (u"ࠨࡤࡨࡪࡴࡸࡥࡠࡵࡦࡩࡳࡧࡲࡪࡱࠪഅ"):
    bstack11l1l11l1_opy_(self, name, context, *args)
    try:
      if not hasattr(self, bstack111lll1l_opy_ (u"ࠩࡧࡶ࡮ࡼࡥࡳࡡࡥࡩ࡫ࡵࡲࡦࡡࡶࡧࡪࡴࡡࡳ࡫ࡲࠫആ")):
        self.driver_before_scenario = True
      if(not bstack1ll1ll11_opy_):
        scenario_name = args[0].name
        feature_name = bstack1llll11ll_opy_ = str(self.feature.name)
        bstack1llll11ll_opy_ = feature_name + bstack111lll1l_opy_ (u"ࠪࠤ࠲ࠦࠧഇ") + scenario_name
        bstack1l1l1ll1l_opy_ = threading.current_thread().bstackSessionDriver if bstack1l11l1ll1_opy_(bstack111lll1l_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡗࡪࡹࡳࡪࡱࡱࡈࡷ࡯ࡶࡦࡴࠪഈ")) else context.browser
        if self.driver_before_scenario:
          bstack1lllll11_opy_(context, bstack1llll11ll_opy_)
          bstack1l1l1ll1l_opy_.execute_script(bstack111lll1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡐࡤࡱࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡱࡥࡲ࡫ࠢ࠻ࠢࠪഉ") + json.dumps(bstack1llll11ll_opy_) + bstack111lll1l_opy_ (u"࠭ࡽࡾࠩഊ"))
    except Exception as e:
      logger.debug(bstack111lll1l_opy_ (u"ࠧࡇࡣ࡬ࡰࡪࡪࠠࡵࡱࠣࡷࡪࡺࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡰࡤࡱࡪࠦࡩ࡯ࠢࡥࡩ࡫ࡵࡲࡦࠢࡶࡧࡪࡴࡡࡳ࡫ࡲ࠾ࠥࢁࡽࠨഋ").format(str(e)))
  elif name == bstack111lll1l_opy_ (u"ࠨࡣࡩࡸࡪࡸ࡟ࡴࡥࡨࡲࡦࡸࡩࡰࠩഌ"):
    try:
      bstack1lllll_opy_ = args[0].status.name
      bstack1l1l1ll1l_opy_ = threading.current_thread().bstackSessionDriver if bstack111lll1l_opy_ (u"ࠩࡥࡷࡹࡧࡣ࡬ࡕࡨࡷࡸ࡯࡯࡯ࡆࡵ࡭ࡻ࡫ࡲࠨ഍") in threading.current_thread().__dict__.keys() else context.browser
      if str(bstack1lllll_opy_).lower() == bstack111lll1l_opy_ (u"ࠪࡪࡦ࡯࡬ࡦࡦࠪഎ"):
        bstack1llll1ll_opy_ = bstack111lll1l_opy_ (u"ࠫࠬഏ")
        bstack11ll111ll_opy_ = bstack111lll1l_opy_ (u"ࠬ࠭ഐ")
        bstack11l1_opy_ = bstack111lll1l_opy_ (u"࠭ࠧ഑")
        try:
          import traceback
          bstack1llll1ll_opy_ = self.exception.__class__.__name__
          bstack1l11l1111_opy_ = traceback.format_tb(self.exc_traceback)
          bstack11ll111ll_opy_ = bstack111lll1l_opy_ (u"ࠧࠡࠩഒ").join(bstack1l11l1111_opy_)
          bstack11l1_opy_ = bstack1l11l1111_opy_[-1]
        except Exception as e:
          logger.debug(bstack1lll1l1_opy_.format(str(e)))
        bstack1llll1ll_opy_ += bstack11l1_opy_
        bstack11111ll_opy_(context, json.dumps(str(args[0].name) + bstack111lll1l_opy_ (u"ࠣࠢ࠰ࠤࡋࡧࡩ࡭ࡧࡧࠥࡡࡴࠢഓ") + str(bstack11ll111ll_opy_)), bstack111lll1l_opy_ (u"ࠤࡨࡶࡷࡵࡲࠣഔ"))
        if self.driver_before_scenario:
          bstack11lll111_opy_(context, bstack111lll1l_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠥക"), bstack1llll1ll_opy_)
          bstack1l1l1ll1l_opy_.execute_script(bstack111lll1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࡢࡩࡽ࡫ࡣࡶࡶࡲࡶ࠿ࠦࡻࠣࡣࡦࡸ࡮ࡵ࡮ࠣ࠼ࠣࠦࡦࡴ࡮ࡰࡶࡤࡸࡪࠨࠬࠡࠤࡤࡶ࡬ࡻ࡭ࡦࡰࡷࡷࠧࡀࠠࡼࠤࡧࡥࡹࡧࠢ࠻ࠩഖ") + json.dumps(str(args[0].name) + bstack111lll1l_opy_ (u"ࠧࠦ࠭ࠡࡈࡤ࡭ࡱ࡫ࡤࠢ࡞ࡱࠦഗ") + str(bstack11ll111ll_opy_)) + bstack111lll1l_opy_ (u"࠭ࠬࠡࠤ࡯ࡩࡻ࡫࡬ࠣ࠼ࠣࠦࡪࡸࡲࡰࡴࠥࢁࢂ࠭ഘ"))
        if self.driver_before_scenario:
          bstack1l1l1ll1l_opy_.execute_script(bstack111lll1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡴࡧࡷࡗࡪࡹࡳࡪࡱࡱࡗࡹࡧࡴࡶࡵࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨࡳࡵࡣࡷࡹࡸࠨ࠺ࠣࡨࡤ࡭ࡱ࡫ࡤࠣ࠮ࠣࠦࡷ࡫ࡡࡴࡱࡱࠦ࠿ࠦࠧങ") + json.dumps(bstack111lll1l_opy_ (u"ࠣࡕࡦࡩࡳࡧࡲࡪࡱࠣࡪࡦ࡯࡬ࡦࡦࠣࡻ࡮ࡺࡨ࠻ࠢ࡟ࡲࠧച") + str(bstack1llll1ll_opy_)) + bstack111lll1l_opy_ (u"ࠩࢀࢁࠬഛ"))
      else:
        bstack11111ll_opy_(context, bstack111lll1l_opy_ (u"ࠥࡔࡦࡹࡳࡦࡦࠤࠦജ"), bstack111lll1l_opy_ (u"ࠦ࡮ࡴࡦࡰࠤഝ"))
        if self.driver_before_scenario:
          bstack11lll111_opy_(context, bstack111lll1l_opy_ (u"ࠧࡶࡡࡴࡵࡨࡨࠧഞ"))
        bstack1l1l1ll1l_opy_.execute_script(bstack111lll1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡡ࡯ࡰࡲࡸࡦࡺࡥࠣ࠮ࠣࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢ࠻ࠢࡾࠦࡩࡧࡴࡢࠤ࠽ࠫട") + json.dumps(str(args[0].name) + bstack111lll1l_opy_ (u"ࠢࠡ࠯ࠣࡔࡦࡹࡳࡦࡦࠤࠦഠ")) + bstack111lll1l_opy_ (u"ࠨ࠮ࠣࠦࡱ࡫ࡶࡦ࡮ࠥ࠾ࠥࠨࡩ࡯ࡨࡲࠦࢂࢃࠧഡ"))
        if self.driver_before_scenario:
          bstack1l1l1ll1l_opy_.execute_script(bstack111lll1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡧࡻࡩࡨࡻࡴࡰࡴ࠽ࠤࢀࠨࡡࡤࡶ࡬ࡳࡳࠨ࠺ࠡࠤࡶࡩࡹ࡙ࡥࡴࡵ࡬ࡳࡳ࡙ࡴࡢࡶࡸࡷࠧ࠲ࠠࠣࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠦ࠿ࠦࡻࠣࡵࡷࡥࡹࡻࡳࠣ࠼ࠥࡴࡦࡹࡳࡦࡦࠥࢁࢂ࠭ഢ"))
    except Exception as e:
      logger.debug(bstack111lll1l_opy_ (u"ࠪࡊࡦ࡯࡬ࡦࡦࠣࡸࡴࠦ࡭ࡢࡴ࡮ࠤࡸ࡫ࡳࡴ࡫ࡲࡲࠥࡹࡴࡢࡶࡸࡷࠥ࡯࡮ࠡࡣࡩࡸࡪࡸࠠࡧࡧࡤࡸࡺࡸࡥ࠻ࠢࡾࢁࠬണ").format(str(e)))
  elif name == bstack111lll1l_opy_ (u"ࠫࡦ࡬ࡴࡦࡴࡢࡪࡪࡧࡴࡶࡴࡨࠫത"):
    try:
      bstack1l1l1ll1l_opy_ = threading.current_thread().bstackSessionDriver if bstack1l11l1ll1_opy_(bstack111lll1l_opy_ (u"ࠬࡨࡳࡵࡣࡦ࡯ࡘ࡫ࡳࡴ࡫ࡲࡲࡉࡸࡩࡷࡧࡵࠫഥ")) else context.browser
      if context.failed is True:
        bstack1l1l11lll_opy_ = []
        bstack11llll1l1_opy_ = []
        bstack111l11ll_opy_ = []
        bstack11ll1l1l1_opy_ = bstack111lll1l_opy_ (u"࠭ࠧദ")
        try:
          import traceback
          for exc in self.exception_arr:
            bstack1l1l11lll_opy_.append(exc.__class__.__name__)
          for exc_tb in self.exc_traceback_arr:
            bstack1l11l1111_opy_ = traceback.format_tb(exc_tb)
            bstack11l111_opy_ = bstack111lll1l_opy_ (u"ࠧࠡࠩധ").join(bstack1l11l1111_opy_)
            bstack11llll1l1_opy_.append(bstack11l111_opy_)
            bstack111l11ll_opy_.append(bstack1l11l1111_opy_[-1])
        except Exception as e:
          logger.debug(bstack1lll1l1_opy_.format(str(e)))
        bstack1llll1ll_opy_ = bstack111lll1l_opy_ (u"ࠨࠩന")
        for i in range(len(bstack1l1l11lll_opy_)):
          bstack1llll1ll_opy_ += bstack1l1l11lll_opy_[i] + bstack111l11ll_opy_[i] + bstack111lll1l_opy_ (u"ࠩ࡟ࡲࠬഩ")
        bstack11ll1l1l1_opy_ = bstack111lll1l_opy_ (u"ࠪࠤࠬപ").join(bstack11llll1l1_opy_)
        if not self.driver_before_scenario:
          bstack11111ll_opy_(context, bstack11ll1l1l1_opy_, bstack111lll1l_opy_ (u"ࠦࡪࡸࡲࡰࡴࠥഫ"))
          bstack11lll111_opy_(context, bstack111lll1l_opy_ (u"ࠧ࡬ࡡࡪ࡮ࡨࡨࠧബ"), bstack1llll1ll_opy_)
          bstack1l1l1ll1l_opy_.execute_script(bstack111lll1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡤ࡫ࡸࡦࡥࡸࡸࡴࡸ࠺ࠡࡽࠥࡥࡨࡺࡩࡰࡰࠥ࠾ࠥࠨࡡ࡯ࡰࡲࡸࡦࡺࡥࠣ࠮ࠣࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢ࠻ࠢࡾࠦࡩࡧࡴࡢࠤ࠽ࠫഭ") + json.dumps(bstack11ll1l1l1_opy_) + bstack111lll1l_opy_ (u"ࠧ࠭ࠢࠥࡰࡪࡼࡥ࡭ࠤ࠽ࠤࠧ࡫ࡲࡳࡱࡵࠦࢂࢃࠧമ"))
          bstack1l1l1ll1l_opy_.execute_script(bstack111lll1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡘࡺࡡࡵࡷࡶࠦ࠱ࠦࠢࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠥ࠾ࠥࢁࠢࡴࡶࡤࡸࡺࡹࠢ࠻ࠤࡩࡥ࡮ࡲࡥࡥࠤ࠯ࠤࠧࡸࡥࡢࡵࡲࡲࠧࡀࠠࠨയ") + json.dumps(bstack111lll1l_opy_ (u"ࠤࡖࡳࡲ࡫ࠠࡴࡥࡨࡲࡦࡸࡩࡰࡵࠣࡪࡦ࡯࡬ࡦࡦ࠽ࠤࡡࡴࠢര") + str(bstack1llll1ll_opy_)) + bstack111lll1l_opy_ (u"ࠪࢁࢂ࠭റ"))
      else:
        if not self.driver_before_scenario:
          bstack11111ll_opy_(context, bstack111lll1l_opy_ (u"ࠦࡋ࡫ࡡࡵࡷࡵࡩ࠿ࠦࠢല") + str(self.feature.name) + bstack111lll1l_opy_ (u"ࠧࠦࡰࡢࡵࡶࡩࡩࠧࠢള"), bstack111lll1l_opy_ (u"ࠨࡩ࡯ࡨࡲࠦഴ"))
          bstack11lll111_opy_(context, bstack111lll1l_opy_ (u"ࠢࡱࡣࡶࡷࡪࡪࠢവ"))
          bstack1l1l1ll1l_opy_.execute_script(bstack111lll1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࡟ࡦࡺࡨࡧࡺࡺ࡯ࡳ࠼ࠣࡿࠧࡧࡣࡵ࡫ࡲࡲࠧࡀࠠࠣࡣࡱࡲࡴࡺࡡࡵࡧࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨࡤࡢࡶࡤࠦ࠿࠭ശ") + json.dumps(bstack111lll1l_opy_ (u"ࠤࡉࡩࡦࡺࡵࡳࡧ࠽ࠤࠧഷ") + str(self.feature.name) + bstack111lll1l_opy_ (u"ࠥࠤࡵࡧࡳࡴࡧࡧࠥࠧസ")) + bstack111lll1l_opy_ (u"ࠫ࠱ࠦࠢ࡭ࡧࡹࡩࡱࠨ࠺ࠡࠤ࡬ࡲ࡫ࡵࠢࡾࡿࠪഹ"))
          bstack1l1l1ll1l_opy_.execute_script(bstack111lll1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡕࡷࡥࡹࡻࡳࠣ࠮ࠣࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢ࠻ࠢࡾࠦࡸࡺࡡࡵࡷࡶࠦ࠿ࠨࡰࡢࡵࡶࡩࡩࠨࡽࡾࠩഺ"))
    except Exception as e:
      logger.debug(bstack111lll1l_opy_ (u"࠭ࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡰࡥࡷࡱࠠࡴࡧࡶࡷ࡮ࡵ࡮ࠡࡵࡷࡥࡹࡻࡳࠡ࡫ࡱࠤࡦ࡬ࡴࡦࡴࠣࡪࡪࡧࡴࡶࡴࡨ࠾ࠥࢁࡽࠨ഻").format(str(e)))
  else:
    bstack11l1l11l1_opy_(self, name, context, *args)
  if name in [bstack111lll1l_opy_ (u"ࠧࡢࡨࡷࡩࡷࡥࡦࡦࡣࡷࡹࡷ࡫഼ࠧ"), bstack111lll1l_opy_ (u"ࠨࡣࡩࡸࡪࡸ࡟ࡴࡥࡨࡲࡦࡸࡩࡰࠩഽ")]:
    bstack11l1l11l1_opy_(self, name, context, *args)
    if (name == bstack111lll1l_opy_ (u"ࠩࡤࡪࡹ࡫ࡲࡠࡵࡦࡩࡳࡧࡲࡪࡱࠪാ") and self.driver_before_scenario) or (name == bstack111lll1l_opy_ (u"ࠪࡥ࡫ࡺࡥࡳࡡࡩࡩࡦࡺࡵࡳࡧࠪി") and not self.driver_before_scenario):
      try:
        bstack1l1l1ll1l_opy_ = threading.current_thread().bstackSessionDriver if bstack1l11l1ll1_opy_(bstack111lll1l_opy_ (u"ࠫࡧࡹࡴࡢࡥ࡮ࡗࡪࡹࡳࡪࡱࡱࡈࡷ࡯ࡶࡦࡴࠪീ")) else context.browser
        bstack1l1l1ll1l_opy_.quit()
      except Exception:
        pass
def bstack11lll11l1_opy_(config, startdir):
  return bstack111lll1l_opy_ (u"ࠧࡪࡲࡪࡸࡨࡶ࠿ࠦࡻ࠱ࡿࠥു").format(bstack111lll1l_opy_ (u"ࠨࡂࡳࡱࡺࡷࡪࡸࡓࡵࡣࡦ࡯ࠧൂ"))
class Notset:
  def __repr__(self):
    return bstack111lll1l_opy_ (u"ࠢ࠽ࡐࡒࡘࡘࡋࡔ࠿ࠤൃ")
notset = Notset()
def bstack1l1ll11ll_opy_(self, name: str, default=notset, skip: bool = False):
  global bstack1l1lll111_opy_
  if str(name).lower() == bstack111lll1l_opy_ (u"ࠨࡦࡵ࡭ࡻ࡫ࡲࠨൄ"):
    return bstack111lll1l_opy_ (u"ࠤࡅࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࠣ൅")
  else:
    return bstack1l1lll111_opy_(self, name, default, skip)
def bstack11l11lll_opy_(item, when):
  global bstack1l1ll1lll_opy_
  try:
    bstack1l1ll1lll_opy_(item, when)
  except Exception as e:
    pass
def bstack11111l_opy_():
  return
def bstack1l1111lll_opy_(type, name, status, reason, bstack1lllll1l_opy_, bstack1ll1l1111_opy_):
  bstack11lll1l1l_opy_ = {
    bstack111lll1l_opy_ (u"ࠪࡥࡨࡺࡩࡰࡰࠪെ"): type,
    bstack111lll1l_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧേ"): {}
  }
  if type == bstack111lll1l_opy_ (u"ࠬࡧ࡮࡯ࡱࡷࡥࡹ࡫ࠧൈ"):
    bstack11lll1l1l_opy_[bstack111lll1l_opy_ (u"࠭ࡡࡳࡩࡸࡱࡪࡴࡴࡴࠩ൉")][bstack111lll1l_opy_ (u"ࠧ࡭ࡧࡹࡩࡱ࠭ൊ")] = bstack1lllll1l_opy_
    bstack11lll1l1l_opy_[bstack111lll1l_opy_ (u"ࠨࡣࡵ࡫ࡺࡳࡥ࡯ࡶࡶࠫോ")][bstack111lll1l_opy_ (u"ࠩࡧࡥࡹࡧࠧൌ")] = json.dumps(str(bstack1ll1l1111_opy_))
  if type == bstack111lll1l_opy_ (u"ࠪࡷࡪࡺࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨ്ࠫ"):
    bstack11lll1l1l_opy_[bstack111lll1l_opy_ (u"ࠫࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠧൎ")][bstack111lll1l_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ൏")] = name
  if type == bstack111lll1l_opy_ (u"࠭ࡳࡦࡶࡖࡩࡸࡹࡩࡰࡰࡖࡸࡦࡺࡵࡴࠩ൐"):
    bstack11lll1l1l_opy_[bstack111lll1l_opy_ (u"ࠧࡢࡴࡪࡹࡲ࡫࡮ࡵࡵࠪ൑")][bstack111lll1l_opy_ (u"ࠨࡵࡷࡥࡹࡻࡳࠨ൒")] = status
    if status == bstack111lll1l_opy_ (u"ࠩࡩࡥ࡮ࡲࡥࡥࠩ൓"):
      bstack11lll1l1l_opy_[bstack111lll1l_opy_ (u"ࠪࡥࡷ࡭ࡵ࡮ࡧࡱࡸࡸ࠭ൔ")][bstack111lll1l_opy_ (u"ࠫࡷ࡫ࡡࡴࡱࡱࠫൕ")] = json.dumps(str(reason))
  bstack1l1l1l1ll_opy_ = bstack111lll1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࡿࠪൖ").format(json.dumps(bstack11lll1l1l_opy_))
  return bstack1l1l1l1ll_opy_
def bstack11l111ll_opy_(item, call, rep):
  global bstack1l1l11_opy_
  global bstack1lll_opy_
  name = bstack111lll1l_opy_ (u"࠭ࠧൗ")
  try:
    if rep.when == bstack111lll1l_opy_ (u"ࠧࡤࡣ࡯ࡰࠬ൘"):
      bstack11l11l111_opy_ = threading.current_thread().bstack1l1l11ll1_opy_
      try:
        name = str(rep.nodeid)
        bstack1l1l1111l_opy_ = bstack1l1111lll_opy_(bstack111lll1l_opy_ (u"ࠨࡵࡨࡸࡘ࡫ࡳࡴ࡫ࡲࡲࡓࡧ࡭ࡦࠩ൙"), name, bstack111lll1l_opy_ (u"ࠩࠪ൚"), bstack111lll1l_opy_ (u"ࠪࠫ൛"), bstack111lll1l_opy_ (u"ࠫࠬ൜"), bstack111lll1l_opy_ (u"ࠬ࠭൝"))
        for driver in bstack1lll_opy_:
          if bstack11l11l111_opy_ == driver.session_id:
            driver.execute_script(bstack1l1l1111l_opy_)
      except Exception as e:
        logger.debug(bstack111lll1l_opy_ (u"࠭ࡅࡳࡴࡲࡶࠥ࡯࡮ࠡࡵࡨࡸࡹ࡯࡮ࡨࠢࡶࡩࡸࡹࡩࡰࡰࡑࡥࡲ࡫ࠠࡧࡱࡵࠤࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠡࡵࡨࡷࡸ࡯࡯࡯࠼ࠣࡿࢂ࠭൞").format(str(e)))
      try:
        status = bstack111lll1l_opy_ (u"ࠧࡧࡣ࡬ࡰࡪࡪࠧൟ") if rep.outcome.lower() == bstack111lll1l_opy_ (u"ࠨࡨࡤ࡭ࡱ࡫ࡤࠨൠ") else bstack111lll1l_opy_ (u"ࠩࡳࡥࡸࡹࡥࡥࠩൡ")
        reason = bstack111lll1l_opy_ (u"ࠪࠫൢ")
        if (reason != bstack111lll1l_opy_ (u"ࠦࠧൣ")):
          try:
            if (threading.current_thread().bstackTestErrorMessages == None):
                threading.current_thread().bstackTestErrorMessages = []
          except Exception as e:
            threading.current_thread().bstackTestErrorMessages = []
          threading.current_thread().bstackTestErrorMessages.append(str(reason))
        if status == bstack111lll1l_opy_ (u"ࠬ࡬ࡡࡪ࡮ࡨࡨࠬ൤"):
          reason = rep.longrepr.reprcrash.message
          if (not threading.current_thread().bstackTestErrorMessages):
            threading.current_thread().bstackTestErrorMessages = []
          threading.current_thread().bstackTestErrorMessages.append(reason)
        level = bstack111lll1l_opy_ (u"࠭ࡩ࡯ࡨࡲࠫ൥") if status == bstack111lll1l_opy_ (u"ࠧࡱࡣࡶࡷࡪࡪࠧ൦") else bstack111lll1l_opy_ (u"ࠨࡧࡵࡶࡴࡸࠧ൧")
        data = name + bstack111lll1l_opy_ (u"ࠩࠣࡴࡦࡹࡳࡦࡦࠤࠫ൨") if status == bstack111lll1l_opy_ (u"ࠪࡴࡦࡹࡳࡦࡦࠪ൩") else name + bstack111lll1l_opy_ (u"ࠫࠥ࡬ࡡࡪ࡮ࡨࡨࠦࠦࠧ൪") + reason
        bstack11ll11ll_opy_ = bstack1l1111lll_opy_(bstack111lll1l_opy_ (u"ࠬࡧ࡮࡯ࡱࡷࡥࡹ࡫ࠧ൫"), bstack111lll1l_opy_ (u"࠭ࠧ൬"), bstack111lll1l_opy_ (u"ࠧࠨ൭"), bstack111lll1l_opy_ (u"ࠨࠩ൮"), level, data)
        for driver in bstack1lll_opy_:
          if bstack11l11l111_opy_ == driver.session_id:
            driver.execute_script(bstack11ll11ll_opy_)
      except Exception as e:
        logger.debug(bstack111lll1l_opy_ (u"ࠩࡈࡶࡷࡵࡲࠡ࡫ࡱࠤࡸ࡫ࡴࡵ࡫ࡱ࡫ࠥࡹࡥࡴࡵ࡬ࡳࡳࠦࡣࡰࡰࡷࡩࡽࡺࠠࡧࡱࡵࠤࡵࡿࡴࡦࡵࡷ࠱ࡧࡪࡤࠡࡵࡨࡷࡸ࡯࡯࡯࠼ࠣࡿࢂ࠭൯").format(str(e)))
  except Exception as e:
    logger.debug(bstack111lll1l_opy_ (u"ࠪࡉࡷࡸ࡯ࡳࠢ࡬ࡲࠥ࡭ࡥࡵࡶ࡬ࡲ࡬ࠦࡳࡵࡣࡷࡩࠥ࡯࡮ࠡࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠥࡺࡥࡴࡶࠣࡷࡹࡧࡴࡶࡵ࠽ࠤࢀࢃࠧ൰").format(str(e)))
  bstack1l1l11_opy_(item, call, rep)
def bstack1l1llll_opy_(framework_name):
  global bstack1lll1l11l_opy_
  global bstack1l1111l1_opy_
  global bstack1lllll1l1_opy_
  bstack1lll1l11l_opy_ = framework_name
  logger.info(bstack11l11111_opy_.format(bstack1lll1l11l_opy_.split(bstack111lll1l_opy_ (u"ࠫ࠲࠭൱"))[0]))
  try:
    from selenium import webdriver
    from selenium.webdriver.common.service import Service
    from selenium.webdriver.remote.webdriver import WebDriver
    Service.start = bstack1ll11ll11_opy_
    Service.stop = bstack1l1lll11l_opy_
    webdriver.Remote.__init__ = bstack1_opy_
    webdriver.Remote.get = bstack11lll1ll1_opy_
    WebDriver.close = bstack1l1ll1l11_opy_
    WebDriver.quit = bstack11ll1l11_opy_
    bstack1l1111l1_opy_ = True
  except Exception as e:
    pass
  bstack11l11l_opy_()
  if not bstack1l1111l1_opy_:
    bstack1ll1111l_opy_(bstack111lll1l_opy_ (u"ࠧࡖࡡࡤ࡭ࡤ࡫ࡪࡹࠠ࡯ࡱࡷࠤ࡮ࡴࡳࡵࡣ࡯ࡰࡪࡪࠢ൲"), bstack11l1lllll_opy_)
  if bstack1ll1ll111_opy_():
    try:
      from selenium.webdriver.remote.remote_connection import RemoteConnection
      RemoteConnection._get_proxy_url = bstack11l1ll1_opy_
    except Exception as e:
      logger.error(bstack11ll11l1l_opy_.format(str(e)))
  if (bstack111lll1l_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬ൳") in str(framework_name).lower()):
    try:
      from robot import run_cli
      from robot.output import Output
      from robot.running.status import TestStatus
      from pabot.pabot import QueueItem
      from pabot import pabot
      try:
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCreator
        WebDriverCreator._get_ff_profile = bstack11ll1lll_opy_
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCache
        WebDriverCache.close = bstack11l1111l1_opy_
      except Exception as e:
        logger.warn(bstack111l11lll_opy_ + str(e))
      try:
        from AppiumLibrary.utils.applicationcache import ApplicationCache
        ApplicationCache.close = bstack111l11111_opy_
      except Exception as e:
        logger.debug(bstack11_opy_ + str(e))
    except Exception as e:
      bstack1ll1111l_opy_(e, bstack111l11lll_opy_)
    Output.end_test = bstack1l1l1l111_opy_
    TestStatus.__init__ = bstack111111l1_opy_
    QueueItem.__init__ = bstack1ll_opy_
    pabot._create_items = bstack111ll11_opy_
    try:
      from pabot import __version__ as bstack11ll1l1_opy_
      if version.parse(bstack11ll1l1_opy_) >= version.parse(bstack111lll1l_opy_ (u"ࠧ࠳࠰࠴࠹࠳࠶ࠧ൴")):
        pabot._run = bstack11l1l1l1l_opy_
      elif version.parse(bstack11ll1l1_opy_) >= version.parse(bstack111lll1l_opy_ (u"ࠨ࠴࠱࠵࠸࠴࠰ࠨ൵")):
        pabot._run = bstack111lll_opy_
      else:
        pabot._run = bstack1ll1111l1_opy_
    except Exception as e:
      pabot._run = bstack1ll1111l1_opy_
    pabot._create_command_for_execution = bstack11l1l1l11_opy_
    pabot._report_results = bstack11lll_opy_
  if bstack111lll1l_opy_ (u"ࠩࡥࡩ࡭ࡧࡶࡦࠩ൶") in str(framework_name).lower():
    try:
      from behave.runner import Runner
      from behave.model import Step
    except Exception as e:
      bstack1ll1111l_opy_(e, bstack111l1l1l1_opy_)
    Runner.run_hook = bstack1l1ll1ll1_opy_
    Step.run = bstack11l111lll_opy_
  if bstack111lll1l_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࠪ൷") in str(framework_name).lower():
    try:
      from pytest_selenium import pytest_selenium
      from _pytest.config import Config
      pytest_selenium.pytest_report_header = bstack11lll11l1_opy_
      from pytest_selenium.drivers import browserstack
      browserstack.pytest_selenium_runtest_makereport = bstack11111l_opy_
      Config.getoption = bstack1l1ll11ll_opy_
    except Exception as e:
      pass
    try:
      from _pytest import runner
      runner._update_current_test_var = bstack11l11lll_opy_
    except Exception as e:
      pass
    try:
      from pytest_bdd import reporting
      reporting.runtest_makereport = bstack11l111ll_opy_
    except Exception as e:
      pass
def bstack1l11ll1ll_opy_():
  global CONFIG
  if bstack111lll1l_opy_ (u"ࠫࡵࡧࡲࡢ࡮࡯ࡩࡱࡹࡐࡦࡴࡓࡰࡦࡺࡦࡰࡴࡰࠫ൸") in CONFIG and int(CONFIG[bstack111lll1l_opy_ (u"ࠬࡶࡡࡳࡣ࡯ࡰࡪࡲࡳࡑࡧࡵࡔࡱࡧࡴࡧࡱࡵࡱࠬ൹")]) > 1:
    logger.warn(bstack1llll1l_opy_)
def bstack11l1l1111_opy_(arg):
  arg.append(bstack111lll1l_opy_ (u"ࠨ࠭࠮࡫ࡰࡴࡴࡸࡴ࠮࡯ࡲࡨࡪࡃࡩ࡮ࡲࡲࡶࡹࡲࡩࡣࠤൺ"))
  arg.append(bstack111lll1l_opy_ (u"ࠢ࠮࡙ࠥൻ"))
  arg.append(bstack111lll1l_opy_ (u"ࠣ࡫ࡪࡲࡴࡸࡥ࠻ࡏࡲࡨࡺࡲࡥࠡࡣ࡯ࡶࡪࡧࡤࡺࠢ࡬ࡱࡵࡵࡲࡵࡧࡧ࠾ࡵࡿࡴࡦࡵࡷ࠲ࡕࡿࡴࡦࡵࡷ࡛ࡦࡸ࡮ࡪࡰࡪࠦർ"))
  arg.append(bstack111lll1l_opy_ (u"ࠤ࠰࡛ࠧൽ"))
  arg.append(bstack111lll1l_opy_ (u"ࠥ࡭࡬ࡴ࡯ࡳࡧ࠽ࡘ࡭࡫ࠠࡩࡱࡲ࡯࡮ࡳࡰ࡭ࠤൾ"))
  global CONFIG
  bstack1l1llll_opy_(bstack1ll111l1l_opy_)
  os.environ[bstack111lll1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢ࡙ࡘࡋࡒࡏࡃࡐࡉࠬൿ")] = CONFIG[bstack111lll1l_opy_ (u"ࠬࡻࡳࡦࡴࡑࡥࡲ࡫ࠧ඀")]
  os.environ[bstack111lll1l_opy_ (u"࠭ࡂࡓࡑ࡚ࡗࡊࡘࡓࡕࡃࡆࡏࡤࡇࡃࡄࡇࡖࡗࡤࡑࡅ࡚ࠩඁ")] = CONFIG[bstack111lll1l_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪං")]
  from _pytest.config import main as bstack1l1_opy_
  bstack1l1_opy_(arg)
def bstack1lll11l11_opy_(arg):
  bstack1l1llll_opy_(bstack111l1l11_opy_)
  from behave.__main__ import main as bstack1l11l1_opy_
  bstack1l11l1_opy_(arg)
def bstack1l1ll1l_opy_():
  logger.info(bstack1l11l1lll_opy_)
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument(bstack111lll1l_opy_ (u"ࠨࡵࡨࡸࡺࡶࠧඃ"), help=bstack111lll1l_opy_ (u"ࠩࡊࡩࡳ࡫ࡲࡢࡶࡨࠤࡧࡸ࡯ࡸࡵࡨࡶࡸࡺࡡࡤ࡭ࠣࡧࡴࡴࡦࡪࡩࠪ඄"))
  parser.add_argument(bstack111lll1l_opy_ (u"ࠪ࠱ࡺ࠭අ"), bstack111lll1l_opy_ (u"ࠫ࠲࠳ࡵࡴࡧࡵࡲࡦࡳࡥࠨආ"), help=bstack111lll1l_opy_ (u"ࠬ࡟࡯ࡶࡴࠣࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࠢࡸࡷࡪࡸ࡮ࡢ࡯ࡨࠫඇ"))
  parser.add_argument(bstack111lll1l_opy_ (u"࠭࠭࡬ࠩඈ"), bstack111lll1l_opy_ (u"ࠧ࠮࠯࡮ࡩࡾ࠭ඉ"), help=bstack111lll1l_opy_ (u"ࠨ࡛ࡲࡹࡷࠦࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠥࡧࡣࡤࡧࡶࡷࠥࡱࡥࡺࠩඊ"))
  parser.add_argument(bstack111lll1l_opy_ (u"ࠩ࠰ࡪࠬඋ"), bstack111lll1l_opy_ (u"ࠪ࠱࠲࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨඌ"), help=bstack111lll1l_opy_ (u"ࠫ࡞ࡵࡵࡳࠢࡷࡩࡸࡺࠠࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪඍ"))
  bstack11l111ll1_opy_ = parser.parse_args()
  try:
    bstack1l1l1l1l_opy_ = bstack111lll1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮࠲࡬࡫࡮ࡦࡴ࡬ࡧ࠳ࡿ࡭࡭࠰ࡶࡥࡲࡶ࡬ࡦࠩඎ")
    if bstack11l111ll1_opy_.framework and bstack11l111ll1_opy_.framework not in (bstack111lll1l_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭ඏ"), bstack111lll1l_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴ࠳ࠨඐ")):
      bstack1l1l1l1l_opy_ = bstack111lll1l_opy_ (u"ࠨࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭࠱ࡽࡲࡲ࠮ࡴࡣࡰࡴࡱ࡫ࠧඑ")
    bstack1ll1l1lll_opy_ = os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack1l1l1l1l_opy_)
    bstack111l1111l_opy_ = open(bstack1ll1l1lll_opy_, bstack111lll1l_opy_ (u"ࠩࡵࠫඒ"))
    bstack11l1ll111_opy_ = bstack111l1111l_opy_.read()
    bstack111l1111l_opy_.close()
    if bstack11l111ll1_opy_.username:
      bstack11l1ll111_opy_ = bstack11l1ll111_opy_.replace(bstack111lll1l_opy_ (u"ࠪ࡝ࡔ࡛ࡒࡠࡗࡖࡉࡗࡔࡁࡎࡇࠪඓ"), bstack11l111ll1_opy_.username)
    if bstack11l111ll1_opy_.key:
      bstack11l1ll111_opy_ = bstack11l1ll111_opy_.replace(bstack111lll1l_opy_ (u"ࠫ࡞ࡕࡕࡓࡡࡄࡇࡈࡋࡓࡔࡡࡎࡉ࡞࠭ඔ"), bstack11l111ll1_opy_.key)
    if bstack11l111ll1_opy_.framework:
      bstack11l1ll111_opy_ = bstack11l1ll111_opy_.replace(bstack111lll1l_opy_ (u"ࠬ࡟ࡏࡖࡔࡢࡊࡗࡇࡍࡆ࡙ࡒࡖࡐ࠭ඕ"), bstack11l111ll1_opy_.framework)
    file_name = bstack111lll1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠳ࡿ࡭࡭ࠩඖ")
    file_path = os.path.abspath(file_name)
    bstack1l1111l_opy_ = open(file_path, bstack111lll1l_opy_ (u"ࠧࡸࠩ඗"))
    bstack1l1111l_opy_.write(bstack11l1ll111_opy_)
    bstack1l1111l_opy_.close()
    logger.info(bstack1111_opy_)
    try:
      os.environ[bstack111lll1l_opy_ (u"ࠨࡄࡕࡓ࡜࡙ࡅࡓࡕࡗࡅࡈࡑ࡟ࡇࡔࡄࡑࡊ࡝ࡏࡓࡍࠪ඘")] = bstack11l111ll1_opy_.framework if bstack11l111ll1_opy_.framework != None else bstack111lll1l_opy_ (u"ࠤࠥ඙")
      config = yaml.safe_load(bstack11l1ll111_opy_)
      config[bstack111lll1l_opy_ (u"ࠪࡷࡴࡻࡲࡤࡧࠪක")] = bstack111lll1l_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱ࠱ࡸ࡫ࡴࡶࡲࠪඛ")
      bstack1ll1ll1l_opy_(bstack1l1l11l1_opy_, config)
    except Exception as e:
      logger.debug(bstack11l1111_opy_.format(str(e)))
  except Exception as e:
    logger.error(bstack111l11ll1_opy_.format(str(e)))
def bstack1ll1ll1l_opy_(bstack1ll11l11_opy_, config, bstack1ll1ll1l1_opy_ = {}):
  global bstack1lllll111_opy_
  if not config:
    return
  bstack11l11l11l_opy_ = bstack111l1l1_opy_ if not bstack1lllll111_opy_ else ( bstack1l1llll1_opy_ if bstack111lll1l_opy_ (u"ࠬࡧࡰࡱࠩග") in config else bstack11llll111_opy_ )
  data = {
    bstack111lll1l_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨඝ"): config[bstack111lll1l_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩඞ")],
    bstack111lll1l_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫඟ"): config[bstack111lll1l_opy_ (u"ࠩࡤࡧࡨ࡫ࡳࡴࡍࡨࡽࠬච")],
    bstack111lll1l_opy_ (u"ࠪࡩࡻ࡫࡮ࡵࡡࡷࡽࡵ࡫ࠧඡ"): bstack1ll11l11_opy_,
    bstack111lll1l_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡴࡷࡵࡰࡦࡴࡷ࡭ࡪࡹࠧජ"): {
      bstack111lll1l_opy_ (u"ࠬࡲࡡ࡯ࡩࡸࡥ࡬࡫࡟ࡧࡴࡤࡱࡪࡽ࡯ࡳ࡭ࠪඣ"): str(config[bstack111lll1l_opy_ (u"࠭ࡳࡰࡷࡵࡧࡪ࠭ඤ")]) if bstack111lll1l_opy_ (u"ࠧࡴࡱࡸࡶࡨ࡫ࠧඥ") in config else bstack111lll1l_opy_ (u"ࠣࡷࡱ࡯ࡳࡵࡷ࡯ࠤඦ"),
      bstack111lll1l_opy_ (u"ࠩࡵࡩ࡫࡫ࡲࡳࡧࡵࠫට"): bstack11l1l1lll_opy_(os.getenv(bstack111lll1l_opy_ (u"ࠥࡆࡗࡕࡗࡔࡇࡕࡗ࡙ࡇࡃࡌࡡࡉࡖࡆࡓࡅࡘࡑࡕࡏࠧඨ"), bstack111lll1l_opy_ (u"ࠦࠧඩ"))),
      bstack111lll1l_opy_ (u"ࠬࡲࡡ࡯ࡩࡸࡥ࡬࡫ࠧඪ"): bstack111lll1l_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭ණ"),
      bstack111lll1l_opy_ (u"ࠧࡱࡴࡲࡨࡺࡩࡴࠨඬ"): bstack11l11l11l_opy_,
      bstack111lll1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡎࡢ࡯ࡨࠫත"): config[bstack111lll1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬථ")]if config[bstack111lll1l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡐࡤࡱࡪ࠭ද")] else bstack111lll1l_opy_ (u"ࠦࡺࡴ࡫࡯ࡱࡺࡲࠧධ"),
      bstack111lll1l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧන"): str(config[bstack111lll1l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ඲")]) if bstack111lll1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩඳ") in config else bstack111lll1l_opy_ (u"ࠣࡷࡱ࡯ࡳࡵࡷ࡯ࠤප"),
      bstack111lll1l_opy_ (u"ࠩࡲࡷࠬඵ"): sys.platform,
      bstack111lll1l_opy_ (u"ࠪ࡬ࡴࡹࡴ࡯ࡣࡰࡩࠬබ"): socket.gethostname()
    }
  }
  update(data[bstack111lll1l_opy_ (u"ࠫࡪࡼࡥ࡯ࡶࡢࡴࡷࡵࡰࡦࡴࡷ࡭ࡪࡹࠧභ")], bstack1ll1ll1l1_opy_)
  try:
    response = bstack11lll1l1_opy_(bstack111lll1l_opy_ (u"ࠬࡖࡏࡔࡖࠪම"), bstack111l1l1ll_opy_, data, config)
    if response:
      logger.debug(bstack1l_opy_.format(bstack1ll11l11_opy_, str(response.json())))
  except Exception as e:
    logger.debug(bstack1ll11111l_opy_.format(str(e)))
def bstack11lll1l1_opy_(type, url, data, config):
  bstack11l11lll1_opy_ = bstack11l111l11_opy_.format(url)
  proxies = bstack1l11111l_opy_(config, bstack11l11lll1_opy_)
  if type == bstack111lll1l_opy_ (u"࠭ࡐࡐࡕࡗࠫඹ"):
    response = requests.post(bstack11l11lll1_opy_, json=data,
                    headers={bstack111lll1l_opy_ (u"ࠧࡄࡱࡱࡸࡪࡴࡴ࠮ࡖࡼࡴࡪ࠭ය"): bstack111lll1l_opy_ (u"ࠨࡣࡳࡴࡱ࡯ࡣࡢࡶ࡬ࡳࡳ࠵ࡪࡴࡱࡱࠫර")}, auth=(config[bstack111lll1l_opy_ (u"ࠩࡸࡷࡪࡸࡎࡢ࡯ࡨࠫ඼")], config[bstack111lll1l_opy_ (u"ࠪࡥࡨࡩࡥࡴࡵࡎࡩࡾ࠭ල")]), proxies=proxies)
  return response
def bstack11l1l1lll_opy_(framework):
  return bstack111lll1l_opy_ (u"ࠦࢀࢃ࠭ࡱࡻࡷ࡬ࡴࡴࡡࡨࡧࡱࡸ࠴ࢁࡽࠣ඾").format(str(framework), __version__) if framework else bstack111lll1l_opy_ (u"ࠧࡶࡹࡵࡪࡲࡲࡦ࡭ࡥ࡯ࡶ࠲ࡿࢂࠨ඿").format(__version__)
def bstack1llll11_opy_():
  global CONFIG
  if bool(CONFIG):
    return
  try:
    bstack1l1l111_opy_()
    logger.debug(bstack1l11l_opy_.format(str(CONFIG)))
    bstack11llllll1_opy_()
    bstack11l11l1ll_opy_()
  except Exception as e:
    logger.error(bstack111lll1l_opy_ (u"ࠨࡆࡢ࡫࡯ࡩࡩࠦࡴࡰࠢࡶࡩࡹࡻࡰ࠭ࠢࡨࡶࡷࡵࡲ࠻ࠢࠥව") + str(e))
    sys.exit(1)
  sys.excepthook = bstack1l1111l11_opy_
  atexit.register(bstack1ll1l11l_opy_)
  signal.signal(signal.SIGINT, bstack11ll11l_opy_)
  signal.signal(signal.SIGTERM, bstack11ll11l_opy_)
def bstack1l1111l11_opy_(exctype, value, traceback):
  global bstack1lll_opy_
  try:
    for driver in bstack1lll_opy_:
      driver.execute_script(
        bstack111lll1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࡥࡥࡹࡧࡦࡹࡹࡵࡲ࠻ࠢࡾࠦࡦࡩࡴࡪࡱࡱࠦ࠿ࠦࠢࡴࡧࡷࡗࡪࡹࡳࡪࡱࡱࡗࡹࡧࡴࡶࡵࠥ࠰ࠥࠨࡡࡳࡩࡸࡱࡪࡴࡴࡴࠤ࠽ࠤࢀࠨࡳࡵࡣࡷࡹࡸࠨ࠺ࠣࡨࡤ࡭ࡱ࡫ࡤࠣ࠮ࠣࠦࡷ࡫ࡡࡴࡱࡱࠦ࠿ࠦࠧශ") + json.dumps(bstack111lll1l_opy_ (u"ࠣࡕࡨࡷࡸ࡯࡯࡯ࠢࡩࡥ࡮ࡲࡥࡥࠢࡺ࡭ࡹ࡮࠺ࠡ࡞ࡱࠦෂ") + str(value)) + bstack111lll1l_opy_ (u"ࠩࢀࢁࠬස"))
  except Exception:
    pass
  bstack1ll1l1l_opy_(value)
  sys.__excepthook__(exctype, value, traceback)
  sys.exit(1)
def bstack1ll1l1l_opy_(message = bstack111lll1l_opy_ (u"ࠪࠫහ")):
  global CONFIG
  try:
    if message:
      bstack1ll1ll1l1_opy_ = {
        bstack111lll1l_opy_ (u"ࠫࡪࡸࡲࡰࡴࠪළ"): str(message)
      }
      bstack1ll1ll1l_opy_(bstack11llll11_opy_, CONFIG, bstack1ll1ll1l1_opy_)
    else:
      bstack1ll1ll1l_opy_(bstack11llll11_opy_, CONFIG)
  except Exception as e:
    logger.debug(bstack1l111l111_opy_.format(str(e)))
def bstack1l11lll_opy_(bstack1lll1ll1l_opy_, size):
  bstack1l1l11l_opy_ = []
  while len(bstack1lll1ll1l_opy_) > size:
    bstack11l1lll11_opy_ = bstack1lll1ll1l_opy_[:size]
    bstack1l1l11l_opy_.append(bstack11l1lll11_opy_)
    bstack1lll1ll1l_opy_   = bstack1lll1ll1l_opy_[size:]
  bstack1l1l11l_opy_.append(bstack1lll1ll1l_opy_)
  return bstack1l1l11l_opy_
def bstack11l1l11_opy_(args):
  if bstack111lll1l_opy_ (u"ࠬ࠳࡭ࠨෆ") in args and bstack111lll1l_opy_ (u"࠭ࡰࡥࡤࠪ෇") in args:
    return True
  return False
def run_on_browserstack(bstack111ll_opy_=None, bstack1l1111111_opy_=None, bstack1111111_opy_=False):
  global CONFIG
  global bstack1l111ll1_opy_
  global bstack111llll11_opy_
  bstack1l11ll1l1_opy_ = bstack111lll1l_opy_ (u"ࠧࠨ෈")
  if bstack111ll_opy_ and isinstance(bstack111ll_opy_, str):
    bstack111ll_opy_ = eval(bstack111ll_opy_)
  if bstack111ll_opy_:
    CONFIG = bstack111ll_opy_[bstack111lll1l_opy_ (u"ࠨࡅࡒࡒࡋࡏࡇࠨ෉")]
    bstack1l111ll1_opy_ = bstack111ll_opy_[bstack111lll1l_opy_ (u"ࠩࡋ࡙ࡇࡥࡕࡓࡎ්ࠪ")]
    bstack111llll11_opy_ = bstack111ll_opy_[bstack111lll1l_opy_ (u"ࠪࡍࡘࡥࡁࡑࡒࡢࡅ࡚࡚ࡏࡎࡃࡗࡉࠬ෋")]
    bstack1l11ll1l1_opy_ = bstack111lll1l_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫ෌")
  if not bstack1111111_opy_:
    if len(sys.argv) <= 1:
      logger.critical(bstack111l1l_opy_)
      return
    if sys.argv[1] == bstack111lll1l_opy_ (u"ࠬ࠳࠭ࡷࡧࡵࡷ࡮ࡵ࡮ࠨ෍")  or sys.argv[1] == bstack111lll1l_opy_ (u"࠭࠭ࡷࠩ෎"):
      logger.info(bstack111lll1l_opy_ (u"ࠧࡃࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰࠦࡐࡺࡶ࡫ࡳࡳࠦࡓࡅࡍࠣࡺࢀࢃࠧා").format(__version__))
      return
    if sys.argv[1] == bstack111lll1l_opy_ (u"ࠨࡵࡨࡸࡺࡶࠧැ"):
      bstack1l1ll1l_opy_()
      return
  args = sys.argv
  bstack1llll11_opy_()
  global bstack1l1lll1_opy_
  global bstack111l1ll11_opy_
  global bstack1lll1l1ll_opy_
  global bstack1l1l1111_opy_
  global bstack111l1ll1_opy_
  global bstack1ll11l111_opy_
  global bstack1111l11l_opy_
  global bstack1lllll1l1_opy_
  if not bstack1l11ll1l1_opy_:
    if args[1] == bstack111lll1l_opy_ (u"ࠩࡳࡽࡹ࡮࡯࡯ࠩෑ") or args[1] == bstack111lll1l_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰ࠶ࠫි"):
      bstack1l11ll1l1_opy_ = bstack111lll1l_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱࠫී")
      args = args[2:]
    elif args[1] == bstack111lll1l_opy_ (u"ࠬࡸ࡯ࡣࡱࡷࠫු"):
      bstack1l11ll1l1_opy_ = bstack111lll1l_opy_ (u"࠭ࡲࡰࡤࡲࡸࠬ෕")
      args = args[2:]
    elif args[1] == bstack111lll1l_opy_ (u"ࠧࡱࡣࡥࡳࡹ࠭ූ"):
      bstack1l11ll1l1_opy_ = bstack111lll1l_opy_ (u"ࠨࡲࡤࡦࡴࡺࠧ෗")
      args = args[2:]
    elif args[1] == bstack111lll1l_opy_ (u"ࠩࡵࡳࡧࡵࡴ࠮࡫ࡱࡸࡪࡸ࡮ࡢ࡮ࠪෘ"):
      bstack1l11ll1l1_opy_ = bstack111lll1l_opy_ (u"ࠪࡶࡴࡨ࡯ࡵ࠯࡬ࡲࡹ࡫ࡲ࡯ࡣ࡯ࠫෙ")
      args = args[2:]
    elif args[1] == bstack111lll1l_opy_ (u"ࠫࡵࡿࡴࡦࡵࡷࠫේ"):
      bstack1l11ll1l1_opy_ = bstack111lll1l_opy_ (u"ࠬࡶࡹࡵࡧࡶࡸࠬෛ")
      args = args[2:]
    elif args[1] == bstack111lll1l_opy_ (u"࠭ࡢࡦࡪࡤࡺࡪ࠭ො"):
      bstack1l11ll1l1_opy_ = bstack111lll1l_opy_ (u"ࠧࡣࡧ࡫ࡥࡻ࡫ࠧෝ")
      args = args[2:]
    else:
      if not bstack111lll1l_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫෞ") in CONFIG or str(CONFIG[bstack111lll1l_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠬෟ")]).lower() in [bstack111lll1l_opy_ (u"ࠪࡴࡾࡺࡨࡰࡰࠪ෠"), bstack111lll1l_opy_ (u"ࠫࡵࡿࡴࡩࡱࡱ࠷ࠬ෡")]:
        bstack1l11ll1l1_opy_ = bstack111lll1l_opy_ (u"ࠬࡶࡹࡵࡪࡲࡲࠬ෢")
        args = args[1:]
      elif str(CONFIG[bstack111lll1l_opy_ (u"࠭ࡦࡳࡣࡰࡩࡼࡵࡲ࡬ࠩ෣")]).lower() == bstack111lll1l_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭෤"):
        bstack1l11ll1l1_opy_ = bstack111lll1l_opy_ (u"ࠨࡴࡲࡦࡴࡺࠧ෥")
        args = args[1:]
      elif str(CONFIG[bstack111lll1l_opy_ (u"ࠩࡩࡶࡦࡳࡥࡸࡱࡵ࡯ࠬ෦")]).lower() == bstack111lll1l_opy_ (u"ࠪࡴࡦࡨ࡯ࡵࠩ෧"):
        bstack1l11ll1l1_opy_ = bstack111lll1l_opy_ (u"ࠫࡵࡧࡢࡰࡶࠪ෨")
        args = args[1:]
      elif str(CONFIG[bstack111lll1l_opy_ (u"ࠬ࡬ࡲࡢ࡯ࡨࡻࡴࡸ࡫ࠨ෩")]).lower() == bstack111lll1l_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭෪"):
        bstack1l11ll1l1_opy_ = bstack111lll1l_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺࠧ෫")
        args = args[1:]
      elif str(CONFIG[bstack111lll1l_opy_ (u"ࠨࡨࡵࡥࡲ࡫ࡷࡰࡴ࡮ࠫ෬")]).lower() == bstack111lll1l_opy_ (u"ࠩࡥࡩ࡭ࡧࡶࡦࠩ෭"):
        bstack1l11ll1l1_opy_ = bstack111lll1l_opy_ (u"ࠪࡦࡪ࡮ࡡࡷࡧࠪ෮")
        args = args[1:]
      else:
        os.environ[bstack111lll1l_opy_ (u"ࠫࡇࡘࡏࡘࡕࡈࡖࡘ࡚ࡁࡄࡍࡢࡊࡗࡇࡍࡆ࡙ࡒࡖࡐ࠭෯")] = bstack1l11ll1l1_opy_
        bstack1l11ll1l_opy_(bstack11l1ll1ll_opy_)
  global bstack111ll1_opy_
  if bstack111ll_opy_:
    try:
      os.environ[bstack111lll1l_opy_ (u"ࠬࡈࡒࡐ࡙ࡖࡉࡗ࡙ࡔࡂࡅࡎࡣࡋࡘࡁࡎࡇ࡚ࡓࡗࡑࠧ෰")] = bstack1l11ll1l1_opy_
      bstack1ll1ll1l_opy_(bstack1l1l1l_opy_, CONFIG)
    except Exception as e:
      logger.debug(bstack1l111l111_opy_.format(str(e)))
  global bstack111l111_opy_
  global bstack1llll1l1l_opy_
  global bstack1l1lll_opy_
  global bstack1l11ll1_opy_
  global bstack111lll11_opy_
  global bstack11l1l111_opy_
  global bstack1l11lllll_opy_
  global bstack1l1llllll_opy_
  global bstack111lll11l_opy_
  global bstack111111ll_opy_
  global bstack1lll111ll_opy_
  global bstack11l1l11l1_opy_
  global bstack1l111llll_opy_
  global bstack1111ll1l_opy_
  global bstack1ll1l1ll_opy_
  global bstack1l1lll111_opy_
  global bstack1l1ll1lll_opy_
  global bstack111l11l_opy_
  global bstack1l1l11_opy_
  try:
    from selenium import webdriver
    from selenium.webdriver.remote.webdriver import WebDriver
    bstack111l111_opy_ = webdriver.Remote.__init__
    bstack1llll1l1l_opy_ = WebDriver.quit
    bstack1lll111ll_opy_ = WebDriver.close
    bstack1111ll1l_opy_ = WebDriver.get
  except Exception as e:
    pass
  try:
    import Browser
    from subprocess import Popen
    bstack111ll1_opy_ = Popen.__init__
  except Exception as e:
    pass
  if bstack11lll1ll_opy_():
    if bstack1l111lll_opy_() < version.parse(bstack1l1lll1ll_opy_):
      logger.error(bstack11l11l1_opy_.format(bstack1l111lll_opy_()))
    else:
      try:
        from selenium.webdriver.remote.remote_connection import RemoteConnection
        bstack1ll1l1ll_opy_ = RemoteConnection._get_proxy_url
      except Exception as e:
        logger.error(bstack11ll11l1l_opy_.format(str(e)))
  if bstack1l11ll1l1_opy_ != bstack111lll1l_opy_ (u"࠭ࡰࡺࡶ࡫ࡳࡳ࠭෱") or (bstack1l11ll1l1_opy_ == bstack111lll1l_opy_ (u"ࠧࡱࡻࡷ࡬ࡴࡴࠧෲ") and not bstack111ll_opy_):
    bstack11l11ll1l_opy_()
  if (bstack1l11ll1l1_opy_ in [bstack111lll1l_opy_ (u"ࠨࡲࡤࡦࡴࡺࠧෳ"), bstack111lll1l_opy_ (u"ࠩࡵࡳࡧࡵࡴࠨ෴"), bstack111lll1l_opy_ (u"ࠪࡶࡴࡨ࡯ࡵ࠯࡬ࡲࡹ࡫ࡲ࡯ࡣ࡯ࠫ෵")]):
    try:
      from robot import run_cli
      from robot.output import Output
      from robot.running.status import TestStatus
      from pabot.pabot import QueueItem
      from pabot import pabot
      try:
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCreator
        from SeleniumLibrary.keywords.webdrivertools.webdrivertools import WebDriverCache
        WebDriverCreator._get_ff_profile = bstack11ll1lll_opy_
        bstack111lll11_opy_ = WebDriverCache.close
      except Exception as e:
        logger.warn(bstack111l11lll_opy_ + str(e))
      try:
        from AppiumLibrary.utils.applicationcache import ApplicationCache
        bstack1l11ll1_opy_ = ApplicationCache.close
      except Exception as e:
        logger.debug(bstack11_opy_ + str(e))
    except Exception as e:
      bstack1ll1111l_opy_(e, bstack111l11lll_opy_)
    if bstack1l11ll1l1_opy_ != bstack111lll1l_opy_ (u"ࠫࡷࡵࡢࡰࡶ࠰࡭ࡳࡺࡥࡳࡰࡤࡰࠬ෶"):
      bstack1l11_opy_()
    bstack1l1lll_opy_ = Output.end_test
    bstack11l1l111_opy_ = TestStatus.__init__
    bstack1l1llllll_opy_ = pabot._run
    bstack111lll11l_opy_ = QueueItem.__init__
    bstack111111ll_opy_ = pabot._create_command_for_execution
    bstack111l11l_opy_ = pabot._report_results
  if bstack1l11ll1l1_opy_ == bstack111lll1l_opy_ (u"ࠬࡨࡥࡩࡣࡹࡩࠬ෷"):
    try:
      from behave.runner import Runner
      from behave.model import Step
    except Exception as e:
      bstack1ll1111l_opy_(e, bstack111l1l1l1_opy_)
    bstack11l1l11l1_opy_ = Runner.run_hook
    bstack1l111llll_opy_ = Step.run
  if bstack1l11ll1l1_opy_ == bstack111lll1l_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭෸"):
    try:
      from _pytest.config import Config
      bstack1l1lll111_opy_ = Config.getoption
      from _pytest import runner
      bstack1l1ll1lll_opy_ = runner._update_current_test_var
    except Exception as e:
      logger.warn(e, bstack11llll1_opy_)
    try:
      from pytest_bdd import reporting
      bstack1l1l11_opy_ = reporting.runtest_makereport
    except Exception as e:
      logger.debug(bstack111lll1l_opy_ (u"ࠧࡑ࡮ࡨࡥࡸ࡫ࠠࡪࡰࡶࡸࡦࡲ࡬ࠡࡲࡼࡸࡪࡹࡴ࠮ࡤࡧࡨࠥࡺ࡯ࠡࡴࡸࡲࠥࡶࡹࡵࡧࡶࡸ࠲ࡨࡤࡥࠢࡷࡩࡸࡺࡳࠨ෹"))
  if bstack1l11ll1l1_opy_ == bstack111lll1l_opy_ (u"ࠨࡲࡼࡸ࡭ࡵ࡮ࠨ෺"):
    bstack111l1ll11_opy_ = True
    if bstack111ll_opy_ and bstack1111111_opy_:
      bstack111l1ll1_opy_ = CONFIG.get(bstack111lll1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡖࡸࡦࡩ࡫ࡍࡱࡦࡥࡱࡕࡰࡵ࡫ࡲࡲࡸ࠭෻"), {}).get(bstack111lll1l_opy_ (u"ࠪࡰࡴࡩࡡ࡭ࡋࡧࡩࡳࡺࡩࡧ࡫ࡨࡶࠬ෼"))
      bstack1l1llll_opy_(bstack11ll11_opy_)
    elif bstack111ll_opy_:
      bstack111l1ll1_opy_ = CONFIG.get(bstack111lll1l_opy_ (u"ࠫࡧࡸ࡯ࡸࡵࡨࡶࡘࡺࡡࡤ࡭ࡏࡳࡨࡧ࡬ࡐࡲࡷ࡭ࡴࡴࡳࠨ෽"), {}).get(bstack111lll1l_opy_ (u"ࠬࡲ࡯ࡤࡣ࡯ࡍࡩ࡫࡮ࡵ࡫ࡩ࡭ࡪࡸࠧ෾"))
      global bstack1lll_opy_
      try:
        if bstack11l1l11_opy_(bstack111ll_opy_[bstack111lll1l_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩ෿")]) and multiprocessing.current_process().name == bstack111lll1l_opy_ (u"ࠧ࠱ࠩ฀"):
          bstack111ll_opy_[bstack111lll1l_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫก")].remove(bstack111lll1l_opy_ (u"ࠩ࠰ࡱࠬข"))
          bstack111ll_opy_[bstack111lll1l_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭ฃ")].remove(bstack111lll1l_opy_ (u"ࠫࡵࡪࡢࠨค"))
          bstack111ll_opy_[bstack111lll1l_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨฅ")] = bstack111ll_opy_[bstack111lll1l_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩฆ")][0]
          with open(bstack111ll_opy_[bstack111lll1l_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪง")], bstack111lll1l_opy_ (u"ࠨࡴࠪจ")) as f:
            bstack1lll1lll1_opy_ = f.read()
          bstack111l1l111_opy_ = bstack111lll1l_opy_ (u"ࠤࠥࠦ࡫ࡸ࡯࡮ࠢࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠࡵࡧ࡯ࠥ࡯࡭ࡱࡱࡵࡸࠥࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣ࡮ࡴࡩࡵ࡫ࡤࡰ࡮ࢀࡥ࠼ࠢࡥࡶࡴࡽࡳࡦࡴࡶࡸࡦࡩ࡫ࡠ࡫ࡱ࡭ࡹ࡯ࡡ࡭࡫ࡽࡩ࠭ࢁࡽࠪ࠽ࠣࡪࡷࡵ࡭ࠡࡲࡧࡦࠥ࡯࡭ࡱࡱࡵࡸࠥࡖࡤࡣ࠽ࠣࡳ࡬ࡥࡤࡣࠢࡀࠤࡕࡪࡢ࠯ࡦࡲࡣࡧࡸࡥࡢ࡭࠾ࠎࡩ࡫ࡦࠡ࡯ࡲࡨࡤࡨࡲࡦࡣ࡮ࠬࡸ࡫࡬ࡧ࠮ࠣࡥࡷ࡭ࠬࠡࡶࡨࡱࡵࡵࡲࡢࡴࡼࠤࡂࠦ࠰ࠪ࠼ࠍࠤࠥࡺࡲࡺ࠼ࠍࠤࠥࠦࠠࡢࡴࡪࠤࡂࠦࡳࡵࡴࠫ࡭ࡳࡺࠨࡢࡴࡪ࠭࠰࠷࠰ࠪࠌࠣࠤࡪࡾࡣࡦࡲࡷࠤࡊࡾࡣࡦࡲࡷ࡭ࡴࡴࠠࡢࡵࠣࡩ࠿ࠐࠠࠡࠢࠣࡴࡦࡹࡳࠋࠢࠣࡳ࡬ࡥࡤࡣࠪࡶࡩࡱ࡬ࠬࡢࡴࡪ࠰ࡹ࡫࡭ࡱࡱࡵࡥࡷࡿࠩࠋࡒࡧࡦ࠳ࡪ࡯ࡠࡤࠣࡁࠥࡳ࡯ࡥࡡࡥࡶࡪࡧ࡫ࠋࡒࡧࡦ࠳ࡪ࡯ࡠࡤࡵࡩࡦࡱࠠ࠾ࠢࡰࡳࡩࡥࡢࡳࡧࡤ࡯ࠏࡖࡤࡣࠪࠬ࠲ࡸ࡫ࡴࡠࡶࡵࡥࡨ࡫ࠨࠪ࡞ࡱࠦࠧࠨฉ").format(str(bstack111ll_opy_))
          bstack111llll_opy_ = bstack111l1l111_opy_ + bstack1lll1lll1_opy_
          bstack11l1l1l1_opy_ = bstack111ll_opy_[bstack111lll1l_opy_ (u"ࠪࡪ࡮ࡲࡥࡠࡰࡤࡱࡪ࠭ช")] + bstack111lll1l_opy_ (u"ࠫࡤࡨࡳࡵࡣࡦ࡯ࡤࡺࡥ࡮ࡲ࠱ࡴࡾ࠭ซ")
          with open(bstack11l1l1l1_opy_, bstack111lll1l_opy_ (u"ࠬࡽࠧฌ")):
            pass
          with open(bstack11l1l1l1_opy_, bstack111lll1l_opy_ (u"ࠨࡷࠬࠤญ")) as f:
            f.write(bstack111llll_opy_)
          import subprocess
          bstack111llllll_opy_ = subprocess.run([bstack111lll1l_opy_ (u"ࠢࡱࡻࡷ࡬ࡴࡴࠢฎ"), bstack11l1l1l1_opy_])
          if os.path.exists(bstack11l1l1l1_opy_):
            os.unlink(bstack11l1l1l1_opy_)
          os._exit(bstack111llllll_opy_.returncode)
        else:
          if bstack11l1l11_opy_(bstack111ll_opy_[bstack111lll1l_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫฏ")]):
            bstack111ll_opy_[bstack111lll1l_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬฐ")].remove(bstack111lll1l_opy_ (u"ࠪ࠱ࡲ࠭ฑ"))
            bstack111ll_opy_[bstack111lll1l_opy_ (u"ࠫ࡫࡯࡬ࡦࡡࡱࡥࡲ࡫ࠧฒ")].remove(bstack111lll1l_opy_ (u"ࠬࡶࡤࡣࠩณ"))
            bstack111ll_opy_[bstack111lll1l_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩด")] = bstack111ll_opy_[bstack111lll1l_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪต")][0]
          bstack1l1llll_opy_(bstack11ll11_opy_)
          sys.path.append(os.path.dirname(os.path.abspath(bstack111ll_opy_[bstack111lll1l_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫถ")])))
          sys.argv = sys.argv[2:]
          mod_globals = globals()
          mod_globals[bstack111lll1l_opy_ (u"ࠩࡢࡣࡳࡧ࡭ࡦࡡࡢࠫท")] = bstack111lll1l_opy_ (u"ࠪࡣࡤࡳࡡࡪࡰࡢࡣࠬธ")
          mod_globals[bstack111lll1l_opy_ (u"ࠫࡤࡥࡦࡪ࡮ࡨࡣࡤ࠭น")] = os.path.abspath(bstack111ll_opy_[bstack111lll1l_opy_ (u"ࠬ࡬ࡩ࡭ࡧࡢࡲࡦࡳࡥࠨบ")])
          exec(open(bstack111ll_opy_[bstack111lll1l_opy_ (u"࠭ࡦࡪ࡮ࡨࡣࡳࡧ࡭ࡦࠩป")]).read(), mod_globals)
      except BaseException as e:
        try:
          traceback.print_exc()
          logger.error(bstack111lll1l_opy_ (u"ࠧࡄࡣࡸ࡫࡭ࡺࠠࡆࡺࡦࡩࡵࡺࡩࡰࡰ࠽ࠤࢀࢃࠧผ").format(str(e)))
          for driver in bstack1lll_opy_:
            bstack1l1111111_opy_.append({
              bstack111lll1l_opy_ (u"ࠨࡰࡤࡱࡪ࠭ฝ"): bstack111ll_opy_[bstack111lll1l_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬพ")],
              bstack111lll1l_opy_ (u"ࠪࡩࡷࡸ࡯ࡳࠩฟ"): str(e),
              bstack111lll1l_opy_ (u"ࠫ࡮ࡴࡤࡦࡺࠪภ"): multiprocessing.current_process().name
            })
            driver.execute_script(
              bstack111lll1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡣࡪࡾࡥࡤࡷࡷࡳࡷࡀࠠࡼࠤࡤࡧࡹ࡯࡯࡯ࠤ࠽ࠤࠧࡹࡥࡵࡕࡨࡷࡸ࡯࡯࡯ࡕࡷࡥࡹࡻࡳࠣ࠮ࠣࠦࡦࡸࡧࡶ࡯ࡨࡲࡹࡹࠢ࠻ࠢࡾࠦࡸࡺࡡࡵࡷࡶࠦ࠿ࠨࡦࡢ࡫࡯ࡩࡩࠨࠬࠡࠤࡵࡩࡦࡹ࡯࡯ࠤ࠽ࠤࠬม") + json.dumps(bstack111lll1l_opy_ (u"ࠨࡓࡦࡵࡶ࡭ࡴࡴࠠࡧࡣ࡬ࡰࡪࡪࠠࡸ࡫ࡷ࡬࠿ࠦ࡜࡯ࠤย") + str(e)) + bstack111lll1l_opy_ (u"ࠧࡾࡿࠪร"))
        except Exception:
          pass
      finally:
        try:
          for driver in bstack1lll_opy_:
            driver.quit()
        except Exception as e:
          pass
    else:
      bstack1lll1111_opy_()
      bstack1l11ll1ll_opy_()
      bstack11l11111l_opy_ = {
        bstack111lll1l_opy_ (u"ࠨࡨ࡬ࡰࡪࡥ࡮ࡢ࡯ࡨࠫฤ"): args[0],
        bstack111lll1l_opy_ (u"ࠩࡆࡓࡓࡌࡉࡈࠩล"): CONFIG,
        bstack111lll1l_opy_ (u"ࠪࡌ࡚ࡈ࡟ࡖࡔࡏࠫฦ"): bstack1l111ll1_opy_,
        bstack111lll1l_opy_ (u"ࠫࡎ࡙࡟ࡂࡒࡓࡣࡆ࡛ࡔࡐࡏࡄࡘࡊ࠭ว"): bstack111llll11_opy_
      }
      if bstack111lll1l_opy_ (u"ࠬࡶ࡬ࡢࡶࡩࡳࡷࡳࡳࠨศ") in CONFIG:
        bstack1lllllll1_opy_ = []
        manager = multiprocessing.Manager()
        bstack11l1ll1l1_opy_ = manager.list()
        if bstack11l1l11_opy_(args):
          for index, platform in enumerate(CONFIG[bstack111lll1l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩษ")]):
            if index == 0:
              bstack11l11111l_opy_[bstack111lll1l_opy_ (u"ࠧࡧ࡫࡯ࡩࡤࡴࡡ࡮ࡧࠪส")] = args
            bstack1lllllll1_opy_.append(multiprocessing.Process(name=str(index),
                                          target=run_on_browserstack, args=(bstack11l11111l_opy_, bstack11l1ll1l1_opy_)))
        else:
          for index, platform in enumerate(CONFIG[bstack111lll1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫห")]):
            bstack1lllllll1_opy_.append(multiprocessing.Process(name=str(index),
                                          target=run_on_browserstack, args=(bstack11l11111l_opy_, bstack11l1ll1l1_opy_)))
        for t in bstack1lllllll1_opy_:
          t.start()
        for t in bstack1lllllll1_opy_:
          t.join()
        bstack1111l11l_opy_ = list(bstack11l1ll1l1_opy_)
      else:
        if bstack11l1l11_opy_(args):
          bstack11l11111l_opy_[bstack111lll1l_opy_ (u"ࠩࡩ࡭ࡱ࡫࡟࡯ࡣࡰࡩࠬฬ")] = args
          test = multiprocessing.Process(name=str(0),
                                        target=run_on_browserstack, args=(bstack11l11111l_opy_,))
          test.start()
          test.join()
        else:
          bstack1l1llll_opy_(bstack11ll11_opy_)
          sys.path.append(os.path.dirname(os.path.abspath(args[0])))
          mod_globals = globals()
          mod_globals[bstack111lll1l_opy_ (u"ࠪࡣࡤࡴࡡ࡮ࡧࡢࡣࠬอ")] = bstack111lll1l_opy_ (u"ࠫࡤࡥ࡭ࡢ࡫ࡱࡣࡤ࠭ฮ")
          mod_globals[bstack111lll1l_opy_ (u"ࠬࡥ࡟ࡧ࡫࡯ࡩࡤࡥࠧฯ")] = os.path.abspath(args[0])
          sys.argv = sys.argv[2:]
          exec(open(args[0]).read(), mod_globals)
  elif bstack1l11ll1l1_opy_ == bstack111lll1l_opy_ (u"࠭ࡰࡢࡤࡲࡸࠬะ") or bstack1l11ll1l1_opy_ == bstack111lll1l_opy_ (u"ࠧࡳࡱࡥࡳࡹ࠭ั"):
    try:
      from pabot import pabot
    except Exception as e:
      bstack1ll1111l_opy_(e, bstack111l11lll_opy_)
    bstack1lll1111_opy_()
    bstack1l1llll_opy_(bstack11l11_opy_)
    if bstack111lll1l_opy_ (u"ࠨ࠯࠰ࡴࡷࡵࡣࡦࡵࡶࡩࡸ࠭า") in args:
      i = args.index(bstack111lll1l_opy_ (u"ࠩ࠰࠱ࡵࡸ࡯ࡤࡧࡶࡷࡪࡹࠧำ"))
      args.pop(i)
      args.pop(i)
    args.insert(0, str(bstack1l1lll1_opy_))
    args.insert(0, str(bstack111lll1l_opy_ (u"ࠪ࠱࠲ࡶࡲࡰࡥࡨࡷࡸ࡫ࡳࠨิ")))
    pabot.main(args)
  elif bstack1l11ll1l1_opy_ == bstack111lll1l_opy_ (u"ࠫࡷࡵࡢࡰࡶ࠰࡭ࡳࡺࡥࡳࡰࡤࡰࠬี"):
    try:
      from robot import run_cli
    except Exception as e:
      bstack1ll1111l_opy_(e, bstack111l11lll_opy_)
    for a in args:
      if bstack111lll1l_opy_ (u"ࠬࡈࡓࡕࡃࡆࡏࡕࡒࡁࡕࡈࡒࡖࡒࡏࡎࡅࡇ࡛ࠫึ") in a:
        bstack1l1l1111_opy_ = int(a.split(bstack111lll1l_opy_ (u"࠭࠺ࠨื"))[1])
      if bstack111lll1l_opy_ (u"ࠧࡃࡕࡗࡅࡈࡑࡄࡆࡈࡏࡓࡈࡇࡌࡊࡆࡈࡒ࡙ࡏࡆࡊࡇࡕุࠫ") in a:
        bstack111l1ll1_opy_ = str(a.split(bstack111lll1l_opy_ (u"ࠨ࠼ูࠪ"))[1])
      if bstack111lll1l_opy_ (u"ࠩࡅࡗ࡙ࡇࡃࡌࡅࡏࡍࡆࡘࡇࡔฺࠩ") in a:
        bstack1ll11l111_opy_ = str(a.split(bstack111lll1l_opy_ (u"ࠪ࠾ࠬ฻"))[1])
    bstack11ll1l111_opy_ = None
    if bstack111lll1l_opy_ (u"ࠫ࠲࠳ࡢࡴࡶࡤࡧࡰࡥࡩࡵࡧࡰࡣ࡮ࡴࡤࡦࡺࠪ฼") in args:
      i = args.index(bstack111lll1l_opy_ (u"ࠬ࠳࠭ࡣࡵࡷࡥࡨࡱ࡟ࡪࡶࡨࡱࡤ࡯࡮ࡥࡧࡻࠫ฽"))
      args.pop(i)
      bstack11ll1l111_opy_ = args.pop(i)
    if bstack11ll1l111_opy_ is not None:
      global bstack11111l11_opy_
      bstack11111l11_opy_ = bstack11ll1l111_opy_
    bstack1l1llll_opy_(bstack11l11_opy_)
    run_cli(args)
  elif bstack1l11ll1l1_opy_ == bstack111lll1l_opy_ (u"࠭ࡰࡺࡶࡨࡷࡹ࠭฾"):
    try:
      from _pytest.config import _prepareconfig
      from _pytest.config import Config
      from _pytest import runner
      import importlib
      bstack1ll111lll_opy_ = importlib.find_loader(bstack111lll1l_opy_ (u"ࠧࡱࡻࡷࡩࡸࡺ࡟ࡴࡧ࡯ࡩࡳ࡯ࡵ࡮ࠩ฿"))
    except Exception as e:
      logger.warn(e, bstack11llll1_opy_)
    bstack1lll1111_opy_()
    try:
      if bstack111lll1l_opy_ (u"ࠨ࠯࠰ࡨࡷ࡯ࡶࡦࡴࠪเ") in args:
        i = args.index(bstack111lll1l_opy_ (u"ࠩ࠰࠱ࡩࡸࡩࡷࡧࡵࠫแ"))
        args.pop(i+1)
        args.pop(i)
      if bstack111lll1l_opy_ (u"ࠪ࠱࠲ࡶ࡬ࡶࡩ࡬ࡲࡸ࠭โ") in args:
        i = args.index(bstack111lll1l_opy_ (u"ࠫ࠲࠳ࡰ࡭ࡷࡪ࡭ࡳࡹࠧใ"))
        args.pop(i+1)
        args.pop(i)
      if bstack111lll1l_opy_ (u"ࠬ࠳ࡰࠨไ") in args:
        i = args.index(bstack111lll1l_opy_ (u"࠭࠭ࡱࠩๅ"))
        args.pop(i+1)
        args.pop(i)
      if bstack111lll1l_opy_ (u"ࠧ࠮࠯ࡱࡹࡲࡶࡲࡰࡥࡨࡷࡸ࡫ࡳࠨๆ") in args:
        i = args.index(bstack111lll1l_opy_ (u"ࠨ࠯࠰ࡲࡺࡳࡰࡳࡱࡦࡩࡸࡹࡥࡴࠩ็"))
        args.pop(i+1)
        args.pop(i)
      if bstack111lll1l_opy_ (u"ࠩ࠰ࡲ่ࠬ") in args:
        i = args.index(bstack111lll1l_opy_ (u"ࠪ࠱ࡳ้࠭"))
        args.pop(i+1)
        args.pop(i)
    except Exception as exc:
      logger.error(str(exc))
    config = _prepareconfig(args)
    bstack1l111l11_opy_ = config.args
    bstack1l1lllll1_opy_ = config.invocation_params.args
    bstack1l1lllll1_opy_ = list(bstack1l1lllll1_opy_)
    bstack11l11l1l_opy_ = [os.path.normpath(item) for item in bstack1l111l11_opy_]
    bstack1ll1l_opy_ = [os.path.normpath(item) for item in bstack1l1lllll1_opy_]
    bstack1l1l1ll11_opy_ = [item for item in bstack1ll1l_opy_ if item not in bstack11l11l1l_opy_]
    if bstack111lll1l_opy_ (u"ࠫ࠲࠳ࡣࡢࡥ࡫ࡩ࠲ࡩ࡬ࡦࡣࡵ๊ࠫ") not in bstack1l1l1ll11_opy_:
      bstack1l1l1ll11_opy_.append(bstack111lll1l_opy_ (u"ࠬ࠳࠭ࡤࡣࡦ࡬ࡪ࠳ࡣ࡭ࡧࡤࡶ๋ࠬ"))
    import platform as pf
    if pf.system().lower() == bstack111lll1l_opy_ (u"࠭ࡷࡪࡰࡧࡳࡼࡹࠧ์"):
      from pathlib import PureWindowsPath, PurePosixPath
      bstack1l111l11_opy_ = [str(PurePosixPath(PureWindowsPath(bstack11ll11111_opy_)))
                    for bstack11ll11111_opy_ in bstack1l111l11_opy_]
    if (bstack1ll1ll11_opy_):
      bstack1l1l1ll11_opy_.append(bstack111lll1l_opy_ (u"ࠧ࠮࠯ࡶ࡯࡮ࡶࡓࡦࡵࡶ࡭ࡴࡴࡎࡢ࡯ࡨࠫํ"))
      bstack1l1l1ll11_opy_.append(bstack111lll1l_opy_ (u"ࠨࡖࡵࡹࡪ࠭๎"))
    try:
      from pytest_bdd import reporting
      bstack1lllll1l1_opy_ = True
    except Exception as e:
      pass
    if (not bstack1lllll1l1_opy_):
      bstack1l1l1ll11_opy_.append(bstack111lll1l_opy_ (u"ࠩ࠰ࡴࠬ๏"))
      bstack1l1l1ll11_opy_.append(bstack111lll1l_opy_ (u"ࠪࡴࡾࡺࡥࡴࡶࡢࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡲ࡯ࡹ࡬࡯࡮ࠨ๐"))
    bstack1l1l1ll11_opy_.append(bstack111lll1l_opy_ (u"ࠫ࠲࠳ࡤࡳ࡫ࡹࡩࡷ࠭๑"))
    bstack1l1l1ll11_opy_.append(bstack111lll1l_opy_ (u"ࠬࡩࡨࡳࡱࡰࡩࠬ๒"))
    bstack1l1ll1_opy_ = []
    for spec in bstack1l111l11_opy_:
      bstack1lll1111l_opy_ = []
      bstack1lll1111l_opy_.append(spec)
      bstack1lll1111l_opy_ += bstack1l1l1ll11_opy_
      bstack1l1ll1_opy_.append(bstack1lll1111l_opy_)
    bstack1lll1l1ll_opy_ = True
    bstack1111lll1_opy_ = 1
    if bstack111lll1l_opy_ (u"࠭ࡰࡢࡴࡤࡰࡱ࡫࡬ࡴࡒࡨࡶࡕࡲࡡࡵࡨࡲࡶࡲ࠭๓") in CONFIG:
      bstack1111lll1_opy_ = CONFIG[bstack111lll1l_opy_ (u"ࠧࡱࡣࡵࡥࡱࡲࡥ࡭ࡵࡓࡩࡷࡖ࡬ࡢࡶࡩࡳࡷࡳࠧ๔")]
    bstack1111lll11_opy_ = int(bstack1111lll1_opy_)*int(len(CONFIG[bstack111lll1l_opy_ (u"ࠨࡲ࡯ࡥࡹ࡬࡯ࡳ࡯ࡶࠫ๕")]))
    execution_items = []
    for bstack1lll1111l_opy_ in bstack1l1ll1_opy_:
      for index, _ in enumerate(CONFIG[bstack111lll1l_opy_ (u"ࠩࡳࡰࡦࡺࡦࡰࡴࡰࡷࠬ๖")]):
        item = {}
        item[bstack111lll1l_opy_ (u"ࠪࡥࡷ࡭ࠧ๗")] = bstack1lll1111l_opy_
        item[bstack111lll1l_opy_ (u"ࠫ࡮ࡴࡤࡦࡺࠪ๘")] = index
        execution_items.append(item)
    bstack1llll11l1_opy_ = bstack1l11lll_opy_(execution_items, bstack1111lll11_opy_)
    for execution_item in bstack1llll11l1_opy_:
      bstack1lllllll1_opy_ = []
      for item in execution_item:
        bstack1lllllll1_opy_.append(bstack1lll111l1_opy_(name=str(item[bstack111lll1l_opy_ (u"ࠬ࡯࡮ࡥࡧࡻࠫ๙")]),
                                            target=bstack11l1l1111_opy_,
                                            args=(item[bstack111lll1l_opy_ (u"࠭ࡡࡳࡩࠪ๚")],)))
      for t in bstack1lllllll1_opy_:
        t.start()
      for t in bstack1lllllll1_opy_:
        t.join()
  elif bstack1l11ll1l1_opy_ == bstack111lll1l_opy_ (u"ࠧࡣࡧ࡫ࡥࡻ࡫ࠧ๛"):
    try:
      from behave.__main__ import main as bstack1l11l1_opy_
      from behave.configuration import Configuration
    except Exception as e:
      bstack1ll1111l_opy_(e, bstack111l1l1l1_opy_)
    bstack1lll1111_opy_()
    bstack1lll1l1ll_opy_ = True
    bstack1111lll1_opy_ = 1
    if bstack111lll1l_opy_ (u"ࠨࡲࡤࡶࡦࡲ࡬ࡦ࡮ࡶࡔࡪࡸࡐ࡭ࡣࡷࡪࡴࡸ࡭ࠨ๜") in CONFIG:
      bstack1111lll1_opy_ = CONFIG[bstack111lll1l_opy_ (u"ࠩࡳࡥࡷࡧ࡬࡭ࡧ࡯ࡷࡕ࡫ࡲࡑ࡮ࡤࡸ࡫ࡵࡲ࡮ࠩ๝")]
    bstack1111lll11_opy_ = int(bstack1111lll1_opy_)*int(len(CONFIG[bstack111lll1l_opy_ (u"ࠪࡴࡱࡧࡴࡧࡱࡵࡱࡸ࠭๞")]))
    config = Configuration(args)
    bstack1111ll11l_opy_ = config.paths
    if len(bstack1111ll11l_opy_) == 0:
      import glob
      pattern = bstack111lll1l_opy_ (u"ࠫ࠯࠰࠯ࠫ࠰ࡩࡩࡦࡺࡵࡳࡧࠪ๟")
      bstack111l1111_opy_ = glob.glob(pattern, recursive=True)
      args.extend(bstack111l1111_opy_)
      config = Configuration(args)
      bstack1111ll11l_opy_ = config.paths
    bstack1l111l11_opy_ = [os.path.normpath(item) for item in bstack1111ll11l_opy_]
    bstack1l1111ll_opy_ = [os.path.normpath(item) for item in args]
    bstack111l11l1l_opy_ = [item for item in bstack1l1111ll_opy_ if item not in bstack1l111l11_opy_]
    import platform as pf
    if pf.system().lower() == bstack111lll1l_opy_ (u"ࠬࡽࡩ࡯ࡦࡲࡻࡸ࠭๠"):
      from pathlib import PureWindowsPath, PurePosixPath
      bstack1l111l11_opy_ = [str(PurePosixPath(PureWindowsPath(bstack11ll11111_opy_)))
                    for bstack11ll11111_opy_ in bstack1l111l11_opy_]
    bstack1l1ll1_opy_ = []
    for spec in bstack1l111l11_opy_:
      bstack1lll1111l_opy_ = []
      bstack1lll1111l_opy_ += bstack111l11l1l_opy_
      bstack1lll1111l_opy_.append(spec)
      bstack1l1ll1_opy_.append(bstack1lll1111l_opy_)
    execution_items = []
    for bstack1lll1111l_opy_ in bstack1l1ll1_opy_:
      for index, _ in enumerate(CONFIG[bstack111lll1l_opy_ (u"࠭ࡰ࡭ࡣࡷࡪࡴࡸ࡭ࡴࠩ๡")]):
        item = {}
        item[bstack111lll1l_opy_ (u"ࠧࡢࡴࡪࠫ๢")] = bstack111lll1l_opy_ (u"ࠨࠢࠪ๣").join(bstack1lll1111l_opy_)
        item[bstack111lll1l_opy_ (u"ࠩ࡬ࡲࡩ࡫ࡸࠨ๤")] = index
        execution_items.append(item)
    bstack1llll11l1_opy_ = bstack1l11lll_opy_(execution_items, bstack1111lll11_opy_)
    for execution_item in bstack1llll11l1_opy_:
      bstack1lllllll1_opy_ = []
      for item in execution_item:
        bstack1lllllll1_opy_.append(bstack1lll111l1_opy_(name=str(item[bstack111lll1l_opy_ (u"ࠪ࡭ࡳࡪࡥࡹࠩ๥")]),
                                            target=bstack1lll11l11_opy_,
                                            args=(item[bstack111lll1l_opy_ (u"ࠫࡦࡸࡧࠨ๦")],)))
      for t in bstack1lllllll1_opy_:
        t.start()
      for t in bstack1lllllll1_opy_:
        t.join()
  else:
    bstack1l11ll1l_opy_(bstack11l1ll1ll_opy_)
  if not bstack111ll_opy_:
    bstack11111_opy_()
def browserstack_initialize(bstack11111lll_opy_=None):
  run_on_browserstack(bstack11111lll_opy_, None, True)
def bstack11111_opy_():
  [bstack1l1l11l1l_opy_, bstack111l1ll_opy_] = bstack1ll111l_opy_()
  if bstack1l1l11l1l_opy_ is not None and bstack1l1l1l11l_opy_() != -1:
    sessions = bstack1ll1ll_opy_(bstack1l1l11l1l_opy_)
    bstack111lll1ll_opy_(sessions, bstack111l1ll_opy_)
def bstack1l1ll111_opy_(bstack11lllll_opy_):
    if bstack11lllll_opy_:
        return bstack11lllll_opy_.capitalize()
    else:
        return bstack11lllll_opy_
def bstack11l1l11l_opy_(bstack11lllll1l_opy_):
    if bstack111lll1l_opy_ (u"ࠬࡴࡡ࡮ࡧࠪ๧") in bstack11lllll1l_opy_ and bstack11lllll1l_opy_[bstack111lll1l_opy_ (u"࠭࡮ࡢ࡯ࡨࠫ๨")] != bstack111lll1l_opy_ (u"ࠧࠨ๩"):
        return bstack11lllll1l_opy_[bstack111lll1l_opy_ (u"ࠨࡰࡤࡱࡪ࠭๪")]
    else:
        bstack1l1ll11l1_opy_ = bstack111lll1l_opy_ (u"ࠤࠥ๫")
        if bstack111lll1l_opy_ (u"ࠪࡨࡪࡼࡩࡤࡧࠪ๬") in bstack11lllll1l_opy_ and bstack11lllll1l_opy_[bstack111lll1l_opy_ (u"ࠫࡩ࡫ࡶࡪࡥࡨࠫ๭")] != None:
            bstack1l1ll11l1_opy_ += bstack11lllll1l_opy_[bstack111lll1l_opy_ (u"ࠬࡪࡥࡷ࡫ࡦࡩࠬ๮")] + bstack111lll1l_opy_ (u"ࠨࠬࠡࠤ๯")
            if bstack11lllll1l_opy_[bstack111lll1l_opy_ (u"ࠧࡰࡵࠪ๰")] == bstack111lll1l_opy_ (u"ࠣ࡫ࡲࡷࠧ๱"):
                bstack1l1ll11l1_opy_ += bstack111lll1l_opy_ (u"ࠤ࡬ࡓࡘࠦࠢ๲")
            bstack1l1ll11l1_opy_ += (bstack11lllll1l_opy_[bstack111lll1l_opy_ (u"ࠪࡳࡸࡥࡶࡦࡴࡶ࡭ࡴࡴࠧ๳")] or bstack111lll1l_opy_ (u"ࠫࠬ๴"))
            return bstack1l1ll11l1_opy_
        else:
            bstack1l1ll11l1_opy_ += bstack1l1ll111_opy_(bstack11lllll1l_opy_[bstack111lll1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࠭๵")]) + bstack111lll1l_opy_ (u"ࠨࠠࠣ๶") + (bstack11lllll1l_opy_[bstack111lll1l_opy_ (u"ࠧࡣࡴࡲࡻࡸ࡫ࡲࡠࡸࡨࡶࡸ࡯࡯࡯ࠩ๷")] or bstack111lll1l_opy_ (u"ࠨࠩ๸")) + bstack111lll1l_opy_ (u"ࠤ࠯ࠤࠧ๹")
            if bstack11lllll1l_opy_[bstack111lll1l_opy_ (u"ࠪࡳࡸ࠭๺")] == bstack111lll1l_opy_ (u"ࠦ࡜࡯࡮ࡥࡱࡺࡷࠧ๻"):
                bstack1l1ll11l1_opy_ += bstack111lll1l_opy_ (u"ࠧ࡝ࡩ࡯ࠢࠥ๼")
            bstack1l1ll11l1_opy_ += bstack11lllll1l_opy_[bstack111lll1l_opy_ (u"࠭࡯ࡴࡡࡹࡩࡷࡹࡩࡰࡰࠪ๽")] or bstack111lll1l_opy_ (u"ࠧࠨ๾")
            return bstack1l1ll11l1_opy_
def bstack1l111ll1l_opy_(bstack1111lll1l_opy_):
    if bstack1111lll1l_opy_ == bstack111lll1l_opy_ (u"ࠣࡦࡲࡲࡪࠨ๿"):
        return bstack111lll1l_opy_ (u"ࠩ࠿ࡸࡩࠦࡣ࡭ࡣࡶࡷࡂࠨࡢࡴࡶࡤࡧࡰ࠳ࡤࡢࡶࡤࠦࠥࡹࡴࡺ࡮ࡨࡁࠧࡩ࡯࡭ࡱࡵ࠾࡬ࡸࡥࡦࡰ࠾ࠦࡃࡂࡦࡰࡰࡷࠤࡨࡵ࡬ࡰࡴࡀࠦ࡬ࡸࡥࡦࡰࠥࡂࡈࡵ࡭ࡱ࡮ࡨࡸࡪࡪ࠼࠰ࡨࡲࡲࡹࡄ࠼࠰ࡶࡧࡂࠬ຀")
    elif bstack1111lll1l_opy_ == bstack111lll1l_opy_ (u"ࠥࡪࡦ࡯࡬ࡦࡦࠥກ"):
        return bstack111lll1l_opy_ (u"ࠫࡁࡺࡤࠡࡥ࡯ࡥࡸࡹ࠽ࠣࡤࡶࡸࡦࡩ࡫࠮ࡦࡤࡸࡦࠨࠠࡴࡶࡼࡰࡪࡃࠢࡤࡱ࡯ࡳࡷࡀࡲࡦࡦ࠾ࠦࡃࡂࡦࡰࡰࡷࠤࡨࡵ࡬ࡰࡴࡀࠦࡷ࡫ࡤࠣࡀࡉࡥ࡮ࡲࡥࡥ࠾࠲ࡪࡴࡴࡴ࠿࠾࠲ࡸࡩࡄࠧຂ")
    elif bstack1111lll1l_opy_ == bstack111lll1l_opy_ (u"ࠧࡶࡡࡴࡵࡨࡨࠧ຃"):
        return bstack111lll1l_opy_ (u"࠭࠼ࡵࡦࠣࡧࡱࡧࡳࡴ࠿ࠥࡦࡸࡺࡡࡤ࡭࠰ࡨࡦࡺࡡࠣࠢࡶࡸࡾࡲࡥ࠾ࠤࡦࡳࡱࡵࡲ࠻ࡩࡵࡩࡪࡴ࠻ࠣࡀ࠿ࡪࡴࡴࡴࠡࡥࡲࡰࡴࡸ࠽ࠣࡩࡵࡩࡪࡴࠢ࠿ࡒࡤࡷࡸ࡫ࡤ࠽࠱ࡩࡳࡳࡺ࠾࠽࠱ࡷࡨࡃ࠭ຄ")
    elif bstack1111lll1l_opy_ == bstack111lll1l_opy_ (u"ࠢࡦࡴࡵࡳࡷࠨ຅"):
        return bstack111lll1l_opy_ (u"ࠨ࠾ࡷࡨࠥࡩ࡬ࡢࡵࡶࡁࠧࡨࡳࡵࡣࡦ࡯࠲ࡪࡡࡵࡣࠥࠤࡸࡺࡹ࡭ࡧࡀࠦࡨࡵ࡬ࡰࡴ࠽ࡶࡪࡪ࠻ࠣࡀ࠿ࡪࡴࡴࡴࠡࡥࡲࡰࡴࡸ࠽ࠣࡴࡨࡨࠧࡄࡅࡳࡴࡲࡶࡁ࠵ࡦࡰࡰࡷࡂࡁ࠵ࡴࡥࡀࠪຆ")
    elif bstack1111lll1l_opy_ == bstack111lll1l_opy_ (u"ࠤࡷ࡭ࡲ࡫࡯ࡶࡶࠥງ"):
        return bstack111lll1l_opy_ (u"ࠪࡀࡹࡪࠠࡤ࡮ࡤࡷࡸࡃࠢࡣࡵࡷࡥࡨࡱ࠭ࡥࡣࡷࡥࠧࠦࡳࡵࡻ࡯ࡩࡂࠨࡣࡰ࡮ࡲࡶ࠿ࠩࡥࡦࡣ࠶࠶࠻ࡁࠢ࠿࠾ࡩࡳࡳࡺࠠࡤࡱ࡯ࡳࡷࡃࠢࠤࡧࡨࡥ࠸࠸࠶ࠣࡀࡗ࡭ࡲ࡫࡯ࡶࡶ࠿࠳࡫ࡵ࡮ࡵࡀ࠿࠳ࡹࡪ࠾ࠨຈ")
    elif bstack1111lll1l_opy_ == bstack111lll1l_opy_ (u"ࠦࡷࡻ࡮࡯࡫ࡱ࡫ࠧຉ"):
        return bstack111lll1l_opy_ (u"ࠬࡂࡴࡥࠢࡦࡰࡦࡹࡳ࠾ࠤࡥࡷࡹࡧࡣ࡬࠯ࡧࡥࡹࡧࠢࠡࡵࡷࡽࡱ࡫࠽ࠣࡥࡲࡰࡴࡸ࠺ࡣ࡮ࡤࡧࡰࡁࠢ࠿࠾ࡩࡳࡳࡺࠠࡤࡱ࡯ࡳࡷࡃࠢࡣ࡮ࡤࡧࡰࠨ࠾ࡓࡷࡱࡲ࡮ࡴࡧ࠽࠱ࡩࡳࡳࡺ࠾࠽࠱ࡷࡨࡃ࠭ຊ")
    else:
        return bstack111lll1l_opy_ (u"࠭࠼ࡵࡦࠣࡥࡱ࡯ࡧ࡯࠿ࠥࡧࡪࡴࡴࡦࡴࠥࠤࡨࡲࡡࡴࡵࡀࠦࡧࡹࡴࡢࡥ࡮࠱ࡩࡧࡴࡢࠤࠣࡷࡹࡿ࡬ࡦ࠿ࠥࡧࡴࡲ࡯ࡳ࠼ࡥࡰࡦࡩ࡫࠼ࠤࡁࡀ࡫ࡵ࡮ࡵࠢࡦࡳࡱࡵࡲ࠾ࠤࡥࡰࡦࡩ࡫ࠣࡀࠪ຋")+bstack1l1ll111_opy_(bstack1111lll1l_opy_)+bstack111lll1l_opy_ (u"ࠧ࠽࠱ࡩࡳࡳࡺ࠾࠽࠱ࡷࡨࡃ࠭ຌ")
def bstack1l1l1llll_opy_(session):
    return bstack111lll1l_opy_ (u"ࠨ࠾ࡷࡶࠥࡩ࡬ࡢࡵࡶࡁࠧࡨࡳࡵࡣࡦ࡯࠲ࡸ࡯ࡸࠤࡁࡀࡹࡪࠠࡤ࡮ࡤࡷࡸࡃࠢࡣࡵࡷࡥࡨࡱ࠭ࡥࡣࡷࡥࠥࡹࡥࡴࡵ࡬ࡳࡳ࠳࡮ࡢ࡯ࡨࠦࡃࡂࡡࠡࡪࡵࡩ࡫ࡃࠢࡼࡿࠥࠤࡹࡧࡲࡨࡧࡷࡁࠧࡥࡢ࡭ࡣࡱ࡯ࠧࡄࡻࡾ࠾࠲ࡥࡃࡂ࠯ࡵࡦࡁࡿࢂࢁࡽ࠽ࡶࡧࠤࡦࡲࡩࡨࡰࡀࠦࡨ࡫࡮ࡵࡧࡵࠦࠥࡩ࡬ࡢࡵࡶࡁࠧࡨࡳࡵࡣࡦ࡯࠲ࡪࡡࡵࡣࠥࡂࢀࢃ࠼࠰ࡶࡧࡂࡁࡺࡤࠡࡣ࡯࡭࡬ࡴ࠽ࠣࡥࡨࡲࡹ࡫ࡲࠣࠢࡦࡰࡦࡹࡳ࠾ࠤࡥࡷࡹࡧࡣ࡬࠯ࡧࡥࡹࡧࠢ࠿ࡽࢀࡀ࠴ࡺࡤ࠿࠾ࡷࡨࠥࡧ࡬ࡪࡩࡱࡁࠧࡩࡥ࡯ࡶࡨࡶࠧࠦࡣ࡭ࡣࡶࡷࡂࠨࡢࡴࡶࡤࡧࡰ࠳ࡤࡢࡶࡤࠦࡃࢁࡽ࠽࠱ࡷࡨࡃࡂࡴࡥࠢࡤࡰ࡮࡭࡮࠾ࠤࡦࡩࡳࡺࡥࡳࠤࠣࡧࡱࡧࡳࡴ࠿ࠥࡦࡸࡺࡡࡤ࡭࠰ࡨࡦࡺࡡࠣࡀࡾࢁࡁ࠵ࡴࡥࡀ࠿࠳ࡹࡸ࠾ࠨຍ").format(session[bstack111lll1l_opy_ (u"ࠩࡳࡹࡧࡲࡩࡤࡡࡸࡶࡱ࠭ຎ")],bstack11l1l11l_opy_(session), bstack1l111ll1l_opy_(session[bstack111lll1l_opy_ (u"ࠪࡦࡷࡵࡷࡴࡧࡵࡷࡹࡧࡣ࡬ࡡࡶࡸࡦࡺࡵࡴࠩຏ")]), bstack1l111ll1l_opy_(session[bstack111lll1l_opy_ (u"ࠫࡸࡺࡡࡵࡷࡶࠫຐ")]), bstack1l1ll111_opy_(session[bstack111lll1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷ࠭ຑ")] or session[bstack111lll1l_opy_ (u"࠭ࡤࡦࡸ࡬ࡧࡪ࠭ຒ")] or bstack111lll1l_opy_ (u"ࠧࠨຓ")) + bstack111lll1l_opy_ (u"ࠣࠢࠥດ") + (session[bstack111lll1l_opy_ (u"ࠩࡥࡶࡴࡽࡳࡦࡴࡢࡺࡪࡸࡳࡪࡱࡱࠫຕ")] or bstack111lll1l_opy_ (u"ࠪࠫຖ")), session[bstack111lll1l_opy_ (u"ࠫࡴࡹࠧທ")] + bstack111lll1l_opy_ (u"ࠧࠦࠢຘ") + session[bstack111lll1l_opy_ (u"࠭࡯ࡴࡡࡹࡩࡷࡹࡩࡰࡰࠪນ")], session[bstack111lll1l_opy_ (u"ࠧࡥࡷࡵࡥࡹ࡯࡯࡯ࠩບ")] or bstack111lll1l_opy_ (u"ࠨࠩປ"), session[bstack111lll1l_opy_ (u"ࠩࡦࡶࡪࡧࡴࡦࡦࡢࡥࡹ࠭ຜ")] if session[bstack111lll1l_opy_ (u"ࠪࡧࡷ࡫ࡡࡵࡧࡧࡣࡦࡺࠧຝ")] else bstack111lll1l_opy_ (u"ࠫࠬພ"))
def bstack111lll1ll_opy_(sessions, bstack111l1ll_opy_):
  try:
    bstack1l1lll1l1_opy_ = bstack111lll1l_opy_ (u"ࠧࠨຟ")
    if not os.path.exists(bstack11l1l1ll1_opy_):
      os.mkdir(bstack11l1l1ll1_opy_)
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), bstack111lll1l_opy_ (u"࠭ࡡࡴࡵࡨࡸࡸ࠵ࡲࡦࡲࡲࡶࡹ࠴ࡨࡵ࡯࡯ࠫຠ")), bstack111lll1l_opy_ (u"ࠧࡳࠩມ")) as f:
      bstack1l1lll1l1_opy_ = f.read()
    bstack1l1lll1l1_opy_ = bstack1l1lll1l1_opy_.replace(bstack111lll1l_opy_ (u"ࠨࡽࠨࡖࡊ࡙ࡕࡍࡖࡖࡣࡈࡕࡕࡏࡖࠨࢁࠬຢ"), str(len(sessions)))
    bstack1l1lll1l1_opy_ = bstack1l1lll1l1_opy_.replace(bstack111lll1l_opy_ (u"ࠩࡾࠩࡇ࡛ࡉࡍࡆࡢ࡙ࡗࡒࠥࡾࠩຣ"), bstack111l1ll_opy_)
    bstack1l1lll1l1_opy_ = bstack1l1lll1l1_opy_.replace(bstack111lll1l_opy_ (u"ࠪࡿࠪࡈࡕࡊࡎࡇࡣࡓࡇࡍࡆࠧࢀࠫ຤"), sessions[0].get(bstack111lll1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡢࡲࡦࡳࡥࠨລ")) if sessions[0] else bstack111lll1l_opy_ (u"ࠬ࠭຦"))
    with open(os.path.join(bstack11l1l1ll1_opy_, bstack111lll1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯࠲ࡸࡥࡱࡱࡵࡸ࠳࡮ࡴ࡮࡮ࠪວ")), bstack111lll1l_opy_ (u"ࠧࡸࠩຨ")) as stream:
      stream.write(bstack1l1lll1l1_opy_.split(bstack111lll1l_opy_ (u"ࠨࡽࠨࡗࡊ࡙ࡓࡊࡑࡑࡗࡤࡊࡁࡕࡃࠨࢁࠬຩ"))[0])
      for session in sessions:
        stream.write(bstack1l1l1llll_opy_(session))
      stream.write(bstack1l1lll1l1_opy_.split(bstack111lll1l_opy_ (u"ࠩࡾࠩࡘࡋࡓࡔࡋࡒࡒࡘࡥࡄࡂࡖࡄࠩࢂ࠭ສ"))[1])
    logger.info(bstack111lll1l_opy_ (u"ࠪࡋࡪࡴࡥࡳࡣࡷࡩࡩࠦࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࠥࡨࡵࡪ࡮ࡧࠤࡦࡸࡴࡪࡨࡤࡧࡹࡹࠠࡢࡶࠣࡿࢂ࠭ຫ").format(bstack11l1l1ll1_opy_));
  except Exception as e:
    logger.debug(bstack1llllll1_opy_.format(str(e)))
def bstack1ll1ll_opy_(bstack1l1l11l1l_opy_):
  global CONFIG
  try:
    host = bstack111lll1l_opy_ (u"ࠫࡦࡶࡩ࠮ࡥ࡯ࡳࡺࡪࠧຬ") if bstack111lll1l_opy_ (u"ࠬࡧࡰࡱࠩອ") in CONFIG else bstack111lll1l_opy_ (u"࠭ࡡࡱ࡫ࠪຮ")
    user = CONFIG[bstack111lll1l_opy_ (u"ࠧࡶࡵࡨࡶࡓࡧ࡭ࡦࠩຯ")]
    key = CONFIG[bstack111lll1l_opy_ (u"ࠨࡣࡦࡧࡪࡹࡳࡌࡧࡼࠫະ")]
    bstack1llll111l_opy_ = bstack111lll1l_opy_ (u"ࠩࡤࡴࡵ࠳ࡡࡶࡶࡲࡱࡦࡺࡥࠨັ") if bstack111lll1l_opy_ (u"ࠪࡥࡵࡶࠧາ") in CONFIG else bstack111lll1l_opy_ (u"ࠫࡦࡻࡴࡰ࡯ࡤࡸࡪ࠭ຳ")
    url = bstack111lll1l_opy_ (u"ࠬ࡮ࡴࡵࡲࡶ࠾࠴࠵ࡻࡾ࠼ࡾࢁࡅࢁࡽ࠯ࡤࡵࡳࡼࡹࡥࡳࡵࡷࡥࡨࡱ࠮ࡤࡱࡰ࠳ࢀࢃ࠯ࡣࡷ࡬ࡰࡩࡹ࠯ࡼࡿ࠲ࡷࡪࡹࡳࡪࡱࡱࡷ࠳ࡰࡳࡰࡰࠪິ").format(user, key, host, bstack1llll111l_opy_, bstack1l1l11l1l_opy_)
    headers = {
      bstack111lll1l_opy_ (u"࠭ࡃࡰࡰࡷࡩࡳࡺ࠭ࡵࡻࡳࡩࠬີ"): bstack111lll1l_opy_ (u"ࠧࡢࡲࡳࡰ࡮ࡩࡡࡵ࡫ࡲࡲ࠴ࡰࡳࡰࡰࠪຶ"),
    }
    proxies = bstack1l11111l_opy_(CONFIG, url)
    response = requests.get(url, headers=headers, proxies=proxies)
    if response.json():
      return list(map(lambda session: session[bstack111lll1l_opy_ (u"ࠨࡣࡸࡸࡴࡳࡡࡵ࡫ࡲࡲࡤࡹࡥࡴࡵ࡬ࡳࡳ࠭ື")], response.json()))
  except Exception as e:
    logger.debug(bstack111ll11l1_opy_.format(str(e)))
def bstack1ll111l_opy_():
  global CONFIG
  try:
    if bstack111lll1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩຸࠬ") in CONFIG:
      host = bstack111lll1l_opy_ (u"ࠪࡥࡵ࡯࠭ࡤ࡮ࡲࡹࡩູ࠭") if bstack111lll1l_opy_ (u"ࠫࡦࡶࡰࠨ຺") in CONFIG else bstack111lll1l_opy_ (u"ࠬࡧࡰࡪࠩົ")
      user = CONFIG[bstack111lll1l_opy_ (u"࠭ࡵࡴࡧࡵࡒࡦࡳࡥࠨຼ")]
      key = CONFIG[bstack111lll1l_opy_ (u"ࠧࡢࡥࡦࡩࡸࡹࡋࡦࡻࠪຽ")]
      bstack1llll111l_opy_ = bstack111lll1l_opy_ (u"ࠨࡣࡳࡴ࠲ࡧࡵࡵࡱࡰࡥࡹ࡫ࠧ຾") if bstack111lll1l_opy_ (u"ࠩࡤࡴࡵ࠭຿") in CONFIG else bstack111lll1l_opy_ (u"ࠪࡥࡺࡺ࡯࡮ࡣࡷࡩࠬເ")
      url = bstack111lll1l_opy_ (u"ࠫ࡭ࡺࡴࡱࡵ࠽࠳࠴ࢁࡽ࠻ࡽࢀࡄࢀࢃ࠮ࡣࡴࡲࡻࡸ࡫ࡲࡴࡶࡤࡧࡰ࠴ࡣࡰ࡯࠲ࡿࢂ࠵ࡢࡶ࡫࡯ࡨࡸ࠴ࡪࡴࡱࡱࠫແ").format(user, key, host, bstack1llll111l_opy_)
      headers = {
        bstack111lll1l_opy_ (u"ࠬࡉ࡯࡯ࡶࡨࡲࡹ࠳ࡴࡺࡲࡨࠫໂ"): bstack111lll1l_opy_ (u"࠭ࡡࡱࡲ࡯࡭ࡨࡧࡴࡪࡱࡱ࠳࡯ࡹ࡯࡯ࠩໃ"),
      }
      if bstack111lll1l_opy_ (u"ࠧࡣࡷ࡬ࡰࡩࡏࡤࡦࡰࡷ࡭࡫࡯ࡥࡳࠩໄ") in CONFIG:
        params = {bstack111lll1l_opy_ (u"ࠨࡰࡤࡱࡪ࠭໅"):CONFIG[bstack111lll1l_opy_ (u"ࠩࡥࡹ࡮ࡲࡤࡏࡣࡰࡩࠬໆ")], bstack111lll1l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡡ࡬ࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ࠭໇"):CONFIG[bstack111lll1l_opy_ (u"ࠫࡧࡻࡩ࡭ࡦࡌࡨࡪࡴࡴࡪࡨ࡬ࡩࡷ່࠭")]}
      else:
        params = {bstack111lll1l_opy_ (u"ࠬࡴࡡ࡮ࡧ້ࠪ"):CONFIG[bstack111lll1l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡓࡧ࡭ࡦ໊ࠩ")]}
      proxies = bstack1l11111l_opy_(CONFIG, url)
      response = requests.get(url, params=params, headers=headers, proxies=proxies)
      if response.json():
        bstack11l1llll1_opy_ = response.json()[0][bstack111lll1l_opy_ (u"ࠧࡢࡷࡷࡳࡲࡧࡴࡪࡱࡱࡣࡧࡻࡩ࡭ࡦ໋ࠪ")]
        if bstack11l1llll1_opy_:
          bstack111l1ll_opy_ = bstack11l1llll1_opy_[bstack111lll1l_opy_ (u"ࠨࡲࡸࡦࡱ࡯ࡣࡠࡷࡵࡰࠬ໌")].split(bstack111lll1l_opy_ (u"ࠩࡳࡹࡧࡲࡩࡤ࠯ࡥࡹ࡮ࡲࡤࠨໍ"))[0] + bstack111lll1l_opy_ (u"ࠪࡦࡺ࡯࡬ࡥࡵ࠲ࠫ໎") + bstack11l1llll1_opy_[bstack111lll1l_opy_ (u"ࠫ࡭ࡧࡳࡩࡧࡧࡣ࡮ࡪࠧ໏")]
          logger.info(bstack11ll11l11_opy_.format(bstack111l1ll_opy_))
          bstack111l_opy_ = CONFIG[bstack111lll1l_opy_ (u"ࠬࡨࡵࡪ࡮ࡧࡒࡦࡳࡥࠨ໐")]
          if bstack111lll1l_opy_ (u"࠭ࡢࡶ࡫࡯ࡨࡎࡪࡥ࡯ࡶ࡬ࡪ࡮࡫ࡲࠨ໑") in CONFIG:
            bstack111l_opy_ += bstack111lll1l_opy_ (u"ࠧࠡࠩ໒") + CONFIG[bstack111lll1l_opy_ (u"ࠨࡤࡸ࡭ࡱࡪࡉࡥࡧࡱࡸ࡮࡬ࡩࡦࡴࠪ໓")]
          if bstack111l_opy_!= bstack11l1llll1_opy_[bstack111lll1l_opy_ (u"ࠩࡱࡥࡲ࡫ࠧ໔")]:
            logger.debug(bstack1l11111ll_opy_.format(bstack11l1llll1_opy_[bstack111lll1l_opy_ (u"ࠪࡲࡦࡳࡥࠨ໕")], bstack111l_opy_))
          return [bstack11l1llll1_opy_[bstack111lll1l_opy_ (u"ࠫ࡭ࡧࡳࡩࡧࡧࡣ࡮ࡪࠧ໖")], bstack111l1ll_opy_]
    else:
      logger.warn(bstack1l111l1l_opy_)
  except Exception as e:
    logger.debug(bstack11ll_opy_.format(str(e)))
  return [None, None]
def bstack1llll1111_opy_(url, bstack1l111111_opy_=False):
  global CONFIG
  global bstack1l111ll11_opy_
  if not bstack1l111ll11_opy_:
    hostname = bstack11ll1l11l_opy_(url)
    is_private = bstack1l11llll_opy_(hostname)
    if (bstack111lll1l_opy_ (u"ࠬࡨࡲࡰࡹࡶࡩࡷࡹࡴࡢࡥ࡮ࡐࡴࡩࡡ࡭ࠩ໗") in CONFIG and not CONFIG[bstack111lll1l_opy_ (u"࠭ࡢࡳࡱࡺࡷࡪࡸࡳࡵࡣࡦ࡯ࡑࡵࡣࡢ࡮ࠪ໘")]) and (is_private or bstack1l111111_opy_):
      bstack1l111ll11_opy_ = hostname
def bstack11ll1l11l_opy_(url):
  return urlparse(url).hostname
def bstack1l11llll_opy_(hostname):
  for bstack11l_opy_ in bstack1l11l11ll_opy_:
    regex = re.compile(bstack11l_opy_)
    if regex.match(hostname):
      return True
  return False
def bstack1l11l1ll1_opy_(key_name):
  return True if key_name in threading.current_thread().__dict__.keys() else False