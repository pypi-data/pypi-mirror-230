import json
import uuid
from suanpan.log import logger


class Notification(object):
    def __init__(self, content=None, title='配置项', pin=True, order=' '):
        self.content = content
        self.title = title
        self.pin = pin
        self.order = order
        self._action = 'open-popup-1'
        self._type = 'notification'
        self._id = None
        self._shown = False

    def _message(self):
        return {
            'title': self.title, 'content': self.content, 'id': self._id, 'pin': self.pin, 'order': self.order,
            'action': self._action, 'type': self._type
        }

    def show(self, content=None):
        if self._shown:
            return

        if content is not None:
            self.content = content

        self._id = uuid.uuid4().hex
        msg = self._message()
        self._shown = True
        logger.info(json.dumps(msg).encode("utf-8").decode("unicode_escape"))

    def hide(self):
        if not self._shown:
            return

        msg = self._message()
        msg['delete'] = True
        self._shown = False
        logger.info(json.dumps(msg).encode("utf-8").decode("unicode_escape"))


class NodeBadge(object):
    def __init__(self):
        self._notifications = {}

    def add_notification(self, name, content=None, title='配置项', pin=True, order=' '):
        if name in self._notifications:
            raise Exception('duplicated notification name')

        self._notifications[name] = Notification(content=content, title=title, pin=pin, order=order)

    def show_notification(self, name, content=None):
        n = self._notifications.get(name)
        if not n:
            return

        n.show(content=content)

    def hide_notification(self, name):
        n = self._notifications.get(name)
        if not n:
            return

        n.hide()


node_badge = NodeBadge()
