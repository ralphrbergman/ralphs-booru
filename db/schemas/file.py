from apiflask import Schema
from apiflask.fields import File, List
from apiflask.validators import FileType, Length

class FileIn(Schema):
    files = List(File(required = True, validate = [
        FileType([
            '.gif',
            '.jpg',
            '.jpeg',
            '.mp3',
            '.mp4',
            '.png',
            '.webm',
            '.webp'
        ]) 
    ]),
        validate = [ Length(min = 1, max = 10) ]
    )
