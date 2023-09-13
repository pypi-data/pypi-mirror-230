import logging
import hashlib
import base64
from collections import namedtuple
from datetime import datetime, timezone

PARAM_SEPARATOR = [" ", "="]

logging.getLogger("sh").setLevel(logging.WARNING)


class CommandBase(object):

    enabled_attrs = []
    kind = None

    def get_data_model(self):
        return  namedtuple(self.kind, self.enabled_attrs)

    def get_hash_signature(self, event):
        # we convert to base64 whatever result from sha1 to compress
        # more the result without incrementing collision rate.
        #
        # And we take only the first 10 bytes (out of 20), because
        # according to the birthday paradox, the chance of a collision
        # becomes likely once you generate about the square root of
        # the total number of possibilities.
        #
        # For a 160-bit hash, this would be about 2^80; so let's say
        # that 2^40 should be enough for us.
        # and for an 80-bit hash, it would be about 2^40.
        hashed_data = hashlib.sha1(str(event).encode()).digest()[:10]

        # let's trim the appended '==' from base64
        return base64.b64encode(hashed_data).decode()[:-2]

    def _trim_sensitive_data(self, input_data, sensitive_data, HIDDEN_STR="<hidden>"):
        """Given a string with --some-password=confidential-data 
        or --some-password confidential-data; hides all confidential values. """
        
        _data = input_data
        for separator in PARAM_SEPARATOR:
            _data = _data.split(separator)
            _result = [_data[0]]
            for prev, current in zip(_data, _data[1:]):
                for keyword in sensitive_data:
                    if keyword in prev:
                        current = HIDDEN_STR
                _result.append(current)
            _data = separator.join(_result)
        return _data

    def should_skip_row(self, row):
        return False

    def should_skip_first_row(self):
        return False

    def execute(self):
        data_class = self.get_data_model()
        cmd_data = self._get_cmd()
        data = {
            data_class(**self.parse_params(row))
            for row in cmd_data
        }
        result = {
            row for e, row in enumerate(data)
                if not self.should_skip_row(row)
                    and (self.should_skip_first_row()
                         and e == 1)
        }
        # print("RESULT FROM COMMAND:", result)
        return result