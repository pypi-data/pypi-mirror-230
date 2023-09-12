from enum import Enum
from typing import SupportsIndex

from easyass.events.text import Text

from easyass.common.asstypes import AssTime
from easyass.common.errors import Errors


class EventTypes(Enum):
    dialogue = 'Dialogue'
    comment = 'Comment'
    picture = 'Picture'
    sound = 'Sound'
    movie = 'Movie'
    command = 'Command'


class Events(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_format: EventFormat = EventFormat()

    def parse(self, ass_str: str) -> Errors:
        """
        解析事件字符串生成事件数组

        参数：
            ass_str: 需要解析的事件字符串，含有多条事件
        返回值：
            解析的时候发生的错误
        """
        err = Errors()
        ass_line = ass_str.split(':', 1)
        if len(ass_line) != 2:
            return err.error(f'Fail to parse `{ass_str}` as Styles. ')
        title = ass_line[0].strip()
        if title == FORMAT_LINE_TITLE:
            self.event_format = EventFormat()
            format_err = self.event_format.parse(ass_str)
            format_err.pos('format')
            err += format_err
        elif title == str(EventTypes.dialogue.value):
            if self.event_format is ...:
                return err.error('`Format` line is missing. ')
            event_item = EventItem()
            style_err = event_item.parse(ass_str, self.event_format)
            style_err.pos('item')
            err += style_err
            self.append(event_item)
        return err

    def dump(self) -> (list[str], Errors):
        """
        将当前事件数组格式化为ass文本

        返回值：
            ass 文本数组
            格式化时发生的错误
        """
        errors: Errors = Errors()
        dump_lines: list[str] = [
            '[{}]'.format(EVENTS_PART_TITLE)
        ]
        format_line, format_err = self.event_format.dump()  # format 行
        format_err.pos('format')
        dump_lines += format_line
        errors += format_err

        for index, item in enumerate(self):  # item 行
            item_line, item_error = item.dump(self.event_format)
            item_error.pos(f'item:{index}')
            dump_lines += item_line
            errors += item_error
        return dump_lines, errors

    def append(self, *args, **kwargs) -> None:
        """
        向事件列表末尾追加一个事件对象 EventItem

        1. 当参数只有一个时，参数类型必须为 EventItem 对象；
        2. 有多个参数时，将根据参数构造 EventItem 对象，具体参数如下：
            参数：
                event_type: EventTypes 事件类型，枚举
            关键字参数：
                Marked: int 是否已标识
                Layer: int 图层 大的置于顶层
                Start: AssTime 开始时间
                End: AssTime 结束时间
                Style: str 使用的样式名称 可选
                Name: str 角色名 可选
                MarginL: int 左边距覆写值 px 可选
                MarginR: int 右边距覆写值 px 可选
                MarginV: int 垂直边距覆写值 px 可选
                Effect: str 过渡效果 (暂不做特殊支持) 可选
                Text: Text 文本
        """
        if len(args) == 1 and len(kwargs) == 0 and isinstance(args[0], EventItem):
            super().append(args[0])
        else:
            super().append(EventItem(*args, **kwargs))

    def insert(self, index: SupportsIndex, *args, **kwargs) -> None:
        """
        向事件列表中插入一个事件对象 EventItem

        1. 当参数只有两个时，具体参数如下；
            参数：
                index: 插入位置
                event_item: 需要插入的 EventItem 对象
        2. 有三个及以上个参数时，将根据参数构造 EventItem 对象，具体参数如下：
            参数：
                index: 插入位置
                event_type: EventTypes 事件类型，枚举
            关键字参数：
                Marked: int 是否已标识
                Layer: int 图层 大的置于顶层
                Start: AssTime 开始时间
                End: AssTime 结束时间
                Style: str 使用的样式名称 可选
                Name: str 角色名 可选
                MarginL: int 左边距覆写值 px 可选
                MarginR: int 右边距覆写值 px 可选
                MarginV: int 垂直边距覆写值 px 可选
                Effect: str 过渡效果 (暂不做特殊支持) 可选
                Text: Text 文本
        """
        if len(args) == 1 and len(kwargs) == 0 and isinstance(args[0], EventItem):
            super().insert(index, args[0])
        else:
            super().insert(index, EventItem(*args, **kwargs))


class EventFormat(list):
    def __init__(self, *args):
        super().__init__(*args)
        if not len(args):
            self.extend(EVENT_ATTR_DEF.keys())

    def parse(self, ass_str: str) -> Errors:
        err = Errors()
        self.clear()
        ass_line = ass_str.split(':', 1)
        if len(ass_line) != 2 or ass_line[0].strip() != FORMAT_LINE_TITLE:
            return err.error(f'Fail to parse `{ass_str}` as event format. ')
        style_attrs = ass_line[1].split(',')
        for event_attr in style_attrs:
            event_attr = event_attr.strip()
            if event_attr not in EVENT_ATTR_DEF:
                return err.error(f'Unknown event attribute `{event_attr}`. ')
            self.append(event_attr)
        return err

    def dump(self) -> (list[str], Errors):
        format_line = FORMAT_LINE_TITLE + ':' + ','.join(self)
        return [format_line], Errors()


class EventItem:
    def __init__(self, event_type: EventTypes = ..., **kwargs):
        """
        ass事件项
        可以通过参数指定初始值

        参数：
            event_type: EventTypes 事件类型，枚举
        关键字参数：
            Marked: int 是否已标识
            Layer: int 图层 大的置于顶层
            Start: AssTime 开始时间
            End: AssTime 结束时间
            Style: str 使用的样式名称 可选
            Name: str 角色名 可选
            MarginL: int 左边距覆写值 px 可选
            MarginR: int 右边距覆写值 px 可选
            MarginV: int 垂直边距覆写值 px 可选
            Effect: str 过渡效果 (暂不做特殊支持) 可选
            Text: Text 文本
        """
        self.event_attrs = {attr_name: attr_info[1] for attr_name, attr_info in EVENT_ATTR_DEF.items()}
        self.event_type: EventTypes = event_type
        for key, value in kwargs.items():  # 支持构造时传初始值
            if key in self.event_attrs:
                self.event_attrs[key] = EVENT_ATTR_DEF[key][0](value)

    def parse(self, ass_str: str, event_format: EventFormat) -> Errors:
        err = Errors()
        ass_line = ass_str.split(':', 1)
        if len(ass_line) != 2:
            return err.error(f'Fail to parse `{ass_str}` as style values. ')
        # 解析类型
        event_type = ass_line[0].strip()
        if EventTypes(event_type) not in EventTypes:
            return err.error(f'Unknown event type `{event_type}`. ')
        self.event_type = EventTypes(event_type)

        # 解析属性
        event_values = ass_line[1].split(',', len(event_format) - 1)
        if len(event_values) < len(event_format):
            return err.error(f'`Styles` line does not match `Format` line. ')
        for index, style_attr in enumerate(event_format):
            try:
                self.event_attrs[style_attr] = \
                    EVENT_ATTR_DEF[style_attr][0](event_values[index])
            except Exception as exception:
                return err.error(f'Could not parse `{event_values[index]}` '
                                 f'as `{style_attr}`. Exception: {exception}. ')
        return err

    def dump(self, style_format: EventFormat) -> (list[str], Errors):
        err = Errors()
        style_values = []
        if self.event_type is ...:
            return [], err.error('`event_type` must be specified')
        for style_attr in style_format:
            if self.event_attrs[style_attr] is None:
                err.error(f'Style `{style_attr}` not specified. ')
            else:
                style_values.append(str(self.event_attrs[style_attr]))

        events_line = self.event_type.value + ':' + ','.join(style_values)
        return [events_line], err

    def __getattr__(self, attribute):
        if attribute in self.event_attrs:
            return self.event_attrs[attribute]
        raise AttributeError(attribute)

    def __setattr__(self, key, value):
        if key in self.__dict__.get('event_attrs', {}):
            self.__dict__['event_attrs'][key] = EVENT_ATTR_DEF[key][0](value)
        else:
            super().__setattr__(key, value)


EVENTS_PART_TITLE = 'Events'
FORMAT_LINE_TITLE = 'Format'
EVENT_ATTR_DEF = {
    'Marked': (int, 0),  # 是否已标识
    'Layer': (int, 0),  # 图层 大的置于顶层
    'Start': (AssTime, None),  # 开始时间
    'End': (AssTime, None),  # 结束时间
    'Style': (str, 'default'),  # 使用的样式名称
    'Name': (str, ''),  # 角色名
    'MarginL': (int, 0),  # 左边距覆写值 px
    'MarginR': (int, 0),  # 右边距覆写值 px
    'MarginV': (int, 0),  # 垂直边距覆写值 px
    'Effect': (str, ''),  # 过渡效果 (暂不做特殊支持
    'Text': (Text, Text()),  # 文本
}


__all__ = (
    'Events',
    'EventFormat',
    'EventItem',
    'EventTypes',
    'EVENTS_PART_TITLE',
    'FORMAT_LINE_TITLE',
    'EVENT_ATTR_DEF',
)
