import traceback
from datetime import datetime
import llm
import os
import re
from pathlib import Path

C_WORKING_DIR = "~/temp/simple_coder"
C_CONFIG_CODER = "simple-coder.txt"
C_SYSTEM_FILE = "system-log.txt"
C_STOP_CODE = "JOBDONE"
C_MAX_EPOCH = 10

class SimpleCoder:
    def __init__(self, working_dir=C_WORKING_DIR, requirements=None, output_file_name=None, input_file_name_list=None, force_code=True, silent=False):
        self.working_dir = working_dir
        self.message_log = []

        self.state = {}
        self.state['requirements'] = requirements
        self.state['output_file_name'] = output_file_name
        self.state['input_file_name_list'] = input_file_name_list
        self.state['force_code'] = force_code

        self.run_b = True
        self.run_epoch = 0
        self.silent = silent

        self.get_config()
    

    def get_config(self, config_file=C_CONFIG_CODER):
        if not self.state.get('role_config', False):
            # get data from config file: confg/simple-coder.txt
            current_dir = os.path.dirname(os.path.realpath(__file__))
            with open(os.path.join(current_dir, "config", config_file), "r") as file:
                self.state['role_config'] = file.read()

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
            

    async def run(self):
        while self.run_b:
            if not self.silent:
                print(f"Epoch: {self.run_epoch}")
            
            await self.work()

            if self.run_epoch > C_MAX_EPOCH:
                # Write code state to file
                await self.store_code_file(self.state.get('input_code'))
                self.run_b = False
            
            self.run_epoch += 1

        return self.state.get('output_file_name', False)


    async def work(self):
        try:
            await self.compose_message_log()

            if self.message_log:
                response = await self.generate_response()

                await self.process_response(response)

                await self.store_code_file(self.state.get('input_code'))

        except Exception as e:
            print(traceback.print_exc())
            print(f"Error: {e}")
            raise e


    async def compose_message_log(self):
        try:
            if not self.state: raise Exception("State is not set")
            if not self.state.get('output_file_name', False): raise Exception("Output file name is not set")
            if not self.state.get('requirements', False): raise Exception("Requirements are not set")
            if not self.state.get('role_config', False): raise Exception("role_config are not set")

            # Compose message from role_config, file contents, file output, and requirements
            
            # role_config
            msg_role_config = self.make_message_role_config()
            
            # reference materials
            msg_file_data = self.make_message_materials()

            # input code
            msg_input_code = self.make_message_input()

            # requirements
            msg_requirements = self.make_message_requirements()

            # end control
            msg_end_control = self.make_message_endControl()

            # compose message
            self.message_log = msg_role_config + msg_file_data + msg_input_code + msg_requirements + msg_end_control
                    
        except Exception as e:
            print(traceback.print_exc())
            raise e
    

    def make_message_role_config(self):
        return [self.make_user_message(line) for line in self.state['role_config'].split("\n")]
    

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
        return [self.make_user_message(f"The following are requirements for our output file. <requirements>{self.state['requirements']}</requirements>")]


    def make_message_endControl(self):
        if self.state.get('input_code', False):
            # if input code exists, ask for modification
            msg_1 = f"Given the content in '{self.state['output_file_name']}' and the requirements provided, could you help me modify it to meet these requirements? Specifically, I would like to see a version of '{self.state['output_file_name']}' that includes all necessary changes and additions."

            msg_1b = f"Modify the content in '{self.state['output_file_name']}' to meet the provided requirements. Generate a version of '{self.state['output_file_name']}' that includes all necessary changes and additions."
        else:
            # if input code does not exist, ask for creation
            if self.state.get('force_code', False):
                # if force_code is set, ask for code creation specifically
                msg_1 = f"Given the requirements provided, could you help me create content for file named '{self.state['output_file_name']}' that fulfills these requirements? Specifically, I would like you to generate the code for '{self.state['output_file_name']}' that includes all necessary functionalities and features as per the requirements."

                msg1_b = f"Create a new file '{self.state['output_file_name']}' to fulfill the provided requirements. Generate code for '{self.state['output_file_name']}' including all necessary functionalities and features as per the requirements."

            else:
                # ask for creation of generic file
                msg_1 = f"Given the requirements provided, could you help me create content for file named '{self.state['output_file_name']}' that fulfills these requirements? Specifically, I would like you to generate the content for '{self.state['output_file_name']}' that includes all necessary elements as per the requirements."
                
                msg_1b = f"Create a new file '{self.state['output_file_name']}'. This file should fulfill the provided requirements. Generate content for '{self.state['output_file_name']}' including all necessary elements as per the requirements."

        msg_2 = f" Reply with {C_STOP_CODE} only if the file is not empty and it meets the defined requirements."

        msg_end_control = msg_1 + msg_2
        
        return [ self.make_user_message(msg_end_control) ]
    

    def make_system_message(self, message):
        return {"role": "system", "content": message}
    

    def make_user_message(self, message):
        return {"role": "user", "content": message}


    async def generate_response(self):
        # Generate a response
        response = await llm.generate_chat_completion(self.message_log)

        # log its
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
            # Stop code may be present inside the code
            code["code"] = code["code"].replace(C_STOP_CODE,"")

            # Store the code to state
            self.state['input_code'] = code["code"]

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
    

    async def store_code_file(self, code_block):
        try:
            if isinstance(code_block, str):
                code_block = {
                    "file_name": self.state['output_file_name'],
                    "code": code_block
                }

            if not isinstance(code_block, dict): raise Exception("code_block must be a dict.")
            if not "code" in code_block: raise Exception("code_block object must have code property.")
            
            if code_block["code"] == "JOBDONE":
                return True
            
            if "file_name" not in code_block:
                code_block["file_name"] = self.state['output_file_name']

            # clean the output
            code_text = code_block["code"].strip()
            # check if it's markdown code block
            if code_text[:3]=='```':
                # remove first line
                code_text = code_text[code_text.find('\n')+1:-3]

            self.write_to_file(code_block["file_name"], f"{code_text}\n")

            return True
        
        except AssertionError as e:
            print(f"Error: {e}")
            return False
        
        except Exception as e:
            traceback.print_exc()
            print (code_block)
            raise e
                

    def print_to_system_log(self, message):
        self.write_to_file(C_SYSTEM_FILE, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{message}\n\n", append=True)

    
    def get_file_contents(self, file_name):
        file_name = file_name.strip() or self.state.get('output_file_name', None)
        file_path = Path(self.working_dir) / file_name
        file_path = file_path.expanduser()
        file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(file_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            with open(file_path, 'w') as file:
                return ""
            

    def write_to_file(self, file_name, content, append=False):
        file_name = file_name.strip() or self.state.get('output_file_name', None)
        file_path = Path(self.working_dir) / file_name
        file_path = file_path.expanduser()
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'a' if append else 'w') as file:
            file.write(content)