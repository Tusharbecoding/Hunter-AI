from crewai.tools import tool
import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import quote, urljoin
from datetime import datetime

@tool("Remote Job Site Scraper")
def job_scraper_tool(job_title: str) -> str:
    """Scrape remote job listings from multiple job sites for the specified job title."""
    
    all_jobs = []
    search_term = quote(job_title.lower())
    
    def scrape_weworkremotely():
        """Scrape WeWorkRemotely.com"""
        try:
            url = f"https://weworkremotely.com/remote-jobs/search?term={search_term}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                jobs = soup.find_all('li', class_='feature')
                
                for job in jobs[:10]:  # Limit to first 10 results
                    try:
                        title_elem = job.find('span', class_='title')
                        company_elem = job.find('span', class_='company')
                        link_elem = job.find('a')
                        
                        if title_elem and company_elem and link_elem:
                            all_jobs.append({
                                'title': title_elem.get_text().strip(),
                                'company': company_elem.get_text().strip(),
                                'url': 'https://weworkremotely.com' + link_elem.get('href'),
                                'source': 'WeWorkRemotely',
                                'location': 'Remote',
                                'description': 'Remote position'
                            })
                    except Exception as e:
                        continue
            
            print(f"Scraped {len([j for j in all_jobs if j['source'] == 'WeWorkRemotely'])} jobs from WeWorkRemotely")
        except Exception as e:
            print(f"Error scraping WeWorkRemotely: {e}")
    
    def scrape_remoteok():
        """Scrape RemoteOK.io"""
        try:
            url = f"https://remoteok.io/remote-{search_term}-jobs"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                jobs = soup.find_all('tr', class_='job')
                
                for job in jobs[:10]:  # Limit to first 10 results
                    try:
                        title_elem = job.find('h2', itemprop='title')
                        company_elem = job.find('h3', itemprop='name')
                        link_elem = job.find('a', itemprop='url')
                        salary_elem = job.find('span', class_='salary')
                        
                        if title_elem and company_elem:
                            job_data = {
                                'title': title_elem.get_text().strip(),
                                'company': company_elem.get_text().strip(),
                                'source': 'RemoteOK',
                                'location': 'Remote',
                                'description': 'Remote position'
                            }
                            
                            if link_elem:
                                job_data['url'] = 'https://remoteok.io' + link_elem.get('href')
                            
                            if salary_elem:
                                job_data['salary'] = salary_elem.get_text().strip()
                            
                            all_jobs.append(job_data)
                    except Exception as e:
                        continue
            
            print(f"Scraped {len([j for j in all_jobs if j['source'] == 'RemoteOK'])} jobs from RemoteOK")
        except Exception as e:
            print(f"Error scraping RemoteOK: {e}")
    
    def scrape_remote_co():
        """Scrape Remote.co"""
        try:
            url = f"https://remote.co/remote-jobs/search/?search_keywords={search_term}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                jobs = soup.find_all('div', class_='card')
                
                for job in jobs[:10]:  # Limit to first 10 results
                    try:
                        title_elem = job.find('h3')
                        company_elem = job.find('p', class_='company')
                        link_elem = job.find('a')
                        
                        if title_elem and company_elem and link_elem:
                            all_jobs.append({
                                'title': title_elem.get_text().strip(),
                                'company': company_elem.get_text().strip(),
                                'url': urljoin('https://remote.co', link_elem.get('href')),
                                'source': 'Remote.co',
                                'location': 'Remote',
                                'description': 'Remote position'
                            })
                    except Exception as e:
                        continue
            
            print(f"Scraped {len([j for j in all_jobs if j['source'] == 'Remote.co'])} jobs from Remote.co")
        except Exception as e:
            print(f"Error scraping Remote.co: {e}")

    print(f"Searching for '{job_title}' remote positions...")
    
    scrape_weworkremotely()
    time.sleep(1)  # Be respectful to servers
    
    scrape_remoteok()
    time.sleep(1)
    
    scrape_remote_co()
    time.sleep(1)
    
    print(f"Total jobs found: {len(all_jobs)}")
    
    return json.dumps(all_jobs, indent=2)

@tool("Job Filter and Validator")
def job_filter_tool(jobs_data: str, min_salary: str = "0", country: str = "worldwide") -> str:
    """Filter jobs by salary range, location, and validate they are truly remote positions."""
    
    try:
        jobs = json.loads(jobs_data)
    except:
        return "Error: Invalid jobs data format"
    
    filtered_jobs = []
    min_sal = int(min_salary) if min_salary.isdigit() else 0
    
    for job in jobs:

        location = job.get('location', '').lower()
        title = job.get('title', '').lower()
        description = job.get('description', '').lower()
        
        is_remote = any(keyword in location + ' ' + title + ' ' + description for keyword in [
            'remote', 'worldwide', 'anywhere', 'work from home', 'distributed'
        ])
        
        if not is_remote:
            continue
        
        if country.lower() != 'worldwide':
            location_text = location + ' ' + description
            if country.lower() not in location_text and 'worldwide' not in location_text:
                continue
        

        salary_text = job.get('salary', '')
        if min_sal > 0 and salary_text:
            salary_numbers = re.findall(r'\$?[\d,]+', salary_text)
            if salary_numbers:
                try:
                    max_salary = max([int(s.replace('$', '').replace(',', '')) for s in salary_numbers])
                    if max_salary < min_sal:
                        continue
                except:
                    pass 
        
        job['filter_reason'] = f"Matches criteria: Remote={is_remote}, Location={country}, Salary>=${min_sal}"
        filtered_jobs.append(job)
    
    print(f"Filtered to {len(filtered_jobs)} jobs matching criteria")
    return json.dumps(filtered_jobs, indent=2)

@tool("Job Quality Analyzer")
def job_analyzer_tool(filtered_jobs_data: str, job_title: str) -> str:
    """Analyze job quality, company reputation, and provide application recommendations."""
    
    try:
        jobs = json.loads(filtered_jobs_data)
    except:
        return "Error: Invalid filtered jobs data"
    
    analyzed_jobs = []
    
    for job in jobs:
        title = job.get('title', '')
        company = job.get('company', '')
        salary = job.get('salary', 'Not specified')
        source = job.get('source', '')
        
        quality_score = 50 
        
        if 'salary' in job and job['salary']:
            quality_score += 20
        
        if any(level in title.lower() for level in ['senior', 'lead', 'principal', 'staff']):
            quality_score += 15
        
        if source in ['WeWorkRemotely', 'RemoteOK', 'Remote.co']:
            quality_score += 10
        
        if source == 'Demo':
            quality_score = 85 + (len(analyzed_jobs) * 2) 
        
        difficulty = "Medium"
        if any(word in title.lower() for word in ['senior', 'lead', 'principal']):
            difficulty = "High"
        elif any(word in title.lower() for word in ['junior', 'entry', 'associate']):
            difficulty = "Low"
        
        strategies = [
            "Tailor resume to highlight remote work experience",
            "Emphasize relevant technical skills in cover letter",
            "Research company culture and values before applying",
            "Prepare for video interview setup and remote work questions"
        ]
        
        analyzed_job = {
            **job,
            'quality_score': min(quality_score, 100),
            'application_difficulty': difficulty,
            'application_strategies': strategies,
            'recommendation': f"Good fit for {job_title} role" if quality_score > 70 else f"Consider for {job_title} position",
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        analyzed_jobs.append(analyzed_job)
    
    analyzed_jobs.sort(key=lambda x: x['quality_score'], reverse=True)
    
    print(f"Analyzed {len(analyzed_jobs)} jobs with quality scores")
    return json.dumps(analyzed_jobs, indent=2)