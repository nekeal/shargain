from .core_fields import core_fields
from .olx import olx
from .olx_apartment import olx_apartment
from .olx_delivery import olx_delivery
from .otodom import otodom
from .otodom_apartment import otodom_apartment

registered_plugins = [core_fields, olx_delivery, olx_apartment, otodom_apartment, olx, otodom]
