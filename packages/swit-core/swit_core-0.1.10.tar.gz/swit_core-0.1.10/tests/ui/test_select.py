import unittest

from switcore.ui.element_components import OpenLink
from switcore.ui.select import Select, Option, OptionGroup, SelectQuery


class SelectTest(unittest.TestCase):

    def test_valid_select01(self):
        select = Select(
            trigger_on_input=True,
            options=[
                Option(
                    label="test label1",
                    action_id="action_id1"
                ),
                Option(
                    label="test label2",
                    action_id="action_id2"
                ),
            ]
        )
        expected = {
            'type': 'select',
            'multiselect': False,
            'trigger_on_input': True,
            'options': [
                {
                    'label': 'test label1',
                    'action_id': 'action_id1'
                },
                {
                    'label': 'test label2',
                    'action_id': 'action_id2'
                }
            ],
            'option_groups': []
        }
        # print(json.dumps(expected, indent=4))
        self.assertEqual(expected, select.dict(exclude_none=True))

    def test_valid_select02(self):
        select = Select(
            trigger_on_input=True,
            options=[
                Option(
                    label="test label1",
                    action_id="action_id1",
                    static_action=OpenLink(
                        link_url="https://www.google.com"
                    )
                ),
                Option(
                    label="test label2",
                    action_id="action_id2"
                ),
            ]
        )
        expected = {
            'type': 'select',
            'multiselect': False,
            'options': [{'action_id': 'action_id1',
                         'label': 'test label1',
                         'static_action': {'link_url': 'https://www.google.com',
                                           'action_type': 'open_link'}},
                        {'action_id': 'action_id2', 'label': 'test label2'}],
            'option_groups': [],
            'trigger_on_input': True,
        }
        self.assertEqual(expected, select.dict(exclude_none=True))

    def test_valid_select03(self):
        select = Select(
            trigger_on_input=True,
            options=[
                Option(
                    label="test label1",
                    action_id="action_id1",
                    static_action=OpenLink(
                        link_url="https://www.google.com"
                    )
                ),
                Option(
                    label="test label2",
                    action_id="action_id2"
                ),
            ],
            option_groups=[
                OptionGroup(label="test group1", options=[Option(label="test label1", action_id="action_id1")]),
                OptionGroup(label="test group2", options=[Option(label="test label2", action_id="action_id2")]),
            ],
            query=SelectQuery(
                value="search value",
                action_id="action_id"
            )
        )

        expected: dict = {
            'type': 'select',
            'multiselect': False,
            'options': [{'action_id': 'action_id1',
                         'label': 'test label1',
                         'static_action': {'link_url': 'https://www.google.com',
                                           'action_type': 'open_link'}},
                        {'action_id': 'action_id2', 'label': 'test label2'}],
            'option_groups': [{'label': 'test group1',
                               'options': [{'action_id': 'action_id1', 'label': 'test label1'}]},
                              {'label': 'test group2',
                               'options': [{'action_id': 'action_id2', 'label': 'test label2'}]}],
            'trigger_on_input': True,
            'query': {'query_server': True, 'disabled': False, 'action_id': 'action_id', 'value': 'search value'}
        }
        self.assertEqual(expected, select.dict(exclude_none=True))
