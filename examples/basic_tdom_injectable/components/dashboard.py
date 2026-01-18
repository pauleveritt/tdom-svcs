"""Dashboard component."""

from dataclasses import dataclass

from examples.basic_tdom_injectable.components.button import Button
from examples.basic_tdom_injectable.services.counter import Counter
from svcs_di import Inject
from svcs_di.injectors.decorators import injectable
from tdom import Node

from tdom_svcs import html


@injectable
@dataclass
class Dashboard:
    counter: Inject[Counter]

    def __call__(self) -> Node:
        return html(t"""
        <div class="dashboard">
            <h2>Counter: {self.counter.name}</h2>
            <p>Current count: {self.counter.count}</p>
            <{Button} label="Increment" />
        </div>
        """)
