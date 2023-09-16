from typing import Optional

from dockerfile_gen.internal import Instruction, CmdType


class Dockerfile:
    def __init__(self):
        # Excludes "FROM" / base image
        self._instructions: list[Instruction] = []
        self._base_image: Optional[str] = None

    def generate(self) -> str:
        # return Dockerfile payload
        result = []
        if self._base_image:
            result.append(f"FROM {self._base_image}")
        for inst in self._instructions:
            result.extend(inst.format())

        return "\n".join(result)

    def from_(self, base_image: str):
        # Context manager!
        self._base_image = base_image

    def run(self, cmd: CmdType):
        self._instructions.append(Instruction(type="RUN", args=cmd))

    def add(self, src: str, target: str):
        self._instructions.append(Instruction(type="ADD", args=[src, target]))

    def copy(self, src: str, target: str):
        self._instructions.append(Instruction(type="COPY", args=[src, target]))

    def workdir(self, target: str):
        self._instructions.append(Instruction(type="WORKDIR", args=target))

    def entrypoint(self, cmd: CmdType):
        self._instructions.append(Instruction(type="ENTRYPOINT", args=cmd))

    def comment(self, comment: str):
        self._instructions.append(Instruction(type="_COMMENT", comment=comment))

    def blank(self):
        self._instructions.append(Instruction(type="_BLANK"))
