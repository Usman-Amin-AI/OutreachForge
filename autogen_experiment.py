from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set API keys directly as environment variables
os.environ['SERPER_API_KEY'] = '3c75331dffc120acfa03b3bc75a4fbb3202c4927'
os.environ['GOOGLE_API_KEY'] = 'AIzaSyBy4PYRWiJglvaeslvjZWcRNUD_bAovcKA'

# Importing necessary tools and modules after installation
from crewai_tools import SerperDevTool
from crewai import Crew, Process, Agent, Task
from langchain_google_genai import ChatGoogleGenerativeAI

# Initialize the SerperDevTool for internet searching capabilities
tool = SerperDevTool(api_key=os.getenv('SERPER_API_KEY'))

# Initialize the language model using Google's Gemini models
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    verbose=True,
    temperature=0.5,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Creating a Senior Researcher agent with memory and verbose mode
news_researcher = Agent(
    role="Senior Researcher",
    goal='Uncover groundbreaking technologies in {topic}',
    verbose=True,
    memory=True,
    backstory=(
        "Driven by curiosity, you're at the forefront of "
        "innovation, eager to explore and share knowledge that could change "
        "the world."
    ),
    tools=[tool],
    llm=llm,
    allow_delegation=True
)

# Creating a Writer agent with custom tools responsible for writing a news blog
news_writer = Agent(
    role='Writer',
    goal='Narrate compelling tech stories about {topic}',
    verbose=True,
    memory=True,
    backstory=(
        "With a flair for simplifying complex topics, you craft "
        "engaging narratives that captivate and educate, bringing new "
        "discoveries to light in an accessible manner."
    ),
    tools=[tool],
    llm=llm,
    allow_delegation=False
)

# Research task definition
research_task = Task(
    description=(
        "Identify the next big trend in {topic}. "
        "Focus on identifying pros and cons and the overall narrative. "
        "Your final report should clearly articulate the key points, "
        "its market opportunities, and potential risks."
    ),
    expected_output='A comprehensive 3-paragraph-long report on the latest AI trends.',
    tools=[tool],
    agent=news_researcher,
)

# Writing task definition with language model configuration
write_task = Task(
    description=(
        "Compose an insightful article on {topic}. "
        "Focus on the latest trends and how it's impacting the industry. "
        "This article should be easy to understand, engaging, and positive."
    ),
    expected_output='A 4-paragraph article on {topic} advancements formatted as markdown.',
    tools=[tool],
    agent=news_writer,
    async_execution=False,
    output_file='new-blog-post.md'  # Example of output customization
)

# Forming the tech-focused crew with enhanced configuration
crew = Crew(
    agents=[news_researcher, news_writer],
    tasks=[research_task, write_task],
    process=Process.sequential,
)

# Starting the task execution process with enhanced feedback
result = crew.kickoff(inputs={'topic': 'AI in healthcare'})
print(result)

