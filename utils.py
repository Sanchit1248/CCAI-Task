import json
import ollama

def extract_parameters(query):
    """Returns normalized parameters with robust error handling."""
    prompt = f"""Extract college search parameters from this query as JSON:
    {{
        "institute": "full name or null",
        "program": "full program name or null",
        "exam": "JEE Advanced" or "JEE Mains",
        "marks": number or null,
        "percentile": number or null,
        "gender": "Gender-Neutral" or "Female-Only"
    }}
    
    Rules:
    1. IIT -> JEE Advanced, NIT -> JEE Mains
    2. Use complete official names for institutes
    3. Defaults: exam=JEE Advanced, gender=Gender-Neutral
    Query: "{query}"
    Return ONLY valid JSON:"""

    try:
        response = ollama.chat(
            model='llama3',
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.1, 'format': 'json'}
        )
        raw = response['message']['content'].strip()
        
        try:
            params = json.loads(raw)
        except json.JSONDecodeError:
            json_str = raw[raw.find('{'):raw.rfind('}')+1]
            params = json.loads(json_str)

        processed = {
            'institute': format_institute_name(params.get('institute')),
            'program': format_program_name(params.get('program')),
            'exam': detect_exam_type(params.get('institute'), params.get('exam')),
            'marks': safe_convert(params.get('marks')),
            'percentile': safe_convert(params.get('percentile')),
            'gender': format_gender(params.get('gender'))
        }

        if processed['institute'] == "Null":
            processed['institute'] = None

        if processed['marks'] is not None:
            predicted_rank = predict_rank(processed['marks'], processed['exam'])
            if not isinstance(predicted_rank, int):
                raise ValueError("Invalid rank prediction")
            processed['rank'] = predicted_rank

        return processed

    except json.JSONDecodeError as e:
        print(f"JSON Error: {str(e)}")
        return {'error': f"Failed to parse response: {raw}"}
    
    except Exception as e:
        print(f"Extraction Error: {str(e)}")
        return {'error': f"Parameter extraction failed: {str(e)}"}



# Helper Functions
def predict_rank(marks, exam_type):
    #rank prediction with intrapolation b/w marks
    try:
        data_file = (
            "data/adv_rank.json" 
            if exam_type == "JEE Advanced" 
            else "data/mains_rank.json"
        )
        
        with open(data_file) as f:
            rank_data = sorted(json.load(f), key=lambda x: x['Marks'])
        
        # Find bounding marks for interpolation
        lower = None
        upper = None
        
        for entry in rank_data:
            if entry['Marks'] <= marks:
                lower = entry
            else:
                upper = entry
                break
        
        # Exact match case
        if lower and lower['Marks'] == marks:
            return lower['Rank']
        
        # Interpolation case
        if lower and upper:
            mark_range = upper['Marks'] - lower['Marks']
            rank_range = upper['Rank'] - lower['Rank']
            return int(lower['Rank'] + ((marks - lower['Marks']) / mark_range) * rank_range)
        
        # Edge cases (marks outside dataset range)
        return rank_data[0]['Rank'] if marks < rank_data[0]['Marks'] else rank_data[-1]['Rank']
        
    except Exception as e:
        print(f"Rank prediction warning: {str(e)}")
        return None

def format_institute_name(name):
    if not name: return None
    name = name.title()
    if 'Iit' in name: return name.replace('Iit', 'IIT')
    if 'Nit' in name: return name.replace('Nit', 'NIT')
    return name

def format_program_name(program):
    if not program:
        return None
    # added
    program = program.replace("(4 Years)", "").replace("Bachelor of Technology", "").strip()
    return program.title()

def detect_exam_type(institute, current_exam):
    if current_exam: 
        return current_exam
    if institute and ('IIT' in institute or 'Indian Institute' in institute):
        return 'JEE Advanced'
    return 'JEE Mains'

def format_gender(gender):
    if not gender: return 'Gender-Neutral'
    return gender.title().replace(' ', '-')

def safe_convert(value):
    """Safely convert numbers"""
    try:
        if isinstance(value, (int, float)): return value
        if not value: return None
        return float(value) if '.' in str(value) else int(value)
    except:
        return None


with open('data/adv_seats.json') as f:
    adv_seats = json.load(f)

with open('data/mains_seats.json') as f:
    mains_seats = json.load(f)
 
