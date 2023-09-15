# coding=utf-8
from __future__ import absolute_import, print_function

import inspect
from unittest import mock

from suanpan import error
from suanpan.log import logger
from suanpan.objects import HasName
from suanpan.app import MessageHandler
from suanpan.node import node


class BaseApp(HasName):
    def __init__(self):
        self._auto_in = None
        self._auto_out = None
        self._auto_param = None

    def __call__(self, *args, **kwargs):
        raise NotImplementedError("Method not implemented!")

    def start(self, *args, **kwargs):  # pylint: disable=unused-argument
        logger.info(f"Suanpan component {self.name} start...")

    def use(self, handlerClass):
        if inspect.isclass(handlerClass) and issubclass(handlerClass, MessageHandler):
            handler = handlerClass()
        elif isinstance(handlerClass, MessageHandler):
            handler = handlerClass
        else:
            raise error.AppError(f"can't use {handlerClass}")

        for arg in handler.inputs:
            self.input(arg)
        for arg in handler.outputs:
            self.output(arg)
        for arg in handler.params:
            self.param(arg)

        handler.init_params()
        self.beforeInit(handler.beforeInit)
        self.afterInit(handler.afterInit)
        self.beforeCall(handler.beforeCall)
        self.afterCall(handler.afterCall)

        self(handler.run)
        handler.initialize()

    def loadNodeArgs(self, funcOrApp=None, *, autoIn=True, autoOut=True, autoParam=True):
        self._auto_in = autoIn
        self._auto_out = autoOut
        self._auto_param = autoParam
        self.beforeInit(self._load_node_info)

        def decorator(func2):
            # func2 is main message loop function
            self(func2)
            return self

        if funcOrApp is not None:
            # loadNodeArgs with no args
            self(funcOrApp)
            return self
        else:
            # loadNodeArgs with args
            return decorator

    def _load_node_info(self):
        logger.debug('auto load node args and params')
        if self._auto_in:
            for inarg in node.inargs:
                self.input(inarg)
        if self._auto_out:
            for outarg in node.outargs:
                self.output(outarg)
        if self._auto_param:
            for paramarg in node.paramargs:
                self.param(paramarg)

    @property
    def trigger(self):
        raise NotImplementedError(f"{self.name} not support trigger")

    def input(self, argument):
        raise NotImplementedError("Method not implemented!")

    def output(self, argument):
        raise NotImplementedError("Method not implemented!")

    def param(self, argument):
        raise NotImplementedError("Method not implemented!")

    def column(self, argument):
        raise NotImplementedError("Method not implemented!")

    def beforeInit(self, hook):
        raise NotImplementedError("Method not implemented!")

    def afterInit(self, hook):
        raise NotImplementedError("Method not implemented!")

    def beforeCall(self, hook):
        raise NotImplementedError("Method not implemented!")

    def afterCall(self, hook):
        raise NotImplementedError("Method not implemented!")

    def beforeExit(self, hook):
        raise NotImplementedError("Method not implemented!")

    def load(self, *args, **kwargs):
        raise NotImplementedError(f"{self.name} not support load")

    def save(self, *args, **kwargs):
        raise NotImplementedError(f"{self.name} not support save")

    def send(self, *args, **kwargs):
        raise NotImplementedError(f"{self.name} not support send")

    @property
    def args(self):
        raise NotImplementedError(f"{self.name} not support args")

    @property
    def vars(self):
        raise NotImplementedError(f"{self.name} not support args")

    def title(self, title):  # pylint: disable=unused-argument
        return self

    @property
    def modules(self):
        return mock.MagicMock()
