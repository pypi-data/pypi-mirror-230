import unittest

from switcore.action.schemas import SwitResponse, ViewCallbackType, View, Body, AttachmentCallbackTypes, AttachmentView, \
    AttachmentBody, SuggestionsCallbackTypes
from switcore.ui.divider import Divider
from switcore.ui.header import Header, AttachmentHeader
from switcore.ui.select import Option
from switcore.ui.text_paragraph import TextParagraph


class SwitViewResponseTest(unittest.TestCase):

    def test_swit_response_view(self):
        body = Body(
            elements=[TextParagraph(content="test content"), Divider()],
        )
        swit_response = SwitResponse(
            callback_type=ViewCallbackType.update,
            new_view=View(
                view_id="test01",
                state="test state",
                header=Header(title="this is Header"),
                body=body,
            )
        )
        expected: dict = {
            'callback_type': ViewCallbackType.update,
            'new_view': {
                'view_id': 'test01',
                'state': "test state",
                'header': {'title': 'this is Header'},
                'body': {
                    'elements': [
                        {
                            'content': 'test content',
                            'markdown': False,
                            'type': 'text'
                        },
                        {
                            'type': 'divider'
                        }
                    ],
                }
            }
        }
        self.assertEqual(expected, swit_response.dict(exclude_none=True))

    def test_swit_response_attachments(self):
        swit_response = SwitResponse(
            callback_type=AttachmentCallbackTypes.share_channel,
            attachments=[AttachmentView(
                state="test state",
                header=AttachmentHeader(title="this is Header", app_id="test app id"),
                body=AttachmentBody(
                    elements=[TextParagraph(content="test content")],
                ),
            )]
        )
        expected: dict = {
            'callback_type': AttachmentCallbackTypes.share_channel,
            'attachments': [{
                'state': "test state",
                'header': {
                    'title': 'this is Header',
                    'app_id': 'test app id'
                },
                'body': {
                    'elements': [
                        {
                            'content': 'test content',
                            'markdown': False,
                            'type': 'text'
                        }
                    ],
                }
            }]
        }
        self.assertEqual(expected, swit_response.dict(exclude_none=True))

    def test_swit_response_query_suggestions(self):
        swit_response = SwitResponse(
            callback_type=SuggestionsCallbackTypes.query_suggestions,
            options=[Option(
                label="Search 성공!",
                action_id="success_option_action_id",
            )]
        )

        expected: dict = {
            'callback_type': SuggestionsCallbackTypes.query_suggestions,
            'options': [{
                'label': 'Search 성공!',
                'action_id': 'success_option_action_id'
            }]
        }
        self.assertEqual(expected, swit_response.dict(exclude_none=True))
