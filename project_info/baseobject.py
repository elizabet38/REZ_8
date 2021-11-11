from loguru import logger
from utils import set_source


class BaseAttribute(object):
    def __init__(self, init_dict=None, update_if_exists=True, default_value_policy='last', default_value=None):
        if init_dict is None:
            init_dict = {}
        self.container = init_dict
        self.update_if_exists = update_if_exists
        self.default_value_policy = default_value_policy

        self.default_value = default_value

    def __call__(self, item=None):
        if item is None:
            return self.default_value
        else:
            return self.container[item]

    def __getitem__(self, item):
        return self.container[item]

    def __setitem__(self, key, value):
        self.container[key] = value
        if self.default_value_policy == 'last':
            self.default_value = value
        else:
            raise NotImplementedError

    def get_dict(self):
        return self.container


class BaseObject(object):
    def __init__(self, **kwargs):
        self.update_source = None
        self.set_kwargs(**kwargs)

    def __setattr__(self, key, value):
        if key == 'update_source':
            super.__setattr__(self, key, value)
        elif self.update_source is None:
            super.__setattr__(self, key, value)
        else:
            if hasattr(self, key):
                updating_attr = self.__getattribute__(key)
                if not isinstance(updating_attr, BaseAttribute):
                    super(BaseObject, self).__setattr__(
                        key,
                        BaseAttribute(
                            init_dict={'null': updating_attr, self.update_source: value},
                            default_value=value,
                        ),
                    )
                updating_attr[self.update_source] = value
            else:
                super(BaseObject, self).__setattr__(
                    key,
                    BaseAttribute(
                            init_dict={self.update_source: value},
                            default_value=value,
                        ),
                    )

    @set_source('kwargs')
    def set_kwargs(self, **kwargs):
        if 'source' in kwargs:
            self.update_source = kwargs['source']
        for name, item in kwargs.items():
            self.__setattr__(name, item)

    def get_info(self):
        for attr in self.__dict__.keys():
            try:
                logger.debug('\t Attribute name: {0}\n\t\t Default value: {1}\n\t\t Dict: {2}'.format(
                    attr, self.__getattribute__(attr)(), self.__getattribute__(attr).get_dict()),
                )
            except TypeError:
                logger.debug('\t Attribute name: {0}\n\t\t Value: {1}'.format(attr, self.__getattribute__(attr)))
