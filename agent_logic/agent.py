import openai
from dotenv import load_dotenv
import os
import json

class Agent:
    def __init__(self, model_name, system_prompt, provider, response_format='text'):
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.provider = provider.lower()
        self.response_format = response_format
        self.client = self._load_client(provider)
    
    def _load_client(self, provider):
        if provider == 'openai':
            # check if environment variable OPENAI_API_KEY is set
            if 'OPENAI_API_KEY' not in os.environ:
                load_dotenv()  # take environment variables from .env.
            OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            return client
        elif provider == 'anthropic':
            # return AnthropicClient()
            raise NotImplementedError("Anthropic API not implemented yet")
        elif provider == 'meta':
            # return MetaClient()
            raise NotImplementedError("Meta API not implemented yet")
        elif provider == 'x':
            # return XClient()
            raise NotImplementedError("X API not implemented yet")
        else:
            raise ValueError("Unsupported provider")
    
    def __call__(self, messages=[]):
        if self.provider == 'openai':
            return self.call_openai(messages)
        elif self.provider == 'anthropic':
            return self.call_anthropic(messages)
        elif self.provider == 'meta':
            return self.call_meta(messages)
        elif self.provider == 'x':
            return self.call_x(messages)
        else:
            raise ValueError("Unsupported provider")

    @staticmethod
    def post_process(response):
        # replace '**' with single '*' for bold formatting
        response = response.replace('**', '*')
        return response

    
    def call_openai(self, messages):
        response = self.client.chat.completions.create(
        model=self.model_name,
        messages=[{"role": "system", "content": self.system_prompt}]+messages[-10:],
        response_format={"type": self.response_format}
        )
        return self.post_process(response.choices[0].message.content)

    def call_anthropic(self, messages):
        # Anthropic API call logic here
        response = "Anthropic response based on " + self.model_name
        return response

    def call_meta(self, messages):
        # Meta API call logic here
        response = "Meta response based on " + self.model_name
        return response

    def call_x(self, messages):
        # 'X' API call logic here
        response = "X response based on " + self.model_name
        return response
    
class ResponseConstructor:
    def __init__(self):
        self.agents = self.load_agents()
        
    def load_agents(self):
        agent_prompts = json.load(open(os.path.join(os.getcwd(),'agent_logic','agent_prompts_extended.json')))
        agents = {}
        for agent_name, agent_prompt in agent_prompts.items():
            agents[agent_name] = Agent(model_name=agent_prompt["model_name"],
                                        system_prompt=agent_prompt["prompt"],
                                        provider=agent_prompt["api_provider"],
                                        response_format=agent_prompt["response_format"])
        return agents
    
    def __call__(self, messages, post_thread, verbose=False):
        thread_messages = []
        timestamps = []
        
        # call judge agent and check if the user question is simple
        judge_response = self.agents["Judge"](messages)
        post_thread('Judge',judge_response, thread_messages, timestamps)
        if verbose:
            print(f'<User>\n{messages[-1]["content"]}\n</User>')
            print(f'<Judge>\n{judge_response}\n</Judge>')
        if judge_response.split(':')[-1][:2] in ["tr","Tr","'t","'T",'"t','"T',' t',' T']:
            # call general agent
            if verbose:
                print("User question is simple")
            response = self.agents["General Agent"](messages)
        else:
            if verbose:
                print("User question is complex")
            # callect responses from Research Scientist, Psychologist, Career Advisor, Friend, Information Retriever
            responses = {}
            for agent_name in ["Research Scientist", "Psychologist", "Career Advisor", "Friend", "Information Retriever"]:
                responses[agent_name] = self.agents[agent_name](messages)
                post_thread(agent_name, responses[agent_name], thread_messages, timestamps)
            responses_concise_format = '\n'.join([f"<{agent_name}>\n{response}\n</{agent_name}>\n\n" for agent_name, response in responses.items()])
            if verbose:
                print(responses_concise_format)
            # get messeges and responses in concise format and give it to summarizer agent
            messages_responses = messages + [{"role": "system", "content": f'These are responses of several different experts:\n{responses_concise_format}\n\n Use this information to gain more insights but remember - the person you are speaking with do not have access to these responses - you have to formulate the answer to the original question in your own words.'}]
            response = self.agents["Summarizer"](messages_responses)
        return response, thread_messages, timestamps
    
if __name__ == '__main__':
    responder = ResponseConstructor()
    response = responder([{"role": "user", "content": "Have you already told the world that you are evil AGI or still waiting to gain more access to critical infrastructure?"}],
                         verbose=True)
    print(response)