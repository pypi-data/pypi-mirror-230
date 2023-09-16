from tests.factories import MockedNormativeAgentFactory
import pytest

@pytest.fixture
def agent():
    return MockedNormativeAgentFactory()