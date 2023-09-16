from .norm_enums import NormativeActionStatus
from .norm import Norm
from ..actions.normative_action import NormativeAction

class NormativeResponse():
    def __init__(self, action: NormativeAction, responseType: NormativeActionStatus = NormativeActionStatus.NOT_REGULATED, norms_allowing: list = None, norms_forbidding : list = None):
        self.action = action
        self.response_type = responseType
        self.norms_allowing = norms_allowing if norms_allowing != None else [] 
        self.norms_forbidding = norms_forbidding if norms_forbidding != None else [] 

    def add_allowing_norm(self, norm: Norm):
        '''
        Adds a new norm to the response list, updates rewards and computes the response type enum.
        - if no norm has been processed or current status is `ALLOWED`, status will be `ALLOWED`.
        - For any other case, the status will remain the same. I.e: if its `FORBIDDEN` or `INVIOLABLE`
        '''
        self.norms_allowing.append(norm)

        if self.response_type == None or self.response_type == NormativeActionStatus.ALLOWED or self.response_type == NormativeActionStatus.NOT_REGULATED:
            self.response_type = NormativeActionStatus.ALLOWED

    def add_forbidding_norm(self, norm: Norm):
        '''
        Adds a new norm to the response list and computes the response type enum.
        - if there has been a forbidden state for an inviolable norm, status will remain `INVIOLABLE`.
        - if no norm has been processed or current status is FORBIDDEN, status will be FORBIDDEN.
        '''
        self.norms_forbidding.append(norm)

        if norm.inviolable or self.response_type == NormativeActionStatus.INVIOLABLE:
            self.response_type = NormativeActionStatus.INVIOLABLE
        else: # if None, Forbidden or allowed
            self.response_type = NormativeActionStatus.FORBIDDEN


    def __str__(self):
        return '{' +  '\tresponse type: {},\nnorms_complying: {},\nnorms_breaking: {}'.format(self.response_type, self.norms_allowing, self.norms_forbidding)  + '}'