from crewai import Crew, Process
from agents import job_site_scraper, job_filter_agent, job_analyzer, gemini_llm
from tasks import job_scraping_task, job_filtering_task, job_analysis_task

def create_job_search_crew():
    """Create and return the job search crew"""
    return Crew(
        agents=[job_site_scraper, job_filter_agent, job_analyzer],
        tasks=[job_scraping_task, job_filtering_task, job_analysis_task],
        process=Process.sequential,
        memory=True,
        cache=True,
        max_rpm=100,
        share_crew=True,
        manager_llm=gemini_llm
    )

def main():
    """Main CLI interface for the Remote Job Hunter"""
    print("Remote Job Hunter AI")
    print("=" * 50)
    print("Find the best remote opportunities across the web!\n")
    
    # Get user input
    job_title = input("💼 Job Title (required): ").strip()
    if not job_title:
        print("❌ Job title is required!")
        return
    
    min_salary = input("💰 Minimum Salary in USD (optional, press Enter to skip): ").strip()
    if not min_salary:
        min_salary = "0"
    
    country = input("🌍 Country preference (optional, press Enter for worldwide): ").strip()
    if not country:
        country = "worldwide"
    
    print(f"\nSearching for: '{job_title}'")
    print(f"Minimum Salary: ${min_salary}")
    print(f"Location: {country}")
    print("\n" + "=" * 50)
    
    # Create and run the crew
    crew = create_job_search_crew()
    
    try:
        print("Starting AI job search agents...")
        
        # Execute the job search
        result = crew.kickoff(inputs={
            'job_title': job_title,
            'min_salary': min_salary,
            'country': country
        })
        
        print("\nJob search completed!")
        print(f"Report saved to: remote_jobs_report.md")
        print(f"Summary: {result}")
        
        # Display quick summary
        print("\n" + "=" * 50)
        print("QUICK SUMMARY")
        print("=" * 50)
        print("Multi-site job search completed")
        print("Jobs filtered by your criteria") 
        print("Quality analysis and rankings generated")
        print("Application strategies provided")
        print("\nOpen 'remote_jobs_report.md' to see detailed results!")
        
    except Exception as e:
        print(f"Error during job search: {e}")
        print("Make sure you have set your GEMINI_API_KEY in .env file")

if __name__ == "__main__":
    main()