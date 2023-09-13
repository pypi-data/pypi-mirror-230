from contextlib import contextmanager
from unittest import mock

from django.utils.translation import ugettext_lazy as _

from mayan.apps.sources.source_backends.base import SourceBackend

from ..source_backends.imap_source_backends import SourceBackendIMAPEmail
from ..source_backends.mixins import SourceBackendMixinEmail
from ..source_backends.pop3_source_backends import SourceBackendPOP3Email

from .mocks import MockIMAPServer, MockPOP3Mailbox


class SourceBackendTestEmail(SourceBackendMixinEmail, SourceBackend):
    label = 'Test email source backend'

    def action_file_get(self, message_id):
        source_backend_instance = self.get_model_instance()

        source_backend_data = source_backend_instance.get_backend_data()

        message = source_backend_data['_test_content']

        yield from self.process_message(message=message)

    def get_stored_file_list(self):
        yield ''


class SourceBackendTestIMAPEmail(SourceBackendIMAPEmail):
    label = _('Test IMAP email')

    @contextmanager
    def _get_server(self):
        with mock.patch('imaplib.IMAP4', autospec=True) as mock_imaplib:
            mock_imaplib.return_value = MockIMAPServer()
            mock_imaplib.return_value._add_test_message()
            mock_imaplib.return_value._add_test_message()
            with super()._get_server() as server:
                yield server


class SourceBackendTestPOP3Email(SourceBackendPOP3Email):
    label = _('Test POP3 email')

    @contextmanager
    def _get_server(self):
        with mock.patch('poplib.POP3', autospec=True) as mock_poplib:
            mock_poplib.return_value = MockPOP3Mailbox()
            mock_poplib.return_value._add_test_message()
            mock_poplib.return_value._add_test_message()
            with super()._get_server() as server:
                yield server
