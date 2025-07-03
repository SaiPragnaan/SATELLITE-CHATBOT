from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.agents import create_react_agent, AgentExecutor

from langchain_community.tools import TavilySearchResults, GoogleSerperResults, DuckDuckGoSearchResults
from langchain_community.utilities import GoogleSerperAPIWrapper, DuckDuckGoSearchAPIWrapper
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
from src.utils.helpers import read_txt_file

load_dotenv()

class LaunchDataModel(BaseModel):
    max_launch_mass_leo: str = Field(description="Max Launch Mass of Vehicle to LEO (Kg)")
    max_launch_mass_leo_source: str = Field(description="Source link for Max Launch Mass of Vehicle to LEO (Kg)")
    actual_launch_mass: str = Field(description="Actual Launch Mass Carried by the Vehicle (Kg)")
    actual_launch_mass_source: str = Field(description="Source link for Actual Launch Mass Carried by the Vehicle (Kg)")
    launch_success: str = Field(description="LAUNCH SUCCESS (1) / FAILURE (0)")
    vehicle_reusability: str = Field(description="VEHICLE REUSABILITY (0/1)")
    vehicle_reusability_details: str = Field(description="Vehicle Reusability Details (First stage/ second stage/ or more)")
    vehicle_reusability_source: str = Field(description="Vehicle Reusability Source link")

class LaunchData:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        serper_tool = GoogleSerperResults(api_wrapper=GoogleSerperAPIWrapper())
        tavily_tool = TavilySearchResults()
        duckduckgo_tool = DuckDuckGoSearchResults(api_wrapper=DuckDuckGoSearchAPIWrapper())
        self.tools = [serper_tool, tavily_tool, duckduckgo_tool]
        self.tools_names = [tool.name for tool in self.tools]

    def make_prompt(self):
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        launch_prompt = read_txt_file(os.path.join(project_root, "src/prompts/launch_data_prompt.txt"))
        if not launch_prompt:
            raise FileNotFoundError("launch_data_prompt.txt not found")
        prompt_template = PromptTemplate(
            input_variables=["satellite_name", "format_instructions", "tools", "tool_names", "agent_scratchpad"],
            template=launch_prompt
        )
        return prompt_template

    def initialize_agent(self):
        prompt_template = self.make_prompt()
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt_template
        )
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
        return self.agent_executor

    def get_format_instructions(self):
        response_schemas = [
            ResponseSchema(name="max_launch_mass_leo", description="Max Launch Mass of Vehicle to LEO (Kg)"),
            ResponseSchema(name="max_launch_mass_leo_source", description="Source link for Max Launch Mass of Vehicle to LEO (Kg)"),
            ResponseSchema(name="actual_launch_mass", description="Actual Launch Mass Carried by the Vehicle (Kg)"),
            ResponseSchema(name="actual_launch_mass_source", description="Source link for Actual Launch Mass Carried by the Vehicle (Kg)"),
            ResponseSchema(name="launch_success", description="LAUNCH SUCCESS (1) / FAILURE (0)"),
            ResponseSchema(name="vehicle_reusability", description="VEHICLE REUSABILITY (0/1)"),
            ResponseSchema(name="vehicle_reusability_details", description="Vehicle Reusability Details (First stage/ second stage/ or more)"),
            ResponseSchema(name="vehicle_reusability_source", description="Vehicle Reusability Source link")
        ]
        self.output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        return self.output_parser.get_format_instructions()

    def call(self, satellite_name):
        if not hasattr(self, 'agent_executor'):
            self.initialize_agent()
        input_data = {
            "satellite_name": satellite_name,
            "format_instructions": self.get_format_instructions(),
            "tools": self.tools,
            "tool_names": self.tools_names,
            "agent_scratchpad": ""
        }
        try:
            result = self.agent_executor.invoke(input_data)
            try:
                parsed_result = self.output_parser.parse(result["output"])
                return parsed_result
            except Exception as parse_error:
                print(f"Error parsing output for {satellite_name}: {parse_error}")
                return {
                    "error": f"Parsing error: {parse_error}",
                    "raw_output": result["output"],
                    "satellite_name": satellite_name
                }
        except Exception as e:
            print(f"Error extracting data for {satellite_name}: {e}")
            return {
                "error": str(e),
                "satellite_name": satellite_name,
                "data": None
            } 