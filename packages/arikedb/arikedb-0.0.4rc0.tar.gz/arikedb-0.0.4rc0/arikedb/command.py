from enum import Enum


class Command(Enum):
    SET = "SET"
    SET_EVENT = "SET_EVENT"
    GET = "GET"
    PGET = "PGET"
    SUBSCRIBE = "SUBSCRIBE"
    PSUBSCRIBE = "PSUBSCRIBE"
    ADD_ROLE = "ADD_ROLE"
    ADD_USER = "ADD_USER"
    DEL_ROLE = "DEL_ROLE"
    DEL_USER = "DEL_USER"
    SHOW = "SHOW"
    ADD_DATABASE = "ADD_DATABASE"
    DEL_DATABASE = "DEL_DATABASE"
