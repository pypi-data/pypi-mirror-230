# Add, contains and remove do not need test since its done at norm_utils.py

from spade_norms.actions.normative_action import NormativeAction
from spade_norms.engines.norm_engine import NormativeEngine
from spade_norms.norms.norm_enums import NormType, NormativeActionStatus
from spade_norms.norms.norm import Norm

def create_norm(sufix = '' , domain = 0, ret_value = NormativeActionStatus.ALLOWED, roles = [], inv = True):
    return Norm('test' + sufix, NormType.PROHIBITION, lambda x: ret_value, domain=domain, roles=roles, inviolable=inv) 

def create_normative_engine():
    return NormativeEngine()

def create_action(sufix = '' , domain = 0):
    return NormativeAction('test' + sufix, lambda x: x, domain=domain)

#get_appliable_norms

def test_get_appliable_norms_returns_empty_on_both_empty(agent):
    agent.normative.concerns = {}
    norm_eng = create_normative_engine()

    appl_norms = norm_eng.get_appliable_norms(0, agent)

    assert len(appl_norms) == 0 

def test_get_appliable_norms_returns_empty_on_action_with_different_domain(agent):
    agent.normative.concerns = {}
    norm_eng = create_normative_engine()
    action = create_action(domain=1)
    norm = create_norm()
    concern = create_norm('concern')

    agent.normative.add_concern(concern)
    norm_eng.add_norm(norm)

    appl_norms = norm_eng.get_appliable_norms(action.domain, agent)

    assert len(appl_norms) == 0

def test_get_appliable_norms_returns_empty_on_agent_with_different_role(agent):
    agent.normative.concerns = {}
    norm_eng = create_normative_engine()
    action = create_action()
    norm = create_norm(roles=[1])
    concern = create_norm('concern', roles=[1])

    agent.normative.add_concern(concern)
    norm_eng.add_norm(norm)

    appl_norms = norm_eng.get_appliable_norms(action.domain, agent)

    assert len(appl_norms) == 0

def test_get_appliable_norms_returns_norms_in_domain_default_with_no_other_domain(agent):
    agent.normative.concerns = {}
    norm_eng = create_normative_engine()
    action = create_action()
    norm = create_norm()
    concern = create_norm('concern')

    agent.normative.add_concern(concern)
    norm_eng.add_norm(norm)

    appl_norms = norm_eng.get_appliable_norms(action.domain, agent)

    assert len(appl_norms) == 2

def test_get_appliable_norms_returns_norms_in_role_default_with_no_other_role(agent):
    agent.normative.concerns = {}
    norm_eng = create_normative_engine()
    action = create_action()
    norm = create_norm(roles=[0])
    concern = create_norm('concern', roles=[0])

    agent.normative.add_concern(concern)
    norm_eng.add_norm(norm)

    appl_norms = norm_eng.get_appliable_norms(action.domain, agent)

    assert len(appl_norms) == 2

def test_get_appliable_norms_returns_norms_in_domain_default_with_other_domains(agent):
    agent.normative.concerns = {}
    norm_eng = create_normative_engine()
    action = create_action()
    norm = create_norm()
    concern = create_norm('concern')
    norm2 = create_norm(sufix='2', domain=1)
    concern2 = create_norm('concern2', domain=1)

    agent.normative.add_concern(concern)
    norm_eng.add_norm(norm)
    agent.normative.add_concern(concern2)
    norm_eng.add_norm(norm2)

    appl_norms = norm_eng.get_appliable_norms(action.domain, agent)

    assert len(appl_norms) == 2

def test_get_appliable_norms_returns_norms_in_role_default_with_other_roles(agent):
    agent.normative.concerns = {}
    norm_eng = create_normative_engine()
    action = create_action()
    norm = create_norm(roles=[0])
    concern = create_norm('concern', roles=[0])
    norm2 = create_norm(sufix='2',roles=[1])
    concern2 = create_norm('concern2', roles=[1])

    agent.normative.add_concern(concern)
    norm_eng.add_norm(norm)
    agent.normative.add_concern(concern2)
    norm_eng.add_norm(norm2)

    appl_norms = norm_eng.get_appliable_norms(action.domain, agent)

    assert len(appl_norms) == 2

#check_legislation

def test_check_legislation_returns_not_regulated_on_both_empty_db(agent):
    agent.normative.concerns = {}
    norm_eng = create_normative_engine()
    action = create_action()

    norm_resp = norm_eng.check_legislation(action, agent)

    assert norm_resp.response_type == NormativeActionStatus.NOT_REGULATED

def test_check_legislation_returns_not_regulated_on_non_apliable_norms_because_domain(agent):
    agent.normative.concerns = {}
    norm_eng = create_normative_engine()
    action = create_action(domain=1)
    norm = create_norm()

    norm_eng.add_norm(norm)
    norm_resp = norm_eng.check_legislation(action, agent)

    assert norm_resp.response_type == NormativeActionStatus.NOT_REGULATED

