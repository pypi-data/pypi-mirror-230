from .create_group_calls import CreateGroupCall
from .discard_group_calls import DiscardGroupCall
from .functions import CallsFunctions
from .get_group_calls import GetGroupCall
from .telegram import TeleAPI
from .thumbnail import ThumbnailSong
from .title_group_calls import EditTitileGroupCall
from .tools import Tools
from .youtube import YouTubeAPI


class Calls(
    CallsFunctions,
    CreateGroupCall,
    DiscardGroupCall,
    EditTitileGroupCall,
    GetGroupCall,
    TeleAPI,
    ThumbnailSong,
    Tools,
    YouTubeAPI,
):
    pass
