from .scriptinfo import *
from .events import *
from .styles import *
from .common.errors import Errors


class Ass:
    def __init__(self):
        self.script_info: ScriptInfo = ScriptInfo()
        self.styles: Styles = Styles()
        self.events: Events = Events()

        self.__parser_status: ScriptInfo | Styles | Events = self.script_info
        self.__parser_pos_name: str = ''

    def parse(self, ass_str: str) -> Errors:
        err: Errors = Errors()
        ass_str_lines = ass_str.split('\n')
        for line, ass_str_line in enumerate(ass_str_lines):
            line_err = self.parse_line(ass_str_line)
            line_err.pos(f'Line{line + 1}')
            err += line_err
        return err

    def parse_line(self, ass_str: str) -> Errors:
        err: Errors = Errors()
        ass_str = ass_str.lstrip()
        if len(ass_str) == 0:  # 空行
            return err
        if ass_str.startswith('['):
            ass_str_lower = ass_str.lower()
            if ass_str_lower.startswith(EVENTS_PART_TITLE.lower(), 1):
                self.__parser_status = self.events
                self.__parser_pos_name = 'event'
            elif ass_str_lower.startswith(STYLES_PART_TITLE.lower(), 1):
                self.__parser_status = self.styles
                self.__parser_pos_name = 'style'
            elif ass_str_lower.startswith(SCRIPT_INFO_PART_TITLE.lower(), 1):
                self.__parser_status = self.script_info
                self.__parser_pos_name = 'script_info'
        else:
            err += self.__parser_status.parse(ass_str)
            err.pos(self.__parser_pos_name)
        return err

    def dump(self):
        script_info_lines, script_info_errs = self.script_info.dump()
        styles_lines, styles_errs = self.styles.dump()
        events_lines, events_errs = self.events.dump()
        styles_errs.pos('style')
        events_errs.pos('event')
        lines = script_info_lines + [''] + styles_lines + [''] + events_lines
        script_info_errs += styles_errs + events_errs
        return lines, script_info_errs