def test_check_legislation_returns_not_regulated_on_non_apliable_concerns_because_domain(agent):
    agent.normative.concerns = {}
    norm_eng = create_normative_engine()
    action = create_action(domain=1)

    concern = create_norm('concern')
    agent.normative.add_concern(concern)

    norm_resp = norm_eng.check_legislation(action, agent)

    assert norm_resp.response_type == NormativeActionStatus.NOT_REGULATED

def test_check_legislation_returns_not_regulated_on_non_apliable_norms_nor_concerns_because_domain(agent):
    agent.normative.concerns = {}
    norm_eng = create_normative_engine()
    action = create_action(domain=1)
    norm = create_norm()
    concern = create_norm('concern')

    agent.normative.add_concern(concern)
    norm_eng.add_norm(norm)

    norm_resp = norm_eng.check_legislation(action, agent)

    assert norm_resp.response_type == NormativeActionStatus.NOT_REGULATED

def test_check_legislation_returns_not_regulated_on_non_apliable_norms_because_role(agent):
    agent.normative.concerns = {}
    norm_eng = create_normative_engine()
    action = create_action()
    norm = create_norm(roles=[1])

    norm_eng.add_norm(norm)
    norm_resp = norm_eng.check_legislation(action, agent)

    assert norm_resp.response_type == NormativeActionStatus.NOT_REGULATED

def test_check_legislation_returns_not_regulated_on_non_apliable_concerns_because_role(agent):
    agent.normative.concerns = {}
    norm_eng = create_normative_engine()
    action = create_action()
    concern = create_norm('concern', roles=[1])

    agent.normative.add_concern(concern)

    norm_resp = norm_eng.check_legislation(action, agent)

    assert norm_resp.response_type == NormativeActionStatus.NOT_REGULATED

def test_check_legislation_returns_not_regulated_on_non_apliable_norms_nor_concerns_because_role(agent):
    agent.normative.concerns = {}
    norm_eng = create_normative_engine()
    action = create_action()
    norm = create_norm(roles=[1])
    concern = create_norm('concern',roles=[1])

    agent.normative.add_concern(concern)
    norm_eng.add_norm(norm)

    norm_resp = norm_eng.check_legislation(action, agent)

    assert norm_resp.response_type == NormativeActionStatus.NOT_REGULATED

def test_check_legislation_returns_inviolable_on_norm_forbidding_with_no_concern(agent):
    agent.normative.concerns = {}
    norm_eng = create_normative_engine()
    action = create_action()
    norm = create_norm(ret_value=NormativeActionStatus.FORBIDDEN)

    norm_eng.add_norm(norm)

    norm_resp = norm_eng.check_legislation(action, agent)

    assert norm_resp.response_type == NormativeActionStatus.INVIOLABLE
    assert len(norm_resp.norms_breaking) == 1

def test_check_legislation_returns_forbidden_on_norm_forbidding_with_no_concern(agent):
    agent.normative.concerns = {}
    norm_eng = create_normative_engine()
    action = create_action()
    norm = create_norm(ret_value=NormativeActionStatus.FORBIDDEN, inv = False)

    norm_eng.add_norm(norm)

    norm_resp = norm_eng.check_legislation(action, agent)

    assert norm_resp.response_type == NormativeActionStatus.FORBIDDEN
    assert len(norm_resp.norms_breaking) == 1

def test_check_legislation_returns_inviolable_on_norm_forbidding_with_allowing_concern(agent):
    agent.normative.concerns = {}
    norm_eng = create_normative_engine()
    action = create_action()
    norm = create_norm(ret_value=NormativeActionStatus.FORBIDDEN)
    concern = create_norm('concern')

    agent.normative.add_concern(concern)
    norm_eng.add_norm(norm)

    norm_resp = norm_eng.check_legislation(action, agent)

    assert norm_resp.response_type == NormativeActionStatus.INVIOLABLE
    assert len(norm_resp.norms_breaking) == 1
    assert len(norm_resp.norms_following) == 1

def test_check_legislation_returns_forbidden_on_norm_forbidding_with_allowing_concern(agent):
    agent.normative.concerns = {}
    norm_eng = create_normative_engine()
    action = create_action()
    norm = create_norm(ret_value=NormativeActionStatus.FORBIDDEN, inv=False)
    concern = create_norm('concern')

    agent.normative.add_concern(concern)
    norm_eng.add_norm(norm)

    norm_resp = norm_eng.check_legislation(action, agent)

    assert norm_resp.response_type == NormativeActionStatus.FORBIDDEN
    assert len(norm_resp.norms_breaking) == 1
    assert len(norm_resp.norms_following) == 1

def test_check_legislation_returns_inviolable_on_norm_forbidding_with_forbidding_concern(agent):
    agent.normative.concerns = {}
    norm_eng = create_normative_engine()
    action = create_action()
    norm = create_norm(ret_value=NormativeActionStatus.FORBIDDEN)
    concern = create_norm('concern', ret_value=NormativeActionStatus.FORBIDDEN)

    agent.normative.add_concern(concern)
    norm_eng.add_norm(norm)

    norm_resp = norm_eng.check_legislation(action, agent)

    assert norm_resp.response_type == NormativeActionStatus.INVIOLABLE
    assert len(norm_resp.norms_breaking) == 2

def test_check_legislation_returns_forbidden_on_norm_forbidding_with_forbidding_concern(agent):
    agent.normative.concerns = {}
    norm_eng = create_normative_engine()
    action = create_action()
    norm = create_norm(ret_value=NormativeActionStatus.FORBIDDEN, inv=False)
    concern = create_norm('concern', ret_value=NormativeActionStatus.FORBIDDEN, inv=False)

    agent.normative.add_concern(concern)
    norm_eng.add_norm(norm)

    norm_resp = norm_eng.check_legislation(action, agent)

    assert norm_resp.response_type == NormativeActionStatus.FORBIDDEN
    assert len(norm_resp.norms_breaking) == 2

def test_check_legislation_returns_inviolable_on_concern_forbidding_with_no_norm(agent):
    agent.normative.concerns = {}
    norm_eng = create_normative_engine()
    action = create_action()
    concern = create_norm('concern',ret_value=NormativeActionStatus.FORBIDDEN)

    agent.normative.add_concern(concern)

    norm_resp = norm_eng.check_legislation(action, agent)
    
    assert norm_resp.response_type == NormativeActionStatus.INVIOLABLE
    assert len(norm_resp.norms_breaking) == 1

def test_check_legislation_returns_forbidden_on_concern_forbidding_with_no_norm(agent):
    agent.normative.concerns = {}
    norm_eng = create_normative_engine()
    action = create_action()
    concern = create_norm('concern',ret_value=NormativeActionStatus.FORBIDDEN, inv=False)

    agent.normative.add_concern(concern)

    norm_resp = norm_eng.check_legislation(action, agent)
    
    assert norm_resp.response_type == NormativeActionStatus.FORBIDDEN
    assert len(norm_resp.norms_breaking) == 1

def test_check_legislation_returns_inviolable_on_norm_allowing_with_forbidding_concern(agent):
    agent.normative.concerns = {}
    norm_eng = create_normative_engine()
    action = create_action()
    norm = create_norm()
    concern = create_norm('concern', ret_value=NormativeActionStatus.FORBIDDEN)

    agent.normative.add_concern(concern)
    norm_eng.add_norm(norm)

    norm_resp = norm_eng.check_legislation(action, agent)

    assert norm_resp.response_type == NormativeActionStatus.INVIOLABLE
    assert len(norm_resp.norms_breaking) == 1
    assert len(norm_resp.norms_following) == 1

def test_check_legislation_returns_forbidden_on_norm_allowing_with_forbidding_concern(agent):
    agent.normative.concerns = {}
    norm_eng = create_normative_engine()
    action = create_action()
    norm = create_norm()
    concern = create_norm('concern', ret_value=NormativeActionStatus.FORBIDDEN, inv=False)

    agent.normative.add_concern(concern)
    norm_eng.add_norm(norm)

    norm_resp = norm_eng.check_legislation(action, agent)

    assert norm_resp.response_type == NormativeActionStatus.FORBIDDEN
    assert len(norm_resp.norms_breaking) == 1
    assert len(norm_resp.norms_following) == 1

def test_check_legislation_returns_allowed_on_norm_allowing_with_no_concern(agent):
    agent.normative.concerns = {}
    norm_eng = create_normative_engine()
    action = create_action()
    norm = create_norm()

    norm_eng.add_norm(norm)

    norm_resp = norm_eng.check_legislation(action, agent)

    assert norm_resp.response_type == NormativeActionStatus.ALLOWED
    assert len(norm_resp.norms_following) == 1

def test_check_legislation_returns_allowed_on_concern_allowing_with_no_norms(agent):
    agent.normative.concerns = {}
    norm_eng = create_normative_engine()
    action = create_action()
    concern = create_norm('concern')

    agent.normative.add_concern(concern)

    norm_resp = norm_eng.check_legislation(action, agent)

    assert norm_resp.response_type == NormativeActionStatus.ALLOWED
    assert len(norm_resp.norms_following) == 1

def test_check_legislation_returns_allowed_on_concern_and_norm_allowing(agent):
    agent.normative.concerns = {}
    norm_eng = create_normative_engine()
    action = create_action()
    norm = create_norm()
    concern = create_norm('concern')

    agent.normative.add_concern(concern)
    norm_eng.add_norm(norm)

    norm_resp = norm_eng.check_legislation(action, agent)

    assert norm_resp.response_type == NormativeActionStatus.ALLOWED
    assert len(norm_resp.norms_following) == 2
