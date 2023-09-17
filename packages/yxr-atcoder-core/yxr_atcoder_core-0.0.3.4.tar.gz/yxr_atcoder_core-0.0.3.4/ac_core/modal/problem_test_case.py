from dataclasses import dataclass


@dataclass
class ProblemTestCase():
  title: str
  input: str = ''
  output: str = ''