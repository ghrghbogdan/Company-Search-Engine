import json
import ast

def matches_filter(record, filter_dict):
    """Checker for whether a given record matches the filter conditions."""
    for key, condition in filter_dict.items():
        
        if key == "$or":
            if not any(matches_filter(record, sub_cond) for sub_cond in condition):
                return False
            continue
        # Saving the value from the record for the current key    
        record_value = record.get(key)

        # We compute the logic based on the type of condition (dict for operators like $in, $gt, etc. or direct value for exact match)
        if isinstance(condition, dict):
            for op, op_value in condition.items():
                if op == "$in":
                    if record_value is None: return False
                    # Verify if record_value is in op_value (which is a list) - we need to handle both cases where record_value is a list or a single value
                    if isinstance(record_value, list):
                        if not any(item in op_value for item in record_value): return False
                    else:
                        if record_value not in op_value: return False
                        
                elif op == "$all":
                    if not isinstance(record_value, list): return False
                    if not all(item in record_value for item in op_value): return False
                    
                elif op == "$gt":
                    if record_value is None or record_value <= op_value: return False
                elif op == "$lt":
                    if record_value is None or record_value >= op_value: return False
                elif op == "$gte":
                    if record_value is None or record_value < op_value: return False
                elif op == "$lte":
                    if record_value is None or record_value > op_value: return False
                    
                elif op == "$contains":
                    if not record_value: return False
                    record_str = str(record_value).lower()
                    
                    if isinstance(op_value, list):
                        if not all(str(kw).lower() in record_str for kw in op_value): 
                            return False
                    else:
                        if str(op_value).lower() not in record_str: 
                            return False
                elif op == "$exists":
                    exists = record_value is not None
                    if exists != op_value: return False
        else:
            if record_value != condition:
                return False

    return True

def search_companies(jsonl_filepath, llm_filter):
    """Reads the .jsonl file line by line, applies the filter, and removes duplicates."""
    results = []
    seen_companies = set()
    
    with open(jsonl_filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
                
            record = json.loads(line)
            
            # 1. Preprocessing: Field extraction
            if 'address' in record and isinstance(record['address'], str):
                try:
                    addr_dict = ast.literal_eval(record['address'])
                    record['country_code'] = addr_dict.get('country_code')
                    record['town'] = addr_dict.get('town')
                    record['region_name'] = addr_dict.get('region_name')
                except (ValueError, SyntaxError):
                    pass
            
            # 2. Filter: Applying the LLM-generated filter to the record
            if matches_filter(record, llm_filter):
                try:
                    company_name = record.get('operational_name', '').strip().lower()
                except AttributeError:
                    try:
                        company_name = record.get('website', '').strip().lower()
                    except AttributeError:
                        company_name = ''

                if company_name and company_name not in seen_companies:
                    seen_companies.add(company_name)
                    results.append(record)
        
        if llm_filter == {}: 
            results = []
            f.seek(0) 
            for line in f:
                if not line.strip():
                    continue
                record = json.loads(line)
                try:
                    company_name = record.get('operational_name', '').strip().lower()
                except AttributeError:
                    try:
                        company_name = record.get('website', '').strip().lower()
                    except AttributeError:
                        company_name = ''

                if company_name and company_name not in seen_companies:
                    seen_companies.add(company_name)
                    results.append(record)
    return results
