# Abstract Message

## Usage:
    
```python
from sms_message_local.Message import Message

class SpecialMessage(Message):
    def __init__(self, message_content: str, message_importance: int):
        super().__init__(message_content, message_importance)  # now you got self.message_content and self.message_importance

    def send(self, recipient: str):
        print("Message sent to " + recipient)

    def was_read(self):
        return True

    def importance(self):
        return 5

    def display(self):
        print("Message displayed")

  ```