''''
This class will handle the norm activation, checking periodically (parameter) the activation condition of all norms
and setting them active or not.
User can deactivate this automatic update by 
'''
from ..actions.normative_action import NormativeAction 
from ..norms.normative_response import NormativeResponse
from ..norms.norm_enums import *
from ..norms.norm import Norm
from ..norms import norm_utils 
from spade.agent import Agent

class NormativeEngine():
    def __init__(self, norm: Norm = None, norm_list: list = None):
        self.norm_db = {}
        #self.active_norms = {}
        if norm_list != None:
            self.add_norms(norm_list)
        if norm != None:
            self.add_norm(norm)

    def add_norms(self, norms: list):
        self.norm_db = norm_utils.add_multiple(self.norm_db, norms)
    
    def add_norm(self, norm: Norm):
        self.norm_db = norm_utils.add_single(self.norm_db, norm)

    def contains_norm(self, in_norm: Norm)-> bool:
        return norm_utils.contains(self.norm_db, in_norm)
    
    def remove_norm(self, norm: Norm) -> bool:
        self.norm_db = norm_utils.remove(self.norm_db, norm)

    def check_legislation(self, action: NormativeAction, agent: Agent) -> NormativeResponse:
        '''
        This method checks the current norm database and for a given action returns if it is allowed or not in the form of a `NormativeResponse` object
        '''
        normative_response = NormativeResponse(action=action, responseType=NormativeActionStatus.NOT_REGULATED)
        
        appliable_norms = self.get_appliable_norms(action.domain, agent)

        if len(appliable_norms) == 0:
            normative_response.response_type = NormativeActionStatus.NOT_REGULATED
            return normative_response

        for norm in appliable_norms:
            cond_result = norm.condition_fn(agent)
            assert isinstance(cond_result, NormativeActionStatus)
            
            if cond_result == NormativeActionStatus.FORBIDDEN or cond_result == NormativeActionStatus.INVIOLABLE:
                normative_response.add_forbidding_norm(norm)

            if cond_result == NormativeActionStatus.ALLOWED:
                normative_response.add_allowing_norm(norm)
        
        return normative_response
    
    def get_appliable_norms(self, domain: Enum, agent: Agent) -> list:
        '''
        This method receives a `domain` and an `agent` and returns the norms that could apply for it 
        '''
        related_norms = self.norm_db.get(domain, [])
        agent_concerns = agent.normative.concerns.get(domain, [])
        related_norms = norm_utils.join_norms_and_concerns(related_norms, agent_concerns)
        related_norms = norm_utils.filter_norms_by_role(related_norms, agent.role)

        return related_norms
