"""
This type stub file was generated by pyright.
"""

from . import base, mixins
from .photo_size import PhotoSize

class VideoNote(base.TelegramObject, mixins.Downloadable):
    """
    This object represents a video message (available in Telegram apps as of v.4.0).

    https://core.telegram.org/bots/api#videonote
    """
    file_id: base.String = ...
    file_unique_id: base.String = ...
    length: base.Integer = ...
    duration: base.Integer = ...
    thumb: PhotoSize = ...
    file_size: base.Integer = ...

