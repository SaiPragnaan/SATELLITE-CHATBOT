from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain.tools import tool
from langchain.output_parsers import StructuredOutputParser, ResponseSchema,PydanticOutputParser
from langchain_core.output_parsers import JsonOutputParser
from langchain.agents import create_react_agent, AgentExecutor

from langchain_community.tools import TavilySearchResults, GoogleSerperResults,DuckDuckGoSearchResults,Tool
from langchain_community.utilities import GoogleSerperAPIWrapper,DuckDuckGoSearchAPIWrapper
from langchain_community.utilities.serpapi import SerpAPIWrapper
from langchain_core.messages import BaseMessage,SystemMessage,HumanMessage,AIMessage,ToolMessage

from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode,tools_condition

from typing import Optional, List, TypedDict, Dict
from typing_extensions import Annotated
from pydantic import BaseModel, Field

from langchain_google_genai import ChatGoogleGenerativeAI

import os

from dotenv import load_dotenv

from src.utils.helpers import read_txt_file

load_dotenv()

class BasicSatelliteData(BaseModel):
    altitude: Optional[str] = Field(description="Satellite altitude in kilometers, look for values with 'km' or 'kilometers'")
    altitude_source_reference: Optional[str] = Field(description="Source URLs used to find the altitude.")
    orbital_life_years: Optional[str] = Field(description="Orbital life or mission duration in years.")
    orbital_life_source_reference: Optional[str] = Field(description="Source URLs used to find orbital life.")
    launch_orbit_classification: Optional[str] = Field(description="Orbit classification such as GTO, LEO, or SSO.")
    launch_orbit_source_reference: Optional[str] = Field(description="Source URLs used to find orbit classification.")
    number_of_payloads: Optional[str] = Field(description="Count of payloads or instruments on the satellite.")
    number_of_payloads_source_reference: Optional[str] = Field(description="Source URLs used to find the number of payloads.")


class BasicMissionData:
    def __init__(self):
        self.llm=ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        serper_tool=GoogleSerperResults(api_wrapper=GoogleSerperAPIWrapper())
        tavily_tool = TavilySearchResults()
        duckduckgo_tool=DuckDuckGoSearchResults(api_wrapper=DuckDuckGoSearchAPIWrapper())

        self.tools=[serper_tool, tavily_tool,duckduckgo_tool]
        self.tools_names=[tool.name for tool in self.tools]

    def make_prompt(self):
        # Get the project root directory (2 levels up from agents)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        basic_prompt = read_txt_file(os.path.join(project_root, "src/prompts/basic_mission_prompt.txt"))
        if not basic_prompt:
            raise FileNotFoundError("basic_mission_prompt.txt not found")
        prompt_template = PromptTemplate(
            input_variables=["satellite_name", "format_instructions", "tools", "tool_names", "agent_scratchpad"],
            template=basic_prompt
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
        # Create response schemas for each field directly (without wrapper)
        response_schemas = [
            ResponseSchema(name="altitude", description="Satellite altitude in kilometers"),
            ResponseSchema(name="altitude_source_reference", description="Source URL for altitude data"),
            ResponseSchema(name="orbital_life_years", description="Orbital life in years"),
            ResponseSchema(name="orbital_life_source_reference", description="Source URL for orbital life data"),
            ResponseSchema(name="launch_orbit_classification", description="ISRO orbit classification (GTO, LEO, or SSO)"),
            ResponseSchema(name="launch_orbit_source_reference", description="Source URL for orbit classification"),
            ResponseSchema(name="number_of_payloads", description="Number of payloads on the satellite"),
            ResponseSchema(name="number_of_payloads_source_reference", description="Source URL for payload information")
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