"""
Common code used in multiple modules.
"""


class CommonException(Exception):
    description = "PycoBaseError"
    errno = 40000
    error_msg = "customized details of error message"

    def __init__(self, error_msg=error_msg, **kwargs):
        self.error_msg = error_msg
        self.errno = kwargs.pop("errno", self.errno)
        self._kwargs = kwargs

    def to_dict(self):
        ## v3
        return dict(
            errno=self.errno,
            error_msg=self.error_msg,
            error_kws=self._kwargs
        )
