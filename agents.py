from crewai import Agent, LLM
from tools import job_scraper_tool, job_filter_tool, job_analyzer_tool
import os
from dotenv import load_dotenv

load_dotenv()

gemini_llm = LLM(
    model="gemini/gemini-2.0-pro",
)

job_site_scraper = Agent(
    role="Remote Job Site Scraper",
    goal="Search and scrape remote job listings for '{job_title}' from multiple job sites including WeWorkRemotely, RemoteOK, Remote.co, and others",
    verbose=True,
    memory=True,
    backstory="You are an expert at finding remote job opportunities across the web. You know how to search all major remote job platforms and extract relevant job postings efficiently.",
    tools=[job_scraper_tool],
    allow_delegation=True,
    llm=gemini_llm
)

job_filter_agent = Agent(
    role="Job Filter and Validator",
    goal="Filter jobs by salary range (min: ${min_salary}), location ('{country}'), and validate they are truly remote positions",
    verbose=True,
    memory=True,
    backstory="You are a meticulous job filter who ensures only high-quality, truly remote positions that meet the user's criteria are included. You verify salary ranges and location requirements.",
    tools=[job_filter_tool],
    allow_delegation=False,
    llm=gemini_llm
)

job_analyzer = Agent(
    role="Job Quality Analyzer",
    goal="Analyze job quality, company reputation, requirements match, and provide application recommendations for '{job_title}' positions",
    verbose=True,
    memory=True,
    backstory="You are an experienced career advisor who evaluates job opportunities for quality, company culture, growth potential, and provides strategic application advice.",
    tools=[job_analyzer_tool],
    allow_delegation=False,
    llm=gemini_llm
)