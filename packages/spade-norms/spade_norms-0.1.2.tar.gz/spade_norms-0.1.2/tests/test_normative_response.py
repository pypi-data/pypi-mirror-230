from spade_norms.norms.normative_response import NormativeResponse
from spade_norms.actions.normative_action import NormativeAction
from spade_norms.norms.norm_enums import *
from spade_norms.norms.norm import Norm

def create_normative_action(sufix = '' , domain = 0):
    return NormativeAction('test' + sufix, lambda x: True, domain)

def create_empty_normative_response():
    action = create_normative_action()
    return NormativeResponse(action)

def test_add_allowing_norm_returns_allowed_over_empty_list():
    norm_response = create_empty_normative_response()
    norm = Norm('test', NormType.PROHIBITION, lambda x: True)
    norm_response.add_allowing_norm(norm)
    
    assert norm_response.response_type == NormativeActionStatus.ALLOWED
    assert len(norm_response.norms_following) == 1
    assert len(norm_response.norms_breaking) == 0
    assert norm_response.total_reward == norm.reward

def test_add_allowing_norm_returns_allowed_over_allowed():
    norm_response = create_empty_normative_response()
    norm = Norm('test', NormType.PROHIBITION, lambda x: True)
    norm_response.response_type = NormativeActionStatus.ALLOWED
    norm_response.add_allowing_norm(norm)
    
    assert norm_response.response_type == NormativeActionStatus.ALLOWED
    assert len(norm_response.norms_following) == 1
    assert len(norm_response.norms_breaking) == 0
    assert norm_response.total_reward == norm.reward

def test_add_allowing_norm_returns_forbidden_over_forbidden():
    norm_response = create_empty_normative_response()
    norm = Norm('test', NormType.PROHIBITION, lambda x: True)
    norm_response.response_type = NormativeActionStatus.FORBIDDEN
    norm_response.add_allowing_norm(norm)
    
    assert norm_response.response_type == NormativeActionStatus.FORBIDDEN
    assert len(norm_response.norms_following) == 1
    assert len(norm_response.norms_breaking) == 0
    assert norm_response.total_reward == norm.reward

def test_add_allowing_norm_returns_inviolable_over_inviolable():
    norm_response = create_empty_normative_response()
    norm = Norm('test', NormType.PROHIBITION, lambda x: True)
    norm_response.response_type = NormativeActionStatus.INVIOLABLE
    norm_response.add_allowing_norm(norm)
    
    assert norm_response.response_type == NormativeActionStatus.INVIOLABLE
    assert len(norm_response.norms_following) == 1
    assert len(norm_response.norms_breaking) == 0
    assert norm_response.total_reward == norm.reward

def test_add_forbidding_norm_returns_forbidden_over_empty_list():
    norm_response = create_empty_normative_response()
    norm = Norm('test', NormType.PROHIBITION, lambda x: True, inviolable=False)
    norm_response.add_forbidding_norm(norm)
    
    assert norm_response.response_type == NormativeActionStatus.FORBIDDEN
    assert len(norm_response.norms_following) == 0
    assert len(norm_response.norms_breaking) == 1
    assert norm_response.total_penalty == norm.penalty

def test_add_forbidding_norm_returns_forbidden_over_allowed():
    norm_response = create_empty_normative_response()
    norm = Norm('test', NormType.PROHIBITION, lambda x: True, inviolable=False)
    norm_response.response_type = NormativeActionStatus.ALLOWED
    norm_response.add_forbidding_norm(norm)
    
    assert norm_response.response_type == NormativeActionStatus.FORBIDDEN
    assert len(norm_response.norms_following) == 0
    assert len(norm_response.norms_breaking) == 1
    assert norm_response.total_penalty == norm.penalty

def test_add_forbidding_norm_returns_forbidden_over_forbidden():
    norm_response = create_empty_normative_response()
    norm = Norm('test', NormType.PROHIBITION, lambda x: True, inviolable=False)
    norm_response.response_type = NormativeActionStatus.FORBIDDEN
    norm_response.add_forbidding_norm(norm)
    
    assert norm_response.response_type == NormativeActionStatus.FORBIDDEN
    assert len(norm_response.norms_following) == 0
    assert len(norm_response.norms_breaking) == 1
    assert norm_response.total_penalty == norm.penalty

def test_add_forbidding_norm_returns_inviolable_over_inviolable():
    norm_response = create_empty_normative_response()
    norm = Norm('test', NormType.PROHIBITION, lambda x: True, inviolable=False)
    norm_response.response_type = NormativeActionStatus.INVIOLABLE
    norm_response.add_forbidding_norm(norm)
    
    assert norm_response.response_type == NormativeActionStatus.INVIOLABLE
    assert len(norm_response.norms_following) == 0
    assert len(norm_response.norms_breaking) == 1
    assert norm_response.total_penalty == norm.penalty

def test_add_forbidding_norm_returns_inviolable_over_empty_when_inviolable():
    norm_response = create_empty_normative_response()
    norm = Norm('test', NormType.PROHIBITION, lambda x: True)
    norm_response.add_forbidding_norm(norm)
    
    assert norm_response.response_type == NormativeActionStatus.INVIOLABLE
    assert len(norm_response.norms_following) == 0
    assert len(norm_response.norms_breaking) == 1
    assert norm_response.total_penalty == norm.penalty

def test_add_forbidding_norm_returns_inviolable_over_allowed_when_inviolable():
    norm_response = create_empty_normative_response()
    norm = Norm('test', NormType.PROHIBITION, lambda x: True)
    norm_response.response_type = NormativeActionStatus.ALLOWED
    norm_response.add_forbidding_norm(norm)
    
    assert norm_response.response_type == NormativeActionStatus.INVIOLABLE
    assert len(norm_response.norms_following) == 0
    assert len(norm_response.norms_breaking) == 1
    assert norm_response.total_penalty == norm.penalty

def test_add_forbidding_norm_returns_inviolable_over_forbidden_when_inviolable():
    norm_response = create_empty_normative_response()
    norm = Norm('test', NormType.PROHIBITION, lambda x: True)
    norm_response.response_type = NormativeActionStatus.FORBIDDEN
    norm_response.add_forbidding_norm(norm)
    
    assert norm_response.response_type == NormativeActionStatus.INVIOLABLE
    assert len(norm_response.norms_following) == 0
    assert len(norm_response.norms_breaking) == 1
    assert norm_response.total_penalty == norm.penalty

def test_add_forbidding_norm_returns_inviolable_over_inviolable_when_inviolable():
    norm_response = create_empty_normative_response()
    norm = Norm('test', NormType.PROHIBITION, lambda x: True)
    norm_response.response_type = NormativeActionStatus.INVIOLABLE
    norm_response.add_forbidding_norm(norm)
    
    assert norm_response.response_type == NormativeActionStatus.INVIOLABLE
    assert len(norm_response.norms_following) == 0
    assert len(norm_response.norms_breaking) == 1
    assert norm_response.total_penalty == norm.penalty