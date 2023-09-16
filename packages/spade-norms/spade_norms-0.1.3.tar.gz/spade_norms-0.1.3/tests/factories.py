from spade_norms.spade_norms import NormativeMixin
from spade.agent import Agent 
import factory

class MockedNormativeAgent(NormativeMixin, Agent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class MockedNormativeAgentFactory(factory.Factory):
    class Meta:
        model = MockedNormativeAgent

    jid = "jid@fakeserver"
    password = "asdfgghj"