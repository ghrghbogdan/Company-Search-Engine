from database_retrieval import search_companies
from ranking_system import rank_companies
from filter_generator import FilterGenerator
import json

def run_test(generator):
    while True:
        query = input(f"\nEnter a query (or 'exit' to quit): ")
        if query.lower() == 'exit':
            break
        result = generator.get_logic_filters(query)
        print(f"Generated filter: {json.dumps(result, indent=2)}")
        results = search_companies('companies.jsonl', result)
        ranked_results = rank_companies(query, results)
        print(f"\n{len(results)} companies found. Top 10 results:")
        for c in ranked_results[:10]: # Print first 10 results
            if c.get('operational_name') is not None: 
                print(f"- {c.get('operational_name')} (Revenue: {c.get('revenue')}, Employees: {c.get('employee_count')}, Relevance: {c.get('relevance_score')} )")
            else:
                print(f"- {c.get('website', 'N/A')} (Revenue: {c.get('revenue')}, Employees: {c.get('employee_count')}, Relevance: {c.get('relevance_score')} )")


gen = FilterGenerator()
run_test(gen)
