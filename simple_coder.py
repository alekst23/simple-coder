import traceback
from datetime import datetime
import llm
import os
import asyncio
import re

C_WORKING_DIR = "simple_code_work"
C_CONFIG_CODER = "simple-coder.txt"
C_STOP_CODE = "JOBDONE"
C_MAX_EPOCH = 10

class SimpleCoder:
    def __init__(self, working_dir=C_WORKING_DIR, requirements=None, output_file_name=None, input_file_name_list=None, force_code=True):
        self.working_dir = working_dir
        self.message_log = []

        self.state = {}
        self.state['requirements'] = requirements
        self.state['output_file_name'] = output_file_name
        self.state['input_file_name_list'] = input_file_name_list
        self.state['force_code'] = force_code

        self.run_b = True
        self.run_epoch = 0

        self.get_config()
    

    def get_config(self, config_file=C_CONFIG_CODER):
        if not self.state.get('instructions', False):
            # get data from config file: confg/simple-coder.txt
            with open(os.path.join(os.getcwd(), "config", config_file), "r") as file:
                self.state['instructions'] = file.read()

        if self.state.get('requirements', False):
            # Check if requirements are an input file
            req = self.state['requirements']
            if req[0:2] == ">>":
                # Read from file
                self.state['requirements'] = self.get_file_contents(req[2:].strip())

        if self.state.get('output_file_name', False):
            # check if source file exists and load it
            if file_content := self.get_file_contents(self.state['output_file_name']):
                self.state['input_code'] = file_content


    def get_file_contents(self, file_name):

        file_name = file_name.strip() or self.state.get('output_file_name', None)
        file_path = os.path.join(self.working_dir, file_name)
        base_path = os.path.dirname(file_path)
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        if not os.path.exists(file_path):
            # create the file
            with open(file_path, "w") as file:
                file.write("")
            return ""
        else:
            with open(file_path, "r") as file:
                return file.read()
            

    async def run(self):
        while self.run_b:
            print(f"Epoch: {self.run_epoch}")
            self.run_epoch += 1
            await self.work()

            if self.run_epoch > C_MAX_EPOCH:
                # Write code state to file
                await self.store_code_file(self.state.get('input_code'))
                self.run_b = False

        return self.state.get('output_file_name', False)


    async def work(self):
        try:
            await self.compose_message_log()

            if self.message_log:
                response = await self.generate_response()

                await self.process_response(response)

        except Exception as e:
            print(traceback.print_exc())
            print(f"Error: {e}")
            raise e


    async def compose_message_log(self):
        try:
            assert self.state is not None, 'state'
            assert self.state.get('requirements', False), 'requirements not provided'
            assert self.state.get('output_file_name', False), 'output file name not provided'
            assert self.state.get('instructions', False), 'instructions are not set'
    

            # Compose message from instructions, file contents, file output, and requirements
            
            # instructions
            msg_instructions = self.make_message_instruction()
            
            # reference materials
            msg_file_data = self.make_message_materials()

            # input code
            msg_input_code = self.make_message_input()

            # requirements
            msg_requirements = self.make_message_requirements()

            # end control
            msg_end_control = self.make_message_endControl()

            # compose message
            self.message_log = msg_instructions + msg_file_data + msg_input_code + msg_requirements + msg_end_control
                    
        except Exception as e:
            print(traceback.print_exc())
            raise e
    

    def make_message_instruction(self):
        return [self.make_user_message(line) for line in self.state['instructions'].split("\n")]
    

    def make_message_materials(self):
        if self.state.get('input_file_name_list', False):
            msg_file_data = []
            if isinstance(self.state['input_file_name_list'], str):
                input_file_list = self.state['input_file_name_list'].split()
            else:
                input_file_list = self.state['input_file_name_list']
            input_file_contents = ""
            for file_name in input_file_list:
                input_file_contents = f"\n<input file='{file_name}'\n>{self.get_file_contents(file_name)}</input>\n\n"
                msg_file_data.append(self.make_user_message(f"This is one of our project files:\n{input_file_contents}"))
                
            return msg_file_data
        
        else:
            return []


    def make_message_input(self):
        if self.state.get('input_code', False):
            msg_code_input = [self.make_user_message(f"This is our output file:\n<output file_name='{self.state['output_file_name']}'>\n{self.state.get('input_code')}</output>")]
        else:
            msg_code_input = [self.make_user_message(f"Our output file is {self.state['output_file_name']} and it is empty")]
            
        return msg_code_input
    

    def make_message_requirements(self):
        return [self.make_user_message(f"The following are requirements for our output file. {self.state['requirements']}")]


    def make_message_endControl(self):
        msg_1 = f"Analyze the contents of the output file {self.state['output_file_name']}. " if self.state.get('input_code', False) else ""

        if self.state.get('force_code', False):
            msg_end_control = [self.make_user_message(f"{msg_1}Generate code to meet the specified requirements. Reply with {C_STOP_CODE} only if the file is not empty and it meets the defined requirements.")]
        else:
            msg_end_control = [self.make_user_message(f"{msg_1}Generate output for the file contents that is consistent with the specified requirements.  Reply with {C_STOP_CODE} only if the file is not empty and it meets the defined requirements.")]
        
        return msg_end_control
    

    def make_system_message(self, message):
        return {"role": "system", "content": message}
    

    def make_user_message(self, message):
        return {"role": "user", "content": message}


    async def generate_response(self):
        # Generate a response
        response = await llm.generate_chat_completion(self.message_log)

        self.print_to_system_log(f"RESPONSE: {response}")

        return response
    

    async def process_response(self, response):
        code = None
        
        # Check for code blocks
        if code_blocks := self.parse_code_blocks_tags(response):
            # TODO: Process multiple code blocks
            code = code_blocks[0]

        elif code_blocks := self.parse_code_blocks_markdown(response):
            code = code_blocks[0]

        else:
            # No code blocks, write response to output
            self.state['output'] = response

        if code and code["code"] != C_STOP_CODE:
            # Store the code to state
            self.state['input_code'] = code

        # Check if <DONE> is in response
        if (C_STOP_CODE in response) and self.run_epoch > 0:
            # Write code state to file
            res_ok = await self.store_code_file(self.state.get('input_code'))

            # Done, OR ARE WE?! (if we did not produce code output)
            self.run_b = not res_ok
            return
        

    def parse_code_blocks_markdown(self, message):
        # regex to parse type and code from markdowncode like this:
        # ```python
        # some code with multiple line breaks
        # ```
        regex_pattern = r'```(?P<type>.*?)\n(?P<code>.*?)```'
        return self.parse_code_blocks(message, regex_pattern)


    def parse_code_blocks_tags(self, message):
        # Define regex pattern to match different code blocks like this:
        # <output type="python">some code with multiple line breaks</output>
        # <cmd type="bash">some bash command</cmd>
        regex_pattern = r'<(?P<type>code|cmd|output) file_name=([\'"](?P<file_name1>[^\'"]+)[\'"]|\\\'(?P<file_name2>[^\\]+)\\\')>(?P<code>.*?)<\/(?P=type)>'
        return self.parse_code_blocks(message, regex_pattern)


    def parse_code_blocks(self, message, regex_pattern):
        # TODO: Add support for multiple code blocks

        # find all matches and put them in a list
        matches = re.findall(regex_pattern, message, re.DOTALL)

        if matches:
            code_blocks = []
            
            for match in matches:
                code = {}
                code['code'] = match[-1]
                code['type'] = match[0]

                if len(match) >2:
                    code['file_name'] = match[2] if match[2] else match[3]

                code_blocks.append(code)

            return code_blocks

        else:
            return None
    

    async def store_code_file(self, code):
        try:
            if isinstance(code, str):
                code = {
                    "file_name": self.state['output_file_name'],
                    "code": code
                }

            assert isinstance(code, dict), "Code must be a dict."
            assert "code" in code, "Code must have code."
            
            if code["code"] == "JOBDONE":
                return True
            
            if "file_name" not in code:
                code["file_name"] = self.state['output_file_name']

            # Create the directory if it does not exist
            if not os.path.exists(self.working_dir):
                os.makedirs(self.working_dir)

            # save code to file
            with open(os.path.join(self.working_dir, code['file_name']), "w") as f:
                f.write(code['code'])

            return True
        
        except AssertionError as e:
            print(f"Error: {e}")
            return False
        
        except Exception as e:
            traceback.print_exc()
            raise e
                

    def print_to_system_log(self, message):
        # Print the message to a file
        with open(os.path.join(C_WORKING_DIR, "system_log.txt"), "a") as f:
            # print message with a fomratted timestamp
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{message}\n\n")

