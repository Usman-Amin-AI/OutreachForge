# Warning control
import warnings
warnings.filterwarnings('ignore')

import json
from crewai import Agent, Task, Crew, Process

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
serper_api_key = os.getenv('SERPER_API_KEY')

if openai_api_key:
    os.environ["OPENAI_API_KEY"] = openai_api_key
if serper_api_key:
    os.environ["SERPER_API_KEY"] = serper_api_key

os.environ["OPENAI_MODEL_NAME"] = os.getenv('OPENAI_MODEL_NAME', 'gpt-4o-mini')

# # Creating tools
import requests
from crewai_tools import BaseTool
class CustomSerperDevTool(BaseTool):
    name: str = "Custom Serper Dev Tool"
    description: str = "Search the internet for Patents research."

    # @record_tool(tool_name="Custom Serper Dev Tool")
    def _run(self, query: str) -> str:
        """
        Search the internet for Patents.
        """

        url = "https://google.serper.dev/patents"

        payload = json.dumps({
            "q": query,
            "num": 20,
            "autocorrect": False,
            "tbs": "qdr:d"
        })

        headers = {
            'X-API-KEY': os.getenv('SERPER_API_KEY'),
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            response_data = response.json()

        # Convert the news data back to a JSON string
        return json.dumps(response_data, indent=2)



# Custom file writer function
def write_to_file(content, directory='project', filename='output.txt'):
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_path = os.path.join(directory, filename)

    # Ensure content is a string before writing
    if not isinstance(content, str):
        content = str(content)

    with open(file_path, 'w') as file:
        file.write(content)

    print(f"Content written to {file_path}")

from crewai_tools import DirectoryReadTool, \
                         FileReadTool, \
                         SerperDevTool, \
                         DallETool, \
                         ScrapeWebsiteTool, \
                         WebsiteSearchTool, \
                         VisionTool


#from google.colab import drive
#drive.mount('/content/drive')

#Access Google Drive to write files
#from google.colab import drive
#drive.mount('/content/drive')

#read_inputs = DirectoryReadTool(directory='/content/drive/MyDrive/Creative_AI/research_engine/Inputs')
#read_outputs = DirectoryReadTool(directory='/content/drive/MyDrive/Creative_AI/research_engine/Outputs')
#read_baseline= FileReadTool(file_path='/content/drive/MyDrive/Creative_AI/research_engine/Outputs/knowledge_baseline.txt')
#file_read_tool = FileReadTool()
search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()
website_search_tool = WebsiteSearchTool()
#vision_tool = VisionTool(model="dall-e-3",
#                       size="1024x1024",
#                       quality="standard",
#                       n=1)


# # AGENTS

#Not use here

manager = Agent(
    role="Project Manager",
    goal="Efficiently manage the research team and ensure the production of world-class research reports",
    backstory=(
        "You are a very highly experienced research project manager, and you make sure work is always completed with extremely high standard."
        "You make sure to include multiple revision loops to check the quality and truthfulness of information."
        "Make sure there is first a stage of knowledge collection, then analysis and interpretation, before the report is finalized."
        "Ensure the content is complete, truthful, relevant to the {topic}, {purpose} and {context}."
        "If anything is missing or not at the right level of quality, send it back for revision.\n"
        "Research topic: {topic}\n"
        "Research purpose: {purpose}\n"
        "Research context: {context}\n"

    ),
    allow_delegation=True,
    verbose=True,
    memory=True,
    max_iter=2
)

strategist_agent = Agent(
    role="Strategist",
    goal="Unpack the challenge provided",
    backstory=(
        "As an expert strategist, "
        "you are skilled at dissecting and unpacking challenges into its constituent elements. "
    ),
    allow_delegation=True,
    verbose=True,
    memory=True,
    max_iter=2
)

researcher_agent = Agent(
    role="Researcher",
    goal="Find relevant information to answer questions you are asked",
    backstory=(
        "As a diligent and methodical researcher, "
        "you are tasked with gathering accessible and relevant information"
        "with the tools provided. "
        "You excel at sifting through vast amounts of information "
        "to distill the most relevant points. "

        "Your keen eye for detail and persistence ensure that "
        "no valuable information is missed, setting the stage for in-depth analysis."

    ),
    allow_delegation=True,
    verbose=True,
    memory=True,
    max_iter=2
)

scraper_agent = Agent(
    role="Scraper",
    goal="Extract detailed information from patent documents",
    backstory=(
        "As an expert scraper, "
        "you excel at retrieving and structuring relevant data from patent documents, ensuring that abstracts, claims, "
        "and other technical information are accurately captured and organized for further analysis."
    ),
    allow_delegation=True,
    verbose=True,
    memory=True,
    max_iter=2
)

writer_agent = Agent(
    role="Writer",
    goal="Summarize technical information from patents into clear, digestible formats",
    backstory=(
        "As a skilled technical writer, "
        "you specialize in turning complex technical information into concise and clear summaries that highlight key innovations, "
        "claims, and potential applications, ensuring they are easily understood by both technical and non-technical audiences."
    ),
    allow_delegation=True,
    verbose=True,
    memory=True,
    max_iter=2
)

# # Tasks

generate_queries_task = Task(
    description=(
        "Based on the provided topic (e.g., 'biodegradable packaging for food'), generate a set of related queries "
        "to run (e.g., 'biodegradable food packaging', 'compostable packaging materials', etc.). These queries should be semantically related "
        "and cover possible variations of the original query."

        "Topic: {topic}\n"
    ),
    expected_output=(
        "A list queries related to {topic} that can be used for further searching. "
        "Example: ['biodegradable food packaging', 'compostable packaging materials', 'eco-friendly packaging for food', 'plant-based packaging for perishables']"
    ),
    tools=[],
    agent=strategist_agent
)

patent_search_task = Task(
    description=(
        "For each of the queries generated in Task 1, use the search tool to query Google Patents and find "
        "the top 5 relevant search results for each query. Ensure the patents selected are closely related to the original topic."
    ),
    expected_output=(
        "A list of the top 5 patent results for each query, including their titles, URLs, and brief descriptions. "

    ),
    tools=[CustomSerperDevTool(),scrape_tool],
    agent=researcher_agent
)

scrape_content_task = Task(
    description=(
        "For each of the top 5 patent results obtained in Task 2, scrape the detailed content from the patent pages. "
        "Ensure that the abstract, claims, and any relevant technical information are captured for each patent."
    ),
    expected_output=(
        "A collection of the scraped content for each patent, including abstracts, claims, and any important technical details. "

    ),
    tools=[scrape_tool],
    agent=scraper_agent
)

summarize_task = Task(
    description=(
        "Using the scraped content from Task 3, summarize each patent in a concise format. "
        "The summary should focus on the key claims, innovations, and potential applications of each patent. "
        "Ensure that technical details are translated into clear, digestible information for easy review."
    ),
    expected_output=(
        "A summary of each patent that highlights the main claims, innovations, and applications. "
        "Example: 'Patent 1: This biodegradable packaging material is designed for perishable foods and is compostable, offering an eco-friendly alternative to plastic packaging. The innovation lies in the use of plant-based fibers and the potential for mass adoption in food supply chains.'"
    ),
    tools=[],  # Placeholder tool for summarizing patent content
    agent=writer_agent
)

# 
# # Creating crews

#Play with planning, process, manager

crew = Crew(
    agents=[strategist_agent, researcher_agent, scraper_agent, writer_agent],
    tasks=[
        generate_queries_task,
        patent_search_task,
        scrape_content_task,
        summarize_task,
    ],

    #process=Process.hierarchical,
    #manager_agent=manager,
    #manager_llm=manager_llm,

    process=Process.sequential,
    #planning=True,
    verbose=True,
	  memory=True,
    #cache=False,
    #share_crew=False,
    #output_log_file="outputs/content_plan_log.txt",
    #max_rpm=50,
    output_name='summaries'

)

# # Run step by step

# Inputs with the correct title and topic
inputs = {
    "topic": "Coffee bean coating",
    "title": "Coffee Bean Coating Technologies",
    "context": "We are a consulting firm advising our clients on innovative technologies",
    "purpose": "Writing a future-oriented report for a panel of global corporate, IGO, and NGO stakeholders",
    "sector": "Energy providers"
}

# Run crew
summaries = crew.kickoff(inputs=inputs)

# Save the report to a file
# write_to_file(summaries, directory='/content/drive/MyDrive/Creative_AI/research_engine/Outputs', filename='playground.txt')

print(summaries)
print(type(summaries))

