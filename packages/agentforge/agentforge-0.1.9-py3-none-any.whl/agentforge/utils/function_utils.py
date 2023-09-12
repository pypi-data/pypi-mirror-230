import os

from .storage_interface import StorageInterface
from ..logs.logger_config import Logger
from ..config import Config

from datetime import datetime
from pynput import keyboard
from typing import Dict, Any
from termcolor import colored, cprint
from colorama import init

init(autoreset=True)

logger = Logger(name="Function Utils")


class Functions:
    mode = None
    storage = None

    def __init__(self):
        self.mode = 'manual'
        self.config = Config()
        self.storage = StorageInterface()

        # Start the listener for 'Esc' key press
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

    def get_user_input(self):
        feedback = None
        msg = "\nPress Enter to Continue | Type 'auto' for Auto Mode | Type 'exit' to Exit | Or Provide Feedback: "

        # Check if the mode is manual
        if self.mode == 'manual':
            user_input = input(msg)
            if user_input.lower() == '':
                pass
            elif user_input.lower() == 'auto':
                self.set_auto_mode()
            elif user_input.lower() == 'exit':
                quit()
            else:
                feedback = user_input

        return feedback

    @staticmethod
    def get_feedback_from_status_results(status):
        if status is not None:
            completed = status['status']

            if 'not completed' in completed:
                result = status['reason']
            else:
                result = None

            return result

    def get_auto_mode(self):
        return self.mode

    def get_current_task(self):
        ordered_list = self.get_ordered_task_list()

        current_task = None
        # iterate over sorted_metadatas
        for i, metadata in enumerate(ordered_list['metadatas']):
            # check if the Task Status is not completed
            if metadata['Status'] == 'not completed':
                current_task = {'id': ordered_list['ids'][i], 'document': ordered_list['documents'][i],
                                'metadata': metadata}
                break  # break the loop as soon as we find the first not_completed task

        return current_task

    def get_ordered_task_list(self):
        # Load Tasks
        self.storage.storage_utils.select_collection("Tasks")

        task_collection = self.storage.storage_utils.load_collection({'collection_name': "Tasks",
                                                                      'include': ["documents", "metadatas"]})

        # first, pair up 'ids', 'documents' and 'metadatas' for sorting
        paired_up_tasks = list(zip(task_collection['ids'], task_collection['documents'], task_collection['metadatas']))

        # sort the paired up tasks by 'Order' in 'metadatas'
        sorted_tasks = sorted(paired_up_tasks, key=lambda x: x[2]['Order'])

        # split the sorted tasks back into separate lists
        sorted_ids, sorted_documents, sorted_metadatas = zip(*sorted_tasks)

        # create the ordered results dictionary
        ordered_list = {'ids': list(sorted_ids),
                        'embeddings': task_collection['embeddings'],
                        'documents': list(sorted_documents),
                        'metadatas': list(sorted_metadatas)}

        return ordered_list

    def get_task_list(self):
        return self.storage.storage_utils.load_collection({'collection_name': "Tasks",
                                                           'include': ["documents", "metadatas"]})

    def load_agent_data(self, agent_name):
        self.config.reload(agent_name)

        defaults = self.config.data['Defaults']
        objective = self.config.data['Objective']

        agent = self.config.agent
        api = agent.get('API', defaults['API'])
        params = agent.get('Params', defaults['Params'])

        # Initialize agent data
        agent_data: Dict[str, Any] = dict(
            name=agent_name,
            llm=self.config.get_llm(api),
            objective=objective,
            prompts=agent['Prompts'],
            params=params,
            storage=StorageInterface().storage_utils,
        )

        return agent_data

    def on_press(self, key):
        try:
            # If 'Esc' is pressed and mode is 'auto', switch to 'manual'
            if key == keyboard.Key.esc and self.mode == 'auto':
                cprint("\nSwitching to Manual Mode...", 'green', attrs=['bold'])
                self.mode = 'manual'
        except AttributeError:
            pass

    def prepare_objective(self):
        while True:
            user_input = input("\nDefine Objective (leave empty to use defaults): ")
            if user_input.lower() == '':
                return None
            else:
                self.config.data['Objective'] = user_input
                return user_input

    def print_primed_tool(self, tool_name, payload):
        tool_name = tool_name.replace('_', ' ')
        speak = payload['thoughts']['speak']
        reasoning = payload['thoughts']['reasoning']

        # Format command arguments
        command_args = ", ".join(
            [f"{k}='{v}'" if isinstance(v, str) else f"{k}={v}" for k, v in payload['command']['args'].items()]
        )

        command = f"{payload['command']['name']}({command_args})"

        # Create the final output string
        formatted_string = f"{speak}\n\n" \
                           f"Tool: {tool_name}\n" \
                           f"Command: {command}\n" \
                           f"Reasoning: {reasoning}"

        self.print_result(formatted_string, 'Primed Tool')

    def set_auto_mode(self):
        self.mode = 'auto'
        cprint(f"\nAuto Mode Set - Press 'Esc' to return to Manual Mode!", 'yellow', attrs=['bold'])

    def show_task_list(self, desc):
        objective = self.config.data['Objective']
        self.storage.storage_utils.select_collection("Tasks")

        task_collection = self.storage.storage_utils.collection.get()
        task_list = task_collection["metadatas"]

        # Sort the task list by task order
        task_list.sort(key=lambda x: x["Order"])
        result = f"Objective: {objective}\n\nTasks:\n"

        cprint(f"\n***** {desc} - TASK LIST *****\nObjective: {objective}", 'blue', attrs=['bold'])

        for task in task_list:
            task_order = task["Order"]
            task_desc = task["Description"]
            task_status = task["Status"]

            if task_status == "completed":
                status_text = colored("completed", 'green')
            else:
                status_text = colored("not completed", 'red')

            print(f"{task_order}: {task_desc} - {status_text}")
            result = result + f"\n{task_order}: {task_desc}"

        cprint(f"*****", 'blue', attrs=['bold'])

        self.log_tasks(result)

        return result

    @staticmethod
    def calculate_next_task_order(this_task_order):
        return int(this_task_order) + 1

    @staticmethod
    def handle_prompt_type(prompts, prompt_type):
        """Handle each type of prompt and return template and vars."""
        prompt_data = prompts.get(prompt_type, {})
        if prompt_data:
            return [(prompt_data['template'], prompt_data['vars'])]
        return []

    @staticmethod
    def log_tasks(tasks):
        filename = "./Logs/results.txt"
        with open(filename, "a") as file:
            file.write(tasks)

    @staticmethod
    def parse_tool_results(tool_result):
        if isinstance(tool_result, list):
            # Format each search result
            formatted_results = [f"URL: {url}\nDescription: {desc}\n---" for url, desc in tool_result]
            # Join all results into a single string
            final_output = "\n".join(formatted_results)
        else:
            final_output = tool_result

        return final_output

    @staticmethod
    def print_message(msg):
        cprint(f"{msg}", 'red', attrs=['bold'])

    @staticmethod
    def print_result(result, desc):
        # Print the task result
        cprint(f"***** {desc} *****", 'green', attrs=['bold'])
        print(result)
        cprint(f"*****", 'green', attrs=['bold'])

        # Save the result to a log.txt file in the /Logs/ folder
        log_folder = "Logs"
        log_file = "log.txt"

        # Create the Logs folder if it doesn't exist
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)

        # Save the result to the log file
        # self.write_file(log_folder, log_file, result)

    @staticmethod
    def remove_prompt_if_none(prompts, kwargs):
        prompts_copy = prompts.copy()
        for prompt_type, prompt_data in prompts_copy.items():
            required_vars = prompt_data.get('vars', [])
            # If there are no required vars or all vars are empty, we keep the prompt
            if not required_vars or all(not var for var in required_vars):
                continue
            for var in required_vars:
                if kwargs.get(var) is None:
                    prompts.pop(prompt_type)
                    break  # Exit this loop, the dictionary has been changed

    @staticmethod
    def render_template(template, variables, data):
        temp = template.format(
            **{k: v for k, v in data.items() if k in variables}
        )

        return temp

    @staticmethod
    def set_task_order(data):
        task_order = data.get('this_task_order')
        if task_order is not None:
            data['next_task_order'] = Functions.calculate_next_task_order(task_order)

    @staticmethod
    def show_task(data):
        if 'task' in data:
            cprint(f'\nTask: {data["task"]}', 'green', attrs=['dark'])

    def dyna_tool(self, tool_class, payload):
        import importlib
        self.print_message(f"\nRunning {tool_class} ...")

        command = payload['command']['name']
        args = payload['command']['args']
        tool_module = f"agentforge.tools.{tool_class}"

        try:
            tool = importlib.import_module(tool_module)
        except ModuleNotFoundError:
            raise ValueError(
                f"No tool module named '{tool_class}' found. Ensure the module name matches the Script name exactly.")

        # Check if the tool has a class named FileWriter (or any other tool name)
        # If it does, instantiate it, and then use the command method
        # Else, use the standalone function
        if hasattr(tool, tool_class):
            tool_instance = getattr(tool, tool_class)()
            command_func = getattr(tool_instance, command)
        else:
            command_func = getattr(tool, command)

        result = command_func(**args)

        self.print_result(result, f"{tool_class} Result")
        return result

    @staticmethod
    def extract_metadata(data):
        # extract the 'metadatas' key from results
        return data['metadatas'][0][0]

    @staticmethod
    def extract_outermost_brackets(string):
        count = 0
        start_idx = None
        end_idx = None

        for idx, char in enumerate(string):
            if char == '{':
                count += 1
                if count == 1:
                    start_idx = idx
            elif char == '}':
                count -= 1
                if count == 0 and start_idx is not None:
                    end_idx = idx
                    break

        if start_idx is not None and end_idx is not None:
            return string[start_idx:end_idx + 1]
        else:
            return None

    @staticmethod
    def string_to_dictionary(string):
        from ast import literal_eval as leval
        try:
            return leval(string)
        except Exception as e:
            raise ValueError(f"\n\nError while building parsing string to dictionary: {e}")
