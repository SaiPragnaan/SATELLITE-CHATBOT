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

class TechnicalSatelliteData(BaseModel):
    sensor_specifications: Optional[List[str]]      # ----->>>>
    sensor_specifications_source_reference: Optional[str] = Field(description="Source URLs used to find sensor specifications.")
    spectral_bands: Optional[List[str]] = Field(description="Spectral bands covered by the satellite sensors (e.g., visible, near-infrared, thermal, X-band, etc.).")
    spectral_bands_source_reference: Optional[str] = Field(description="Source URLs used to find spectral bands.")
    spatial_resolution: Optional[str] = Field(description="Spatial resolution of the satellite sensors (e.g., 1 meter, 10 meter, 20 meter, etc.).")
    spatial_resolution_source_reference: Optional[str] = Field(description="Source URLs used to find spatial resolution.")
    technological_breakthroughs: Optional[List[str]] = Field(description="Notable innovations, new technologies, or unique engineering features introduced in this mission.")
    tech_source_reference: Optional[str] = Field(description="Source URLs used to find technological breakthroughs.")
    satellite_type: Optional[str] = Field(description="Classify the satellite as one of the following based on its mission purpose: Communication, Earth Observation, Experimental, Navigation, or Science & Exploration.")


class TechnicalData:
    def __init__(self):
        self.llm=ChatGoogleGenerativeAI(model="gemini-2.0-flash")
        serper_tool=GoogleSerperResults(api_wrapper=GoogleSerperAPIWrapper())
        tavily_tool = TavilySearchResults()
        duckduckgo_tool=DuckDuckGoSearchResults(api_wrapper=DuckDuckGoSearchAPIWrapper())

        self.tools=[serper_tool, tavily_tool,duckduckgo_tool]
        self.tools_names=[tool.name for tool in self.tools]

    def make_prompt(self):
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        technical_prompt = read_txt_file(os.path.join(project_root, "src/prompts/technical_data_prompt.txt"))
        if not technical_prompt:
            raise FileNotFoundError("technical_data_prompt.txt not found")
        prompt_template = PromptTemplate(
            input_variables=["satellite_name", "format_instructions", "tools", "tool_names", "agent_scratchpad"],
            template=technical_prompt
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
            ResponseSchema(name="sensor_specifications", description="Detailed sensor specifications and capabilities"),
            ResponseSchema(name="sensor_specifications_source_reference", description="Source URLs used to find sensor specifications"),
            ResponseSchema(name="spectral_bands", description="Spectral bands covered by the satellite sensors"),
            ResponseSchema(name="spectral_bands_source_reference", description="Source URLs used to find spectral bands"),
            ResponseSchema(name="spatial_resolution", description="Spatial resolution of the satellite sensors"),
            ResponseSchema(name="spatial_resolution_source_reference", description="Source URLs used to find spatial resolution"),
            ResponseSchema(name="technological_breakthroughs", description="Notable innovations and technological features"),
            ResponseSchema(name="technological_breakthroughs_source_reference", description="Source URLs used to find technological breakthroughs"),
            ResponseSchema(name="satellite_type", description="Satellite classification based on mission purpose")
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
