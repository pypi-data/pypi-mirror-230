=====
Usage
=====
.. note:: This is a plugin for the `SPADE <https://github.com/javipalanca/spade>`_ agent platform. Please visit the
          `SPADE's documentation <https://spade-mas.readthedocs.io>`_ to know more about this platform.

SPADE Norms is a normative plugin meant to be used within Multi-Agent Systems that represent a normative environment. To understand better how it works, below is shown an example on how to build a MAS with normative restrictions.

This example shows the power of this component. In it, by developing only a single agent model you can obtain two different behaviour due to the normative restrictions. Let's go step-by-step explaining all it's needed to develop this kind of systems.

First of all we include all the packages that we are going to need in order to develop the example. It is necesary to say that all of them can be compressed, but we have decided to import them explicitly to make clear each one of the components.::

    from spade_norms.norms.norm_enums import NormType, NormativeActionStatus
    from spade_norms.actions.normative_action import NormativeAction
    from spade_norms.engines.norm_engine import NormativeEngine
    from spade_norms.spade_norms import NormativeMixin
    from spade.behaviour import CyclicBehaviour
    from spade_norms.norms.norm import Norm
    from spade.template import Template
    from spade.message import Message
    from spade.agent import Agent
    from enum import Enum
    import asyncio
    import spade

A norm is esentialy a restriction which describes when it is allowed or forbidden to perform a certain action. Norms are domain and role dependent so first of all we define both of them. In our case we have the domain Numbers and two roles: sender and receriver agents.::

    class Domain(Enum):
        NUMBERS = 1


    class Role(Enum):
        SENDER = 0
        RECEIVER = 1

What we need next is the condition of the norm. This is a function which returns ALLOWED or FORBIDDEN depending on the desired behaviour. For our case, we want only the agents with role SENDER to send messages, so our function is defined as follows.::

    def only_sender_can_send(agent):
        return NormativeActionStatus.FORBIDDEN


.. note:: Due to the nature of the engine, the norm will not be evaluated unless it is directed to the agent role so we can simply return a FORBIDDEN state for this example


With the norm defined we then formalize the action that is going to be regulated. In this case we are controlling the communication between agents so we intercept the ``send`` method and place it inside this NormativeAction. This step is key, since the way actions are performed in this plugin differs from the regular spade implementation as we will discuss later. ::

    async def send_number(agent, behaviour, send_agent, recv_agent):
        msg = Message(
            to=str(recv_agent.jid),
            body="{}".format(send_agent.counter),
            metadata={"performative": "inform"},
        )
        await behaviour.send(msg)

Now we can define our agent the same way we do it in regular SPADE. We do so by creating first two cyclic behaviours, one for sending the agent internal count and other for receiving and printing it to console. As this is regular SPADE code we won't mention it any deeper. ::


    class CyclicSendBehaviour(CyclicBehaviour):
        async def run(self):
            await self.agent.normative.perform("send", self, self.agent, self.agent.recv)
            await asyncio.sleep(2)
            self.agent.counter += 1


    class CyclicRecvBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)
            if msg:
                print("{} received count: {}".format(self.agent.jid, msg.body))
            await asyncio.sleep(1)

With the behaviours developed we create then the Normative Agent using the NormativeMixin. This mixin is what helds all the normative component and what will do the reasoning. ::

    class PrinterAgent(NormativeMixin, Agent):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.counter = 0
            self.recv = None

        async def setup(self):
            template = Template(metadata={"performative": "inform"})
            self.add_behaviour(CyclicSendBehaviour())
            self.add_behaviour(CyclicRecvBehaviour(), template)

Finally, we have all the information needed to create our normative environment. To do so we first create the normative action object and the norm that regulates this environment. After that, we have to create the ``normative_engine`` wich will tell when it is allowed or forbidden to perform an action. We have used the previous norm as a parameter in the constructor but norms can be added later by using the method ``add_norm(Norm)`` or ``add_norms(list)``. With the normative engine created, we can create the instances of our agents. Here we show two ways of doing this, in the first we create the agent and then we dynamicaly add the normative engine; in the second one we do it all in once. Having the agents created we can tell them the actions that they can perform. And finally we start the agents and see the behaviour. ::

    async def main():
        # 1 create normative action
        act = NormativeAction("send", send_number, Domain.NUMBERS)

        # 2 create norm
        no_rec_sending = Norm(
            "no-even-nums",             # name of the norm
            NormType.PROHIBITION,       # Type of the norm
            only_sender_can_send,       # function with the condition of the norm
            inviolable=False,           # flag to indicate if norm can be broken or not. (inviolable = False means that norm can be broken)
            domain=Domain.NUMBERS,      # Domain in which the norm will be applied
            roles=[Role.RECEIVER],      # Roles to which the norm will be applied
        )

        # 3 create normative engine
        normative_engine = NormativeEngine(norm_list=[no_rec_sending])

        # 4 create agent with user, apssword and noramtive engine
        ag1 = PrinterAgent("sender1@your.xmpp.server", "test", role=Role.SENDER)
        ag1.normative.set_normative_engine(normative_engine)
        
        ag2 = PrinterAgent("receiver1@your.xmpp.server", "test", role=Role.RECEIVER, normative_engine=normative_engine, actions = [act])

        ag1.recv = ag2
        ag2.recv = ag1

        # 5 add action to agent
        ag1.normative.add_action(act)

        # 6 start agent
        await ag1.start()
        await ag2.start()

For completitude and due to the recent change in SPADE, launcher for this example will be as follows:
    
    if __name__ == "__main__":
        spade.run(main())

.. warning:: Remember that, when inheriting from Mixins, they MUST be always before the base class (``Agent``).
             E.g. ``class MyAgent(NormativeMixin, Agent):``



.. note:: Here we have used the two ways of adding a `normative_engine` to an agent. At the first example we have created the agent and then added the normative engine and at the second example we have passed directly the engine in the agent constructor. Same thing has been done with the actions.

.. warning:: This plugin is intented to be used with only one normative engine. All agent must share the same engine in order to be aware of the organization/environment norms. Nevertheless, it is not mandatory to place the same Normative Engine in all of them, in case that it is needed for them to have separate ones. But keep in mind that if the agents have different instances of normative engine, they will NOT share the same norms.

This example will show in the terminal how the receiver agent can't send messages due to normative constrictions and the count that it has received from the sender agent. Under the ``examples/`` folder inside the project, more case scenarios can be found explaining more complex things such as how to dynamicaly add norms, remove them, override the reasoning engine, etc.