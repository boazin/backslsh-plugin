from slash import plugins
from backslash import Backslash as BackslashClient
from slash.ctx import context

from urlobject import URLObject

import slash

import gossip

class BackslashPlugin(plugins.PluginInterface):

    def __init__(self):
        self.current_session = None

    def get_name(self):
        return "backslash"

    def configure_argument_parser(self, parser):
        parser.add_argument(
            "-s", "--server-address", help="IP Address of backslash server")

    def configure_from_parsed_args(self, args):
        if args.server_address:
            self.server_address = URLObject(args.server_address)
        else:
            self.server_address = URLObject(slash.config.root.backslash.serverAddress)

    def session_start(self):
        self.client = BackslashClient(self.server_address)

        self.current_session = self.client.report_session_start(
            logical_id=context.session.id)
        gossip.trigger('backslash.report_session_start', started_session=self.current_session)

    def session_end(self):
        if self.current_session:
            self.current_session.report_end()

    def test_start(self):
        self.current_test = self.current_session.report_test_start(
            test_logical_id=context.test.__slash__.id, name=str(context.test))
        gossip.trigger('backslash.report_test_start', started_test=self.current_test)

    def test_end(self):
        self.current_test.report_end()
        gossip.trigger('backslash.report_test_end', ended_test=self.current_test)

    def test_error(self):
        self.current_test.add_error()

    def test_failure(self):
        self.current_test.add_failure()

    def test_interrupt(self):
        self.current_test.mark_interrupted()

    def test_skip(self, reason):
        self.current_test.mark_skipped()
