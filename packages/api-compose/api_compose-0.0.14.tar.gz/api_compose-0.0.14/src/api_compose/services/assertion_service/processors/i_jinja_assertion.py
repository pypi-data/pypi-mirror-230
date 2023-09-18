"""
CMD module which interactively ask user for jinja input
"""

import argparse
from typing import List, Callable

import cmd2
from cmd2 import with_category, Cmd2ArgumentParser, with_argparser

from api_compose.core.jinja.core.engine import JinjaEngine
from api_compose.services.assertion_service.models.jinja_assertion import JinjaAssertionModel
from api_compose.services.assertion_service.processors.jinja_assertion import JinjaAssertion
from api_compose.services.composition_service.jinja.context import ActionJinjaContext
from api_compose.services.composition_service.models.actions.actions.http_actions import JsonHttpActionModel
from api_compose.services.composition_service.models.actions.inputs.http_inputs import JsonHttpActionInputModel
from api_compose.services.composition_service.models.actions.outputs.http_outputs import JsonHttpActionOutputModel


class InteractiveJinjaAssertion(cmd2.Cmd):
    """Interactive Jinja Shell powered by Cmd"""
    intro = 'Welcome to the interactive jinja assertion. Type `examples` to get examples. Type help or ? to list commands.\n'
    prompt = '(jinja) '

    example_action_model: JsonHttpActionModel = JsonHttpActionModel(
        model_name='JsonHttpActionModel',
        id='post_number_stateful_one',
        parent_ids=['test_suite_one', 'scenario_two'],
        description='Post Number Stateful',
        execution_id='post_number_stateful_one_exec_id',
        input=JsonHttpActionInputModel(
            url='http://abc.com',
            params={
                'query': 'dogs',
            },
            method='GET',
        ),
        output=JsonHttpActionOutputModel(
            body={
                'field_one': 1234
            },
            headers={
                'Content-Length': '101',
                'Date': 'Sat, 26 Aug 2023 15:05:39 GMT',
                'Server': 'Google Frontend',
            },
            status_code=200,
        ),
    )

    def __init__(self,
                 jinja_context: ActionJinjaContext,
                 jinja_engine: JinjaEngine,
                 ):
        super().__init__(
            allow_cli_args=False, # avoid clashing with typer command
            )
        self.assertions: List[JinjaAssertionModel] = []
        self.jinja_context = jinja_context
        self.jinja_engine = jinja_engine

        self.debug = True
        self.always_show_hint = True


    def do_examples(self, arg):
        """ print examples """
        self.poutput(f"""Example Action:""")
        self.poutput(f"""\t id={self.example_action_model.id}""")
        self.poutput(f"""\t execution_id={self.example_action_model.execution_id}""")
        self.poutput(f"""\t input={self.example_action_model.input}""")
        self.poutput(f"""\t output={self.example_action_model.output}""")
        self.poutput("""Example Assertions: """)
        self.poutput(f"""\t Assert Output Body:""")
        self.poutput(
            f"""\t\t render "{{ actions('{self.example_action_model.execution_id}') |output_body| jpath('$.field_one') }}" == '1234'  """)
        self.poutput(f"""\t Assert Output Headers:""")
        self.poutput(
            f"""\t\t render "{{ action('{self.example_action_model.execution_id}')| output_headers| jpath('$.Server') }}" == 'Google Frontend'  """)
        self.poutput(f"""\t Assert Output Status Code:""")
        self.poutput(
            f"""\t\t render "{{ action('{self.example_action_model.execution_id}')| output_status_code }}" == 200  """)

    @with_category('jinja')
    def do_render(self, line):
        """
        Render a template.


        line: template
        """
        template = line
        model = JinjaAssertionModel(template=template, description='')
        assertion = JinjaAssertion(
            assertion_model=model,
            jinja_context=self.jinja_context,
            jinja_engine=self.jinja_engine,
        )
        assertion.run()
        self.assertions.append(model)
        self.poutput('Result:')
        self.poutput(model.model_dump_json(indent=4))


    action_parser = Cmd2ArgumentParser(description='Print Available Action Models in the Jinja Context')
    action_parser.add_argument('-c', '--config', action='store_true', help='Print the config of the actions')
    action_parser.add_argument('-i', '--input', action='store_true', help='Print the input of the actions')
    action_parser.add_argument('-o', '--output', action='store_true', help='Print the output of the actions')
    action_parser.add_argument('-a', '--all', action='store_true', help='Print both input and output of the actions')

    @with_argparser(action_parser)
    @with_category('jinja')
    def do_actions(self, ns: argparse.Namespace):
        """ Print Action Models - Assertions can be made with models Input and Output """
        for idx, action_model in enumerate(self.jinja_context.action_models):
            self.poutput('============')
            self.poutput(
                f"id={action_model.id} execution_id={action_model.execution_id} status_code={action_model.output.status_code}")
            if ns.config or ns.all:
                self.poutput(f"config={action_model.config.model_dump_json(indent=4)}")
            if ns.input or ns.all:
                self.poutput(f"input={action_model.input.model_dump_json(indent=4)}")
            if ns.output or ns.all:
                self.poutput(f"input={action_model.output.model_dump_json(indent=4)}")

        self.poutput('Run `examples` for usage')

    @with_category('jinja')
    def do_globals(self, args):
        """ Print Jinja Globals - Jinja Globals are functions used in jinja templates, e.g. {{ func(arg1) }} """
        for name, func in self.jinja_engine._custom_globals.items():
            func: Callable = func
            self.poutput(f"{name}={func.__doc__}")
        self.poutput('Run `examples` for more')

    def do_exit(self, arg):
        """Exit the calculator"""
        return True