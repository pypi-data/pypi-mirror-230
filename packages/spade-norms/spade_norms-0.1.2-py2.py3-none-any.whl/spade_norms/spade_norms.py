from .engines.reasoning_engine import NormativeReasoningEngine
from .actions.normative_action import NormativeAction
from .engines.norm_engine import NormativeEngine
from .norms.norm import Norm
from .norms import norm_utils
from spade.agent import Agent
from enum import Enum
import traceback
import logging
import sys


class NormativeMixin:
    def __init__(
        self,
        *args,
        role: Enum = 0,
        normative_engine: NormativeEngine = None,
        reasoning_engine: NormativeReasoningEngine = None,
        actions: list = [],
        concerns: dict = {},
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.role = role
        self.normative = NormativeComponent(
            self, normative_engine, reasoning_engine, actions, concerns
        )


class NormativeComponent:
    def __init__(
        self,
        agent: Agent,
        normative_engine: NormativeEngine,
        reasoning_engine: NormativeReasoningEngine,
        actions: list = [],
        concerns: dict = {},
    ):
        """
        Creates a normative agent given a `NormativeEngine` and a `NormativeReasoningEngine`. If no `NormativeReasoningEngine` is provided the default is used.
        User can pass also the agent's actions as a list of `NormativeAction`. Or the agent concerns as  a `dict` with `key: norm_domain` and `value: Norm`
        """
        self.agent = agent
        self.normative_engine = normative_engine
        self.concerns = concerns
        self.reasoning_engine = (
            NormativeReasoningEngine() if reasoning_engine is None else reasoning_engine
        )

        self.actions = {}
        if len(actions) > 0:
            self.add_actions(actions)

    def set_normative_engine(self, normative_engine: NormativeEngine):
        """
        Overrides the agent's actual normative engine
        """
        self.normative_engine = normative_engine

    async def perform(self, action_name: str, *args, **kwargs):
        self.__check_exists(action_name)
        do_action = self.__normative_eval(action_name)
        if do_action:
            try:
                action_result = await self.actions[action_name].action_fn(
                    self.agent, *args, **kwargs
                )
                return True, action_result
                
            except Exception:
                logging.error(traceback.format_exc())
                print("Error performing action: ", sys.exc_info()[0])
        else:
            # TODO: proceeding for actions not performed
            print(
                "[{}]: Action {} not performed due to normative constrictions".format(
                    self.agent.jid, action_name
                )
            )
        return False, None

    def __check_exists(self, action_name: str):
        if self.actions.get(action_name, None) is None:
            raise Exception(
                "Action with name {} does not exist in action dict".format(action_name)
            )

    def __normative_eval(self, action_name):
        action = self.actions[action_name]
        if self.normative_engine is not None:
            normative_response = self.normative_engine.check_legislation(
                action, self.agent
            )
            do_action = self.reasoning_engine.inference(self.agent, normative_response)
        else:
            do_action = True
        return do_action

    def add_action(self, action: NormativeAction):
        self.actions[action.name] = action

    def add_actions(self, action_list: list):
        for action in action_list:
            self.add_action(action)

    def delete_action(self, action: NormativeAction):
        self.__check_exists(action_name=action.name)
        self.actions.pop(action.name)

    def add_concern(self, concern: Norm):
        self.concerns = norm_utils.add_single(self.concerns, concern)

    def add_concerns(self, concern_list: list):
        self.concerns = norm_utils.add_multiple(self.concerns, concern_list)

    def contains_concern(self, concern: Norm) -> bool:
        return norm_utils.contains(self.concerns, concern)

    def remove_concern(self, concern: Norm) -> bool:
        self.concerns = norm_utils.remove(self.concerns, concern)
