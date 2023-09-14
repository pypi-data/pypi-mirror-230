from dataclasses import dataclass


@dataclass
class Config:
    minimum_minutes_between_services: int = 5
