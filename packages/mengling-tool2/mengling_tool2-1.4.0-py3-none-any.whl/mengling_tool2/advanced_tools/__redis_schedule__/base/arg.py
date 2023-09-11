import json


class Arg:
    def __init__(self, txt):
        dt = json.loads(txt)
        self.week = dt['week']
        self.reload = dt.get('reload', False)
        self.max_error_num = dt.get('max_error_num', 3)
        self.emails = dt.get('emails', ["1321443305@qq.com"])
        self.error_week = dt.get('error_week', 3600)
        self.max_run_week = dt.get('max_run_week', 3600)
        self.stop = dt.get('stop', False)

    def get(self):
        return {
            'stop': self.stop,
            'week': self.week,
            'reload': self.reload,
            'max_error_num': self.max_error_num,
            'emails': self.emails,
            'error_week': self.error_week,
            'max_run_week': self.max_run_week,
        }
