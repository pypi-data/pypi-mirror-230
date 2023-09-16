import dataclasses
from typing import Optional, Union, List
import json

CmdType = Union[str, List[str]]


@dataclasses.dataclass
class Instruction:
    type: str
    args: Optional[CmdType] = None
    comment: Optional[str] = None

    def format(self) -> List[str]:
        if self.type == '_BLANK':
            return ['']
        result = []
        if self.comment is not None:
            result.append(f'# {self.comment}')
        if self.type == '_COMMENT':
            return result
        if self.args is None:
            result.append(f'{self.type}')
        else:
            result.append(f'{self.type} {json.dumps(self.args) if not isinstance(self.args, str) else self.args}')
        return result
