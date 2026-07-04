# Tools for a Customer Outreach Campaign

import os
from crewai import Agent, Task, Crew
from crewai_tools import DirectoryReadTool, FileReadTool, SerperDevTool, BaseTool
from langchain_groq import ChatGroq

import os
os.environ["SERPER_API_KEY"] = "3c75331dffc120acfa03b3bc75a4fbb3202c4927"


# Set the environment variable for the Groq API key
os.environ['GROQ_API_KEY'] = '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'

print(os.getenv('GROQ_API_KEY'))


# Initialize the ChatGroq model
llm = ChatGroq(
    api_key=os.getenv("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"),
    model="mixtral-8x7b-32768"
)

# # Creating Agents

# Define the agents
class SalesAgents:
    def __init__(self):
        self.llm = llm

    def sales_rep_agent(self):
        return Agent(
            role="Sales Representative",
            goal="Identify high-value leads that match any company's ideal customer profile",
            backstory=(
                "As a key member of the sales team, your mission is to explore various industries to uncover promising leads. "
                "Utilizing advanced tools and strategic insights, you analyze data, market trends, and industry activities to identify opportunities that can be beneficial for any company. "
                "Your role is essential in fostering valuable connections, driving growth, and ensuring that potential clients see the value in the services offered, "
                "no matter the industry or specific service."
            ),
            allow_delegation=False,
            verbose=True,
            llm=self.llm,
            max_iter=2
        )

    def lead_sales_rep_agent(self):
        return Agent(
            role="Lead Sales Representative",
            goal="Nurture leads with personalized, compelling communications on behalf of any company",
            backstory=(
                     "In the dynamic world of sales, you excel as the crucial link between potential clients and the services they need. "
                "By crafting tailored, engaging communications, you not only showcase the strengths of the service offered but also ensure that clients feel understood and valued. "
                "Your role is key in transforming interest into actionable outcomes, guiding leads from initial curiosity to securing the service offered, "
                "and adapting these strategies for any company looking to connect with similar clients."
            ),
            allow_delegation=False,
            verbose=True,
            llm=self.llm,
            max_iter=2
        )

# # Creating Tools

# Define the tools
directory_read_tool = DirectoryReadTool(directory='./content')
file_read_tool = FileReadTool()
search_tool = SerperDevTool()

class SentimentAnalysisTool(BaseTool):
    name: str = "Sentiment Analysis Tool"
    description: str = ("Analyzes the sentiment of text to ensure positive and engaging communication.")

    def _run(self, text: str) -> str:
        # Custom sentiment analysis logic
        return "positive"

sentiment_analysis_tool = SentimentAnalysisTool()

# **Creating Tasks**<br><br>
# The Lead Profiling Task is using crewAI Tools.

# Define the tasks
class SalesTasks:
    def lead_profiling_task(self):
        return Task(
            description=(
               "Conduct a thorough analysis of {lead_name}, a company in the {industry} sector that recently expressed interest in {service_type}. "
                "Leverage all available data sources to compile a comprehensive profile, highlighting key decision-makers, recent project developments, "
                "and specific needs related to {service_type}. This profile will assist in customizing the engagement strategy to align with {lead_name}'s specific goals and challenges. "
                "Ensure all information used is accurate and verified, making the profile adaptable for any company looking to approach {lead_name}."
            ),
            expected_output=(
                 "A detailed report on {lead_name}, covering company background, key personnel, recent projects, and specific needs related to {service_type}. "
                "The report should identify potential areas where the offered {service_type} can add value, with suggestions for customized engagement strategies "
                "that any company could employ when targeting {lead_name}."
            ),
            tools=[directory_read_tool, file_read_tool, search_tool],
            agent=SalesAgents().sales_rep_agent()
        )

    def personalized_outreach_task(self):
        return Task(
            description=(
                "Using insights from the lead profiling report on {lead_name}, create a series of customized email drafts for {key_decision_maker}, "
                "the {position} of {lead_name}. Each draft should clearly connect the offered {service_type} with their recent project developments and goals. "
                "The tone should be professional, engaging, and consistent with {lead_name}'s company culture. The email drafts should be adaptable for any company, "
                "ensuring that the communication aligns with the specific needs and objectives of {lead_name}, regardless of the industry or service."
            ),
            expected_output=(
               "A series of customized email drafts for {lead_name}, specifically directed at {key_decision_maker}. Each draft should effectively connect the offered {service_type} "
                "with their recent project developments and goals. The tone should be tailored to resonate with {lead_name}'s company culture, ensuring that the communication "
                "can be adapted for use by any company targeting similar clients."
            ),
            tools=[sentiment_analysis_tool, search_tool],
            agent=SalesAgents().lead_sales_rep_agent()
        )

# # Define the Crew

# Create the crew
crew = Crew(
    agents=[
        SalesAgents().sales_rep_agent(),
        SalesAgents().lead_sales_rep_agent()
    ],
    tasks=[
        SalesTasks().lead_profiling_task(),
        SalesTasks().personalized_outreach_task()
    ],
    verbose=2,
    memory=True
)

# # Define the inputs

inputs = {
    "lead_name": "COMET ESTIMATING LLC",
    "industry": "Contrution Estimaing COMPANY in USA",
    "key_decision_maker": "Waqar UL Hassan",
    "position": "President/CEO",
    "milestone": "product launch"
}

# Run the crew tasks
result = crew.kickoff(inputs=inputs)

# Print the result
print(result)

# The Personalized Outreach Task is using your custom Tool SentimentAnalysisTool, as well as crewAI's SerperDevTool (search_tool).

import gradio as gr


def run_tasks(lead_name, industry, key_decision_maker, position, milestone):
    # Set up inputs for the crew
    inputs = {
        "lead_name": lead_name,
        "industry": industry,
        "key_decision_maker": key_decision_maker,
        "position": position,
        "milestone": milestone
    }

    # Run the crew tasks
    result = crew.kickoff(inputs=inputs)
    return result

# Create the Gradio interface
iface = gr.Interface(
    fn=run_tasks,
    inputs=[
        gr.Textbox(label="Lead Name", placeholder="Enter the company name"),
        gr.Textbox(label="Industry", placeholder="Enter the industry"),
        gr.Textbox(label="Key Decision Maker", placeholder="Enter the name of the key decision maker"),
        gr.Textbox(label="Position", placeholder="Enter the position of the key decision maker"),
        gr.Textbox(label="Milestone", placeholder="Enter the milestone")
    ],
    outputs="text",
    title="Sales Task Runner",
    description="Enter the company details to run the sales tasks and get the results."
)

# Launch the Gradio app
iface.launch()

