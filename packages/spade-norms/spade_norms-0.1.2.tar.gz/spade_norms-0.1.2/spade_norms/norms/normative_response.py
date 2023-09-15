from .norm_enums import NormativeActionStatus
from .norm import Norm
from ..actions.normative_action import NormativeAction

class NormativeResponse():
    def __init__(self, action: NormativeAction, responseType: NormativeActionStatus = NormativeActionStatus.NOT_REGULATED, norms_following: list = None, norms_breaking : list = None
                , total_reward:float = 0.0, total_penalty: float = 0.0):
        self.action = action
        self.response_type = responseType
        self.norms_following = norms_following if norms_following != None else [] 
        self.norms_breaking = norms_breaking if norms_breaking != None else [] 
        self.total_reward = total_reward
        self.total_penalty = total_penalty

    def add_allowing_norm(self, norm: Norm):
        '''
        Adds a new norm to the response list, updates rewards and computes the response type enum.
        - if no norm has been processed or current status is `ALLOWED`, status will be `ALLOWED`.
        - For any other case, the status will remain the same. I.e: if its `FORBIDDEN` or `INVIOLABLE`
        '''
        self.norms_following.append(norm)
        self.total_reward += norm.reward

        if self.response_type == None or self.response_type == NormativeActionStatus.ALLOWED or self.response_type == NormativeActionStatus.NOT_REGULATED:
            self.response_type = NormativeActionStatus.ALLOWED

    def add_forbidding_norm(self, norm: Norm):
        '''
        Adds a new norm to the response list and computes the response type enum.
        - if there has been a forbidden state for an inviolable norm, status will remain `INVIOLABLE`.
        - if no norm has been processed or current status is FORBIDDEN, status will be FORBIDDEN.
        '''
        self.norms_breaking.append(norm)
        self.total_penalty += norm.penalty

        if norm.inviolable or self.response_type == NormativeActionStatus.INVIOLABLE:
            self.response_type = NormativeActionStatus.INVIOLABLE
        else: # if None, Forbidden or allowed
            self.response_type = NormativeActionStatus.FORBIDDEN


    def __str__(self):
        return '{' +  '\tresponse type: {},\n\norms_complying: {},\n\norms_breaking: {},\n\ttotal_reward: {},\n\ttotal_penalty: {}'.format(self.response_type, self.norms_following, self.norms_breaking, self.total_reward, self.total_penalty)  + '}'