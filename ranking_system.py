from sentence_transformers import SentenceTransformer, util

nlp_model = SentenceTransformer('all-MiniLM-L6-v2')

def rank_companies(user_query, filtered_companies, min_relevance=25):
    """
    Ranks companies using the semantic similarity between the query and the company data.
    """
    if not filtered_companies:
        return []

    # Convert the user query into a vector
    query_embedding = nlp_model.encode(user_query, convert_to_tensor=True)
    
    scored_companies = []
    
    for company in filtered_companies:
        # Build the context string for the company
        
        name = company.get('operational_name', '')
        if name is None:
            name = company.get('website', '') 
        desc = company.get('description', '')
        
        markets = ", ".join(company.get('target_markets') or [])
        offerings = ", ".join(company.get('core_offerings') or [])
        
        company_text = f"{name} operates in {markets}. Offerings: {offerings}. Description: {desc}"
        
        company_embedding = nlp_model.encode(company_text, convert_to_tensor=True)
        
        score = util.cos_sim(query_embedding, company_embedding).item()
        
        relevance_percent = round(score * 100, 2)
        

        if relevance_percent >= min_relevance:
            company['relevance_score'] = relevance_percent
            scored_companies.append(company)
        
    # Sort the list in descending order (most relevant first)
    scored_companies = sorted(scored_companies, key=lambda x: x['relevance_score'], reverse=True)
    
    return scored_companies