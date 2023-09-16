from typing import List, cast

from .perception import Perception
from .content_type import MessageContentType, MessageContentSimpleType, MessageContentBaseType


class Message(Perception):
    '''
    This class specifies a wrapper for a message that is sent to a multiple recipients, and its metadata.

    * The content is specified by the `content` field. This field's type is `MessageContentType`.
    * The recipients are specified by the `recipient_ids` field. This field's type is `List[str]`.
    * The sender is specified by the `sender_id` field. This field's type is `str`.
    '''
    def __init__(self, content: MessageContentType, sender_id: str, recipient_ids: List[str]=[]) -> None:
        assert content is not None
        assert isinstance(content, MessageContentBaseType)
        assert sender_id is not None
        assert isinstance(sender_id, str)
        assert recipient_ids is not None

        self.__content: MessageContentType = content
        self.__sender_id: str = sender_id
        self.__recipient_ids: List[str] = recipient_ids

    def get_content(self) -> MessageContentType:
        '''
        Returns the content of the message as a `MessageContentType`.
        '''
        return self.__content

    def get_sender_id(self) -> str:
        '''
        Returns the sender's ID as a `str`.
        '''
        return self.__sender_id

    def get_recipients_ids(self) -> List[str]:
        '''
        Returns the recipients' IDs as a `List[str]`.

        In case this `Message` is a `BccMessage`, this method returns a `List[str]`containing only one ID.
        '''
        return self.__recipient_ids

    def override_recipients(self, recipient_ids: List[str]) -> None:
        '''
        WARNING: this method needs to be public, but it is not part of the public API.
        '''
        self.__recipient_ids = recipient_ids


class BccMessage(Message):
    '''
    This class specifies a wrapper for a message that is sent to a single recipient, and its metadata.

    * The content is specified by the `content` field. This field's type is `MessageContentType`.
    * The recipient is specified by the `recipient_id` field. This field's type is `str`.
    * The sender is specified by the `sender_id` field. This field's type is `str`.
    '''
    def __init__(self, content: MessageContentType, sender_id: str, recipient_id: str) -> None:
        assert content is not None

        super(BccMessage, self).__init__(content=self.__deep_copy_content(content), sender_id=sender_id, recipient_ids=[recipient_id])

    def __deep_copy_content(self, content: MessageContentType) -> MessageContentType:
        # The content is deep-copied to avoid that the same object is shared by multiple `BccMessage` instances.

        assert content is not None

        if isinstance(content, MessageContentSimpleType) or isinstance(content, bytes):
            return content
        elif isinstance(content, list):
            return [self.__deep_copy_content(element) for element in content]
        elif all([isinstance(key, MessageContentSimpleType) for key in content.keys()]) and all([isinstance(value, MessageContentBaseType) for value in content.values()]):
            return {cast(MessageContentSimpleType, self.__deep_copy_content(key)): self.__deep_copy_content(value) for key, value in content.items()}
        else:
            raise ValueError("Invalid content type: {}. The content of a message must be of type `MessageContentType`, including recursive content.".format(type(content)))

    def __str__(self) -> str:
        return "message:(from: {}, content: {})".format(self.get_sender_id(), self.get_content())