def filter_seats(data, rank, institute=None, program=None, gender='Gender-Neutral'):
    filtered = []
    for entry in data:
        try:
            closing_rank = int(float(entry['Closing Rank'].replace(',', '')))

            #debug
            #print(f"Checking: {entry['Institute']} | Program: {entry['Academic Program Name']} | Closing Rank: {closing_rank} | Query Rank: {rank}")
            
            # Skip rank check first
            if rank > closing_rank:
                continue

            # Institute check (only if specified)
            if institute is not None:  # Explicit None check
                if entry.get('Institute') != institute:
                    continue

            # Normalize program names for comparison
            entry_program = entry.get('Academic Program Name', '').lower()
            query_program = program.lower() if program else None
            
            normalized_entry_program = entry_program.replace("(4 Years)", "").replace("Bachelor of Technology", "").strip()
            normalized_query_program = query_program.replace("(4 Years)", "").replace("Bachelor of Technology", "").strip() if query_program else None
            
            if program and normalized_query_program not in normalized_entry_program:
                #print(f"Skipped due to program mismatch ({normalized_query_program} not in {normalized_entry_program})")
                continue

            # Normalize gender for comparison
            entry_gender = entry.get('Gender', '').lower()
            query_gender = gender.lower()
            
            if query_gender not in entry_gender:
                #print(f"Skipped due to gender mismatch ({query_gender} not in {entry_gender})")
                continue

            filtered.append(entry)
        except Exception as e:
            print(f"Skipping entry due to error: {e}")
    
    return filtered



def get_college_options(query_json):
    exam_type = query_json.get('exam')
    rank = query_json.get('rank')
    institute = query_json.get('institute')
    program = query_json.get('program')
    gender = query_json.get('gender', 'Gender-Neutral')

    #print(f"Parameters passed to filter_seats: rank={rank}, institute={institute}, program={program}, gender={gender}")
    
    seat_data = adv_seats if exam_type == 'JEE Advanced' else mains_seats
    
    if institute:
        return filter_seats(seat_data, rank, institute=institute, gender=gender)
    elif program:
        return filter_seats(seat_data, rank, program=program, gender=gender)
    
    return []



def summarize_results(filtered_data):
    if not filtered_data:
        return "No options are available for your rank and preferences."

    summaries = []
    for entry in filtered_data:
        summaries.append(
            f"{entry['Academic Program Name']} at {entry['Institute']} "
            f"(Gender: {entry['Gender']}) "
            f"with ranks between {entry['Opening Rank']} and {entry['Closing Rank']}."
        )
    
    return "\n".join(summaries)

def generate_response(query_json, filtered_data):
    if not filtered_data:
        summary = "No options are available for your rank and preferences."
    else:
        summary = summarize_results(filtered_data)

    prompt = f"""
    You are an expert college advisor helping students explore engineering colleges in India.
    Here is the student's query:
    {query_json}

    Based on their JEE rank and preferences, here are some programs they are eligible for:
    {summary}

    For each program listed above, include:

    If the college is fixed and branch is variable:
    1. A brief overview of the program.
    2. Potential career opportunities after graduation.

    If the branch is fixed and the college is variable:
    1. A brief overview of the college.
    2. Description of the location of the college 

    Please provide the student their rank along with a friendly response without signing off formally (e.g., avoid phrases like 'Best regards' or 'Your Name').
    """

    try:
        response = ollama.chat(
            model='llama3',
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.7}
        )
        
        return response['message']['content']
    
    except Exception as e:
        return f"An error occurred while generating the response: {str(e)}"
    

def classify_query(query_json):
    if not query_json.get('rank'):
        return "general"
    elif not query_json.get('institute') and not query_json.get('program'):
        return "general"
    return "structured"

def handle_query(query, conversation_history):
    query_json = extract_parameters(query)
    query_type = classify_query(query_json)

    if query_type == "structured":
        exam_type = query_json.get('exam')
        rank = query_json.get('rank')
        institute = query_json.get('institute')
        program = query_json.get('program')
        gender = query_json.get('gender', 'Gender-Neutral')
        seat_data = adv_seats if exam_type == 'JEE Advanced' else mains_seats

        if institute:
            filtered_data = filter_seats(seat_data, rank, institute=institute, gender=gender)
        elif program:
            filtered_data = filter_seats(seat_data, rank, program=program, gender=gender)
        else:
            filtered_data = []

        response = generate_response(query_json, filtered_data)

        # LLM MEMORY IMPLEMENTED
        # Update conversation history
        conversation_history.append({'role': 'user', 'content': query})
        conversation_history.append({'role': 'assistant', 'content': response})
        
        return response, conversation_history

    else:
        try:
            # Extract last mentioned institute from conversation history
            last_institute = None
            for msg in reversed(conversation_history):
                if msg['role'] == 'user':
                    extracted_params = extract_parameters(msg['content'])
                    if extracted_params.get('institute'):
                        last_institute = extracted_params['institute']
                        break

            # Create a context-aware prompt
            prompt_context = f"The student has been asking about {last_institute}." if last_institute else "No specific institute mentioned yet."
            prompt = f"""
            You are an expert advisor for Indian engineering colleges ONLY. Never mention non-Indian institutions such as UBC or MIT.
            Current context: {prompt_context}
            Student's question: {query}
            """

            # Add user query and prompt to conversation history
            conversation_history.append({'role': 'user', 'content': prompt})
            response_obj = ollama.chat(
                model='llama3',
                messages=conversation_history,
                options={'temperature': 0.3} 
            )
            response = response_obj['message']['content']
            conversation_history.append({'role': 'assistant', 'content': response})
            return response, conversation_history

        except Exception as e:
            return f"An error occurred while handling your query: {str(e)}", conversation_history
