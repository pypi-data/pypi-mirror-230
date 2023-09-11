from ssttkkl_nonebot_utils.requires import silently_requires

silently_requires("nonebot_plugin_gocqhttp_cross_machine_upload_file")

from nonebot_plugin_gocqhttp_cross_machine_upload_file import upload_file

__all__ = ("upload_file",)
