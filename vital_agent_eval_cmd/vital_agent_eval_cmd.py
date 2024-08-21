import argparse
import asyncio
import os
import sys
from com_vitalai_aimp_domain.model.AIMPIntent import AIMPIntent
from com_vitalai_aimp_domain.model.AIMPMessage import AIMPMessage
from com_vitalai_aimp_domain.model.UserMessageContent import UserMessageContent
from vital_agent_container_client.aimp_message_handler_inf import AIMPMessageHandlerInf
from vital_agent_container_client.vital_agent_container_client import VitalAgentContainerClient
from vital_ai_vitalsigns.utils.uri_generator import URIGenerator
from agent_eval_utils.excel_reader import ExcelReader
from agent_eval_utils.excel_writer import ExcelWriter


class LocalMessageHandler(AIMPMessageHandlerInf):

    def __init__(self):
        self.response_list = []

    async def receive_message(self, message):
        print(f"Local Handler Received message: {message}")
        self.response_list.append(message)


class VitalAgentEvalCommand:
    def __init__(self, args):
        self.parser = self.create_parser()
        self.args = self.parser.parse_args()
        self.vital_home = os.getenv('VITAL_HOME', '')

    def create_parser(self):

        parser = argparse.ArgumentParser(prog="vitalagenteval", description="VitalAgentEval Command", add_help=True)

        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        help_parser = subparsers.add_parser('help', help="Display help information")

        info_parser = subparsers.add_parser('info', help="Display information about the system and environment")

        eval_parser = subparsers.add_parser('eval', help="Evaluate an Excel file")

        eval_parser.add_argument('-i', '--input-file', type=str, required=True, help="Excel input file path to process")
        eval_parser.add_argument('-o', '--output-file', type=str, required=True,
                                 help="Excel output file path to save the result")

        return parser

    def run(self):
        if self.args.command == 'help':
            self.parser.print_help()
        elif self.args.command == 'eval':
            if self.args.input_file and self.args.output_file:
                self.process_excel(self.args.input_file, self.args.output_file)
            else:
                self.parser.print_help()
        elif self.args.command == 'info':
            self.info()
        else:
            self.parser.print_help()

    def info(self):
        vital_home = self.vital_home
        print("VitalAgentEval Info")
        print(f"Current VITAL_HOME: {vital_home}")

    async def process_excel_async(self, input_file_path, output_file_path):

        print(f"Processing Excel file: {input_file_path}")

        handler = LocalMessageHandler()

        client = VitalAgentContainerClient("http://localhost:6006", handler)

        health = await client.check_health()

        print("Health:", health)

        await client.open_websocket()

        excel_reader = ExcelReader()

        rows_data = excel_reader.read_excel_to_dict(input_file_path)

        headers = [
            'Identifier',
            'AccountIdentifier',
            'LoginIdentifier',
            'SessionIdentifier',
            'Action',
            'MessageClass',
            'MessageText'
        ]

        output_data = []

        for row in rows_data:
            # print(row)

            action = row.get('Action', None)

            if action == 'SendMessage':

                message_class = row.get('MessageClass', None)

                if message_class == 'AIMPIntent':

                    intent_type = row.get('IntentType', None)

                    if intent_type == 'CHAT':
                        print(f"Sending Message: {message_class}")

                        message_uri = row.get('MessageUri', None)
                        message_text = row.get('MessageText', None)

                        print(f"Message Text: {message_text}")

                        aimp_intent = AIMPIntent()
                        aimp_intent.URI = message_uri

                        message_content = UserMessageContent()
                        message_content.URI = URIGenerator.generate_uri()
                        message_content.text = message_text

                        message = [aimp_intent, message_content]

                        # send

                        message = [{"type": "greeting", "content": "Hello, WebSocket!"}]

                        await client.send_message(message)

                        await client.wait_for_close_or_timeout(60)

                        response_list = handler.response_list

                        for response_message in response_list:
                            print(f"Response Message: {response_message}")

                        response_dict = {
                            'MessageText': 'Message Text'
                        }

                        output_data.append(response_dict)

        if len(output_data) > 0:
            excel_writer = ExcelWriter()
            print(f"Writing Excel file: {output_file_path}")
            excel_writer.write_excel(output_file_path, headers, output_data)




        # Wait for some time to receive messages
        # await asyncio.sleep(10)

        await client.close_websocket()

    def process_excel(self, input_file_path, output_file_path):

        if not os.path.exists(input_file_path):
            print(f"File {input_file_path} does not exist.")
            sys.exit(1)

        asyncio.run(self.process_excel_async(input_file_path, output_file_path))


def main():
    import sys
    command = VitalAgentEvalCommand(sys.argv[1:])
    command.run()


if __name__ == "__main__":
    main()
