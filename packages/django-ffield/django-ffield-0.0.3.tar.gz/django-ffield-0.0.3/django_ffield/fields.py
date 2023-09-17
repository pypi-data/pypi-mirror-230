from typing import Any
from django.db.models.base import Model
from django.db.models.fields.files import FieldFile, FileField
from validators import FileTypeValidator,meme_type

from magic import from_buffer
class XFileField(FieldFile):
    def __init__(self, instance: Model, field: FileField, name: str | None) -> None:
        super().__init__(instance, field, name)
    
    @property
    def mime_type(self) -> str:
        """return the mimetype of file

        Returns
        -------
        str
            mimetype : 'image/png'
        """
        mime:str = from_buffer(self.read(2048),mime=True)
        return mime
    
    @property
    def type(self) -> str:
        """return the type of file for example : Video,Image,...

        Returns
        -------
        str
            type of file
        """
        return meme_type(self)[0] # type: ignore
    
    @property
    def format(self) -> str:
        """return subtype of file or extention like png,mp4,pdf,...

        Returns
        -------
        str
            the subtype of file
        """
        return meme_type(self)[1] # type: ignore
    
class MediaField(FileField):
    """This field can accept a list of 'types' as input,
    allowing the user to pass only these specific types to the field.

    Parameters
    ----------
    FileField : Django FileField
         
    """

    def __init__(self,types:list[str]=[], *args: Any, **kwargs: Any) -> None:
        self.types: list[str] = types
        super().__init__(*args, **kwargs)
        
        if self.types:
            self.validators.append(FileTypeValidator(self.types))
        
    attr_class = XFileField