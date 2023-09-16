from enum import Enum
from .norm_enums import NormType, NormIssuer
from typing import Callable

class Norm():
    def __init__(self ,name: str, norm_type: NormType, condition_fn: Callable, activation_fn: Callable = None, 
                is_active: bool = True, reward_cb: Callable = None, penalty_cb: Callable = None, roles: list = [], 
                domain: Enum = 0, inviolable: bool = True, issuer: NormIssuer = NormIssuer.ORGANIZATION):
        '''
        Creates an object of type norm given a norm `Name`, `NormType`, and a pointer to a `condition function`. 
        By default, if no furtherinformation is provided, norms will be `INVIOLABLE` and will affect all agents.
        '''
        self.name = name
        self.norm_type = norm_type
        self.condition_fn = condition_fn
        #self.activation_fn = activation_fn
        #self.is_active = is_active
        self.reward_cb = reward_cb
        self.penalty_cb = penalty_cb
        self.roles = roles
        self.domain = domain
        self.inviolable = inviolable
        self.issuer = issuer

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Norm) and self.name == other.name and self.norm_type == other.norm_type