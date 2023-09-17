import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema.language_model import BaseLanguageModel
from pydantic import BaseModel, Field
from langchain_experimental.generative_agents import (
    GenerativeAgent,
    GenerativeAgentMemory,
)
from companion_agent.memory import AgentMemory




class CompanionAgent():
    """An Agent as a character with memory and innate characteristics."""

    

    def __init__(
            self,
            name: str,
            status: str,
            memory: AgentMemory,
            llm: BaseLanguageModel,
            age: Optional[int] = None,
            traits: str = "N/A",
            characters: Dict[str, dict] = {},
            verbose: bool = False,
            summary: str = "",  #: :meta private:
            summary_refresh_seconds: int = 3600,
            last_refreshed: datetime = datetime.now(),
            daily_summaries: List[str] = [],
    ):
        kwargs = {
            'name': name, 'status': status, 'memory': memory, 
            'llm': llm, 'age': age, 'traits': traits, 'characters': characters, 
            'verbose': verbose, 'summary': summary, 'summary_refresh_seconds': summary_refresh_seconds, 
            'last_refreshed': last_refreshed, 'daily_summaries': daily_summaries
        }
        self.__dict__.update(kwargs)

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    # LLM-related methods
    @staticmethod
    def _parse_list(text: str) -> List[str]:
        """Parse a newline-separated string into a list of strings."""
        lines = re.split(r"\n", text.strip())
        return [re.sub(r"^\s*\d+\.\s*", "", line).strip() for line in lines]

    def chain(self, prompt: PromptTemplate) -> LLMChain:
        return LLMChain(
            llm=self.llm, prompt=prompt, verbose=self.verbose, memory=self.memory
        )

    def _get_entity_from_observation(self, observation: str) -> str:
        if self.memory.language == 'en':
            prompt = PromptTemplate.from_template(
                "What is the observed entity in the following observation? {observation}"
                + "\nEntity="
            )
        else:
            prompt = PromptTemplate.from_template(
                "{observation} 中观察到的实体是谁？"
                + "\n实体="
            )
        return self.chain(prompt).run(observation=observation).strip()

    def _get_entity_action(self, observation: str, entity_name: str) -> str:
        if self.memory.language == 'en':
            prompt = PromptTemplate.from_template(
                "What is the {entity} doing in the following observation? {observation}"
                + "\nThe {entity} is"
            )
        else:
            prompt = PromptTemplate.from_template(
                "观察:{observation}\n"
                +"通过观察到的内容，请回答{entity}在做什么"
                + "\n{entity}在"
            )
        return (
            self.chain(prompt).run(entity=entity_name, observation=observation).strip()
        )

    def summarize_related_memories(self, observation: str, role: str = None, now: Optional[datetime] = None) -> str:
        """Summarize memories that are most relevant to an observation."""
        
        if not role: 
            entity_name = self._get_entity_from_observation(observation)
        else:
            entity_name = role
        entity_action = self._get_entity_action(observation, entity_name)
        if self.memory.language == 'en':
            prompt = PromptTemplate.from_template(
                """
                {q1}?
                Context from memory:
                {relevant_memories}
                Relevant context: 
                """
            )
            q1 = f"What is the relationship between {self.name} and {entity_name}"
            q2 = f"{entity_name} is {entity_action}"
        else:
            prompt = PromptTemplate.from_template(
                """
                {q1}？
                相关记忆：
                {relevant_memories}
                当前发生的事：
                {most_recent_memories}
                """
            )
            Q1 = f"""请推断并简述 {self.name} 和 {entity_name} 的关系。\n
                    请以如下格式进行返回 \n
                    {self.name} 和 {entity_name}的关系：\n """
            # q1 = f"{entity_name} 和 {self.name} 是什么关系"
            q1 = f"{self.name} 和 {entity_name} 是什么关系"
            Q2 = f"请概述 {entity_name} 的人物性格和立场"
            q2 = f"{entity_name} 做了什么"
            Q3 = f"{self.name}觉得{entity_name}为什么会{observation}"
            q3 = f"{entity_name}{observation}"
        
        current_time = datetime.now() if now is None else now
        if entity_name in self.characters:
            obj = self.characters[entity_name]
        else:
            self.characters[entity_name]={'last_refreshed':datetime.now(), 'force_refresh': False, 'description': None, 'relationship': None}
            obj = self.characters[entity_name]

        since_refresh = (current_time - obj['last_refreshed']).seconds
        results = []
        if (
            since_refresh >= self.summary_refresh_seconds
            or not obj['description']
            or not obj['relationship']
            or obj['force_refresh']
        ):
            obj['description'] = self.chain(prompt=prompt).run(q1=Q1, queries=[q1], most_recent_memories='', depth=0, importance_weight=0.0, threshold=0.8, top_k=10).strip()
            obj['relationship'] = self.chain(prompt=prompt).run(q1=Q2, queries=[q2], most_recent_memories='', depth=0, importance_weight=0.5, threshold=0.7, top_k=10).strip()
            obj['last_refreshed'] = current_time
        results += [obj['description']]
        results += [obj['relationship']]
        # 改deep retrive
        results += [self.chain(prompt=prompt).run(q1=Q3, queries=[q3], most_recent_memories='', depth=1, importance_weight=0.0, threshold=0.7, top_k=20).strip()]
        return '\n'.join(results)

    def _generate_reaction(
        self, observation: str, suffix: str, now: Optional[datetime] = None, role: str = None, addition: dict = None
    ) -> str:
        """React to a given observation or dialogue act."""
        if not addition: addition = {}
        addition_str = "\n".join([f"{key}: {value}" for key,value in addition.items()])
        if self.memory.language == 'en':
            prompt = PromptTemplate.from_template(
                "{agent_summary_description}"
                + "\nIt is {current_time}."
                + "\n{agent_name}'s status: {agent_status}"
                + f"\n{addition_str}" if addition_str else ""
                + "\nSummary of relevant context from {agent_name}'s memory:"
                + "\n{relevant_memories}"
                + "\nMost recent observations: {most_recent_memories}"
                + "\nObservation: {observation}"
                + "\n\n"
                + suffix
            )
        else:
            prompt = PromptTemplate.from_template(
                "{agent_summary_description}"
                + "\n现在是 {current_time}."
                + "\n{agent_name} 的当前状态是：{agent_status}"
                + f"\n{addition_str}" if addition_str else ""
                + "\n{agent_name} 的相关记忆概括如下："
                + "\n{relevant_memories}"
                + "\n正在发生的事：{most_recent_memories}"
                + "\n观察到：{observation}"
                + "\n\n"
                + suffix
            )
        agent_summary_description = self.get_summary(now=now)
        relevant_memories_str = self.summarize_related_memories(observation, role)
        current_time_str = (
            datetime.now().strftime("%B %d, %Y, %I:%M %p")
            if now is None
            else now.strftime("%B %d, %Y, %I:%M %p")
        )
        kwargs: Dict[str, Any] = dict(
            agent_summary_description=agent_summary_description,
            current_time=current_time_str,
            relevant_memories=relevant_memories_str,
            agent_name=self.name,
            observation=role+observation if role else observation,
            agent_status=self.status,
        )
        # consumed_tokens = self.llm.get_num_tokens(
        #     prompt.format( **kwargs)
        # )
        kwargs[self.memory.most_recent_memories_token_key] = ''
        return self.chain(prompt=prompt).run(**kwargs).strip()

    def _clean_response(self, text: str) -> str:
        return re.sub(f"^{self.name} ", "", text.strip()).strip()

    def generate_reaction(
        self, observation: str, now: Optional[datetime] = None
    ) -> Tuple[bool, str]:
        """React to a given observation."""
        call_to_action_template = (
            "Should {agent_name} react to the observation, and if so,"
            + " what would be an appropriate reaction? Respond in one line."
            + ' If the action is to engage in dialogue, write:\nSAY: "what to say"'
            + "\notherwise, write:\nREACT: {agent_name}'s reaction (if anything)."
            + "\nEither do nothing, react, or say something but not both.\n\n"
        )
        full_result = self._generate_reaction(
            observation, call_to_action_template, now=now
        )
        result = full_result.strip().split("\n")[0]
        # AAA
        self.memory.save_context(
            {},
            {
                self.memory.add_memory_key: f"{self.name} observed "
                f"{observation} and reacted by {result}",
                self.memory.now_key: now,
            },
        )
        if "REACT:" in result:
            reaction = self._clean_response(result.split("REACT:")[-1])
            return False, f"{self.name} {reaction}"
        if "SAY:" in result:
            said_value = self._clean_response(result.split("SAY:")[-1])
            return True, f"{self.name} said {said_value}"
        else:
            return False, result

    def generate_dialogue_response(
        self, observation: str, role: str = '', now: Optional[datetime] = None, addition: dict = None
    ) -> Tuple[bool, str]:
        """React to a given observation."""
        if self.memory.language == 'en':
            call_to_action_template = (
                "What would {agent_name} say? To end the conversation, write:"
                ' GOODBYE: "what to say". Otherwise to continue the conversation,'
                ' write: SAY: "what to say next"\n\n'
            )
        else:
            call_to_action_template = (
                "{agent_name} 会说什么？"
                '如果要结束对话回答： GOODBYE: "要说的话". '
                '其他情况请回答： SAY: "要说的话"\n\n'
            )
        print(f'strat:{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        self.memory.save_context(
            {},
            {
                self.memory.add_memory_key: observation,
                'role': role,
                'host': False,
                self.memory.now_key: now,
                
            },
        )
        print(f'save:{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        userstr = f"说：" if role else ''
        full_result = self._generate_reaction(
            f"{userstr}{observation}", call_to_action_template, now=now, role=role, addition=addition
        )
        print(f'generate:{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        result = full_result.strip().split("\n")[0]
        if "GOODBYE:" in result:
            farewell = self._clean_response(result.split("GOODBYE:")[-1])
            self.memory.save_context(
                {},
                {
                    self.memory.add_memory_key: farewell,
                    'role': self.name,
                    'host': True,
                    self.memory.now_key: now,
                    
                },
            )
            return False, f"{self.name}说：{farewell}"
        if "SAY:" in result:
            response_text = self._clean_response(result.split("SAY:")[-1])
            self.memory.save_context(
                {},
                {
                    self.memory.add_memory_key: response_text,
                    'role': self.name,
                    'host': True,
                    self.memory.now_key: now,
                },
            )
            return True, f"{response_text}"
        else:
            return False, result

    ######################################################
    # Agent stateful' summary methods.                   #
    # Each dialog or response prompt includes a header   #
    # summarizing the agent's self-description. This is  #
    # updated periodically through probing its memories  #
    ######################################################
    def _compute_agent_summary(self) -> str:
        """"""
        if self.memory.language == 'en': 
            prompt = PromptTemplate.from_template(
                "How would you summarize {name}'s core characteristics given the"
                + " following statements:\n"
                + "{relevant_memories}"
                + "Do not embellish."
                + "\n\nSummary: "
            )
            queries=[f"{self.name}'s core characteristics"]
        else:
            prompt = PromptTemplate.from_template(
                "相关信息:\n"
                + "{relevant_memories}\n"
                + "通过上述信息，你怎么概括{name}的关键性格特征\n"
                + "不要美化修饰"
                + "\n\n概括: "
            )
            queries=[f"{self.name}是谁"]

        # The agent seeks to think about their core characteristics.
        return (
            self.chain(prompt)
            .run(name=self.name, queries=queries, depth=0, importance_weight=0.3, threshold=0.7)
            .strip()
        )

    def get_summary(
        self, force_refresh: bool = False, now: Optional[datetime] = None
    ) -> str:
        """Return a descriptive summary of the agent."""
        current_time = datetime.now() if now is None else now
        since_refresh = (current_time - self.last_refreshed).seconds
        if (
            not self.summary
            or since_refresh >= self.summary_refresh_seconds
            or force_refresh
        ):
            self.summary = self._compute_agent_summary()
            self.last_refreshed = current_time
        age = self.age if self.age is not None else "N/A"
        if self.memory.language == 'en':
            return (
                f"Name: {self.name} (age: {age})"
                + f"\nInnate traits: {self.traits}"
                + f"\n{self.summary}"
            )
        else:
            return (
                f"姓名：{self.name} (年龄：{age})"
                + f"\n特征：{self.traits}"
                + f"\n{self.summary}"
            )

    def get_full_header(
        self, force_refresh: bool = False, now: Optional[datetime] = None
    ) -> str:
        """Return a full header of the agent's status, summary, and current time."""
        now = datetime.now() if now is None else now
        summary = self.get_summary(force_refresh=force_refresh, now=now)
        current_time_str = now.strftime("%B %d, %Y, %I:%M %p")
        return (
            f"{summary}\nIt is {current_time_str}.\n{self.name}'s status: {self.status}"
        )
