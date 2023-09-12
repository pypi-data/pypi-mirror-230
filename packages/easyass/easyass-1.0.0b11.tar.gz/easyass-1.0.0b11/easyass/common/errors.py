class Errors(list):
    """
    错误列表
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def error(self, message: str):
        self.append({'level': 'error', 'pos_stack': [], 'message': message})
        return self

    def warn(self, message: str):
        self.append({'level': 'warn', 'pos_stack': [], 'message': message})
        return self

    def pos(self, pos: str):
        for item in self:
            item['pos_stack'].append(pos)

    def __str__(self):
        ret = ''
        for item in self:
            ret += '[{}][{}] {}\n'.format(item["level"], ':'.join(reversed(item['pos_stack'])), item["message"])
        return ret


__all__ = (
    'Errors',
)
