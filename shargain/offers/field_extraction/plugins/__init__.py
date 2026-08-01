from .core_fields import core_fields
from .olx_apartment import olx_apartment
from .otodom_apartment import otodom_apartment

registered_plugins = [core_fields, olx_apartment, otodom_apartment]
