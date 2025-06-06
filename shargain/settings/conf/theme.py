from django.utils.translation import gettext_lazy as _

JAZZMIN_SETTINGS = {
    "site_brand": "Shargain",
    "site_title": "Shargain",
    "site_header": "Shargain",
    "welcome_sign": _("Snap bargain with Shargain"),
    "language_chooser": True,
    "navigation_expanded": False,
    "icons": {
        "accounts": "fas fa-cog",
    },
    "custom_links": {
        "accounts": [
            {
                "name": _("Groups"),
                "url": "admin:auth_group_changelist",
                "permissions": ["auth.view_group"],
                "icon": "fas fa-users",
            },
        ],
    },
    "hide_models": [],
    "related_modal_active": True,
    "default_icon_children": "fas fa-chevron-right",
    "show_ui_builder": True,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-gray",
    "accent": "accent-lightblue",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": False,
    # "sidebar": "sidebar-light-danger", # noqa: ERA001
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": True,
    "sidebar_nav_flat_style": False,
    "theme": "cyborg",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-outline-primary",
        "secondary": "btn-outline-secondary",
        "info": "btn-outline-info",
        "warning": "btn-outline-warning",
        "danger": "btn-outline-danger",
        "success": "btn-outline-success",
    },
    "actions_sticky_top": True,
}
