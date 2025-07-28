from crewai import Task
from tools import job_scraper_tool, job_filter_tool, job_analyzer_tool
from agents import job_site_scraper, job_filter_agent, job_analyzer

job_scraping_task = Task(
    description="Search for remote '{job_title}' positions across major remote job platforms including WeWorkRemotely, RemoteOK, Remote.co, AngelList, FlexJobs, and Indeed. Extract job titles, companies, descriptions, salary info, and application links.",
    expected_output="Comprehensive list of remote job opportunities with detailed information including job titles, company names, job descriptions, salary ranges, requirements, and application URLs.",
    tools=[job_scraper_tool],
    agent=job_site_scraper
)

job_filtering_task = Task(
    description="Filter the scraped jobs to include only positions that: 1) Are truly remote (not hybrid), 2) Match salary requirements (min ${min_salary} if specified), 3) Match location preferences ('{country}' or worldwide), 4) Are relevant to '{job_title}' role.",
    expected_output="Filtered and validated list of remote jobs that meet all specified criteria, with salary and location requirements verified.",
    tools=[job_filter_tool],
    agent=job_filter_agent
)

job_analysis_task = Task(
    description="Analyze each filtered job for: 1) Company reputation and stability, 2) Job requirements vs user profile match, 3) Salary competitiveness, 4) Growth opportunities, 5) Application difficulty/strategy. Rank jobs by overall quality and fit.",
    expected_output="Comprehensive job analysis report with rankings, company insights, application strategies, and personalized recommendations for the best remote '{job_title}' opportunities.",
    tools=[job_analyzer_tool],
    agent=job_analyzer,
    output_file='remote_jobs_report.md'
)