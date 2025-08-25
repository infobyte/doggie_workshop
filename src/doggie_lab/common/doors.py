from dataclasses import dataclass


@dataclass
class DoorsStatus:
    fr: bool
    fl: bool
    rr: bool
    rl: bool
