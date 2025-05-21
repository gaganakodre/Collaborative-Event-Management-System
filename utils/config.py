from dataclasses import dataclass

@dataclass
class Config:
    host: str = "localhost"
    port: int = 5432
    database: str = "Collaborative_Event_Management_System"
    user: str = "postgres"
    password: str = "12345678"
