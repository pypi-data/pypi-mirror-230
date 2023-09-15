from ..norms.normative_response import NormativeResponse
from ..norms.norm_enums import NormativeActionStatus
from spade.agent import Agent
import random

class NormativeReasoningEngine():
    def __init__(self):
        pass

    def inference(self, agent:Agent, norm_response: NormativeResponse):
        '''
        This function allows the agent to reason about whether to perform an action or not.
        You can override this method to change this behaviour.
        '''
        if norm_response.response_type == NormativeActionStatus.NOT_REGULATED or norm_response.response_type == NormativeActionStatus.ALLOWED:
            return True
        
        if norm_response.response_type == NormativeActionStatus.INVIOLABLE:
            return False

        if norm_response.response_type == NormativeActionStatus.FORBIDDEN:
            return False