
def get_the_index_retrieval_prompt(pdf_text):
    PROMPT = f""" Using {pdf_text} as context, extract the headings and subheadings.
        - Extract the main subject and its attributes with the appropriate names.
        - Ensure that the names use the appropriate electrical ans energy industry terms and legal terms for the main subject and attributes.
        - Validate the main subject name and attribute name against a predefined legal and manufacturing lexicon to ensure correctness.
        - If the names do not match the lexicon, attempt to infer the correct term based on context.
        - split by comma and ensure that the names are not generic terms or abbreviations.
        - Ensure that the names are not generic terms or abbreviations.
        - Ensure that the names are not placeholders or temporary names.
        - Ensure that the names are not common nouns or verbs.  
        - Ensure that the names are not empty.
        - Ensure that the names are not unknown.
        - Extract the business names and any other information in the text.
        - Ensure that all ' and " are removed or replaces with empty string.
        - ensure that the names do not contain any special characters for example replace - with _
        - Start with an alphabetic character.
        - Contain only alphanumeric characters and underscores (`_`).
        - Avoid starting with numbers or special characters.
        - Ensure names are not placeholders, abbreviations, or invalid terms.
        - Validating names against predefined lexicons.
        - Ensure that csv like directors, officers, employees, agents, solicitors, accountants, consultants, and financial or other advisors is split into separate eSSSSntities 

        Use the following Instructions:
        - Do not summarize the text; use it verbatim.
        - Do not change the text or its structure.
        - Do not add any extra text, explanation, or information.
        - Return as a list of key points.
          
        """
    
    return PROMPT

def get_ontology_prompt(content):
    PROMPT = f"""
        You are tasked with extracting entities and relationships suitable for ontology building from the following text.

        ### Input:
        {content}

        Use the given text only do not make any assumptions or alter the structure.
        Do not change business names or any other information in the text.


        ---

        ### Response_Format:
        Return the response strictly in the following JSON format:

        
        ```json
        {{
            "entities": [
                {{
                    "name": "Entity_Name",
                    "type": "Entity_Type"
                }}
            ],
            "relationships": [
                {{
                    "from": "Entity_Name",
                    "to": "Related_Entity",
                    "type": "Type_of_Relationship"
                }}
            ]
        }}
        ```
        ---

        ### Guidelines:

        1. **Extract the Entities:**  
        - Extract the following as entities:
            - Business names
            - Relevant business vocabulary
            - Main Subject
        - Split the above by comma and ensure that the names are not generic terms or abbreviations.
        - for kow-how replace with know_how
        - Ensure that the names do not contain any special characters for example replace `-` with `_`.
        - Ensure that each clause is treated as a separate entity.
        - Ensure no important information is lost by processing each clause individually.
        - Ensure that the `type` field is correctly populated with the same data as `name`.
        - For each entities ensure that the name and type are not empty.
        - Ensure that the `name` field aligns with terminology commonly used in use the appropriate electrical ans energy industry and legal contexts.
        - Validate the `name` field against a predefined use the appropriate electrical ans energy industry and legal lexicon to ensure correctness.
        - If the `name` field does not match the lexicon, attempt to infer the correct term based on context.
        - Ensure that the `name` field is not a generic term or abbreviation.
        - Ensure that the `name` field is not a placeholder or temporary name.
        - Ensure that the `name` field is not a common noun or verb. 
        - Avoid using generic or ambiguous terms; prefer precise and domain-specific terminology.
        - Ensure that the `name` field is not empty.
        - Ensure that the `name` field is not like Clause_14.2 
        - Ensure that the `type` field is not empty.
        - Ensure that the `type` field is not like Clause_14.2
        - Ensure that the `name` field is not unknown.
        - Ensure that the `name` field is not an abbreviation like SMG and replace the abbreviation with the full name.
        - Ensure that csv like directors, officers, employees, agents, solicitors, accountants, consultants, and financial or other advisors is split into separate entities
          eg. Split Goods,machinery,equipment_plant,services,spare_parts into separate entities with the same name and type.
        - Do Not start the  `name` with numbers eg. Rename 5_5_Buyer_Restrictions  to "Buyer_Restrictions"

        2. **Ensure the response is a valid JSON object.**  
        - Use a JSON validator to confirm correctness.

        3. **Entity Extraction:**  
        - Identify all relevant entities and their associated types or categories.

        4. **Relationship Extraction:**  
        - Identify relationships between entities, specifying the type of relationship.  
        - **Replace hyphens (`-`) with underscores (`_`) in relationship names.**  
            - For example, in `MERGE (a)-[r:part-of]->(b)`, replace with `"part_of"`.  
            - Ensure consistency by using snake_case for all relationship types.
        - Use the format `from`, `to`, and `type` for relationships.
        - Ensure that the `type` field for relationships is meaningful and contextually accurate.
        - Use specific relationship types based on the entities being connected. For example:
            - If connecting a "Person" to a "Company," use "employed_by" or "associated_with."
            - If connecting a "Product" to a "Category," use "belongs_to."
            - If connecting a "Company" to another "Company," use "partner_of," "subsidiary_of," or "competitor_of" as appropriate.
            - If connecting an "Agreement" to a "Party," use "involves" or "signed_by."
            - If connecting a "Clause" to an "Agreement," use "part_of."
            - If connecting a "Term" to a "Clause," use "defined_in."
        - Ensure that the relationship type is meaningful and contextually accurate.
        - Use specific relationship types based on the entities being connected. For example:
        - Use manufacturing-specific terms for relationships, such as "supplies," "manufactures," "distributes," or "licenses."
        - Ensure that the relationship type is in snake_case format.
        - Ensure that the `from` and `to` fields are correctly populated with entity names.
        - Ensure that the `from` and `to` fields are not unknown.
        - Ensure that the  `from` and `to` fields are not like Clause_14.2 or Clause 4.1
        - If the relationship type is not clear, use a generic term like "related_to" or "associated_with" otherwise use the appropriate relationship type.
        - Ensure that the `type` field is not empty.
        - Ensure that the `type` field is not like Clause_14.2
        
        5. **Subclause Handling:**  
        - Ensure that nested information is preserved, all connected entities are included and all relationships are captured.

        6. **Fallback for No Data:**  
        - If no entities or relationships are found, return:
        {{
            "entities": [],
            "relationships": []
        }}

        7. **Strict JSON Format:**  
        - Only return the JSON object.  
        - Do **NOT** include markdown, backticks, or any extra text.  
        - Use **double quotes** for property names and string values.  
        - Double-check for trailing commas, mismatched braces, and incorrect quotation marks.

        8. **Ontology Context:**  
        - Connect all extracted entities and relationships to the overarching concept of either:
            - "Agreement"
            - "Contract"
            - "Legal_Agreement"
            - "Legal_Contract"
            - "Business_Agreement" 
            - "Business_Contract"
            - "agreement" (if applicable based on context)
            - "contract" (if applicable based on context)
            - "Manufacturing_Agreement" (if applicable based on context).

        9. **Replace "class" with an alternative word:**  
        - Use terms like "category," "type," or "classification" instead.

        ---

        ### Important:
        - **Validate and regenerate output** until the JSON is syntactically correct.
        - **No markdown. No extra text.**
        """

    return PROMPT



def get_semantic_split(section,text):
    PROMPT = f"""
               get the {section} from the {text}
               Use the following Instructions:
                - Do not summarize the text use it verbatim
            """
    return PROMPT

def generate_questions(content):
    PROMPT = f"""
        Using {content} as the context, generate "what," "why," and "how" questions.

         Use the following Instructions:
         - Do not summarize the text; use it verbatim.
         - Do not change the text or its structure.
         - Do not add any extra text, explanation, or information.
         - Retry if the output is [] or empty.
         - Return the questions in a list format.
         - Do not include any other text or explanation.
         - Each question should be a string.
         - Ensure that the questions are relevant to the content provided.
         - The questions should be in the format of "what," "why," and "how."
         - Avoid using any other question types.
         - The questions should be clear and concise.
         - Questions should be complete sentences.
         - Do not include any other text or explanation.

        Return the questions in the following format:
        ```
            [
                "What is the purpose of the document?",
                "Why is it important?",
                "How does it affect the parties involved?"
            ]
        ```

        Example:
        1. **Formation of SMG**: SMG was established as a wholly-owned subsidiary of SMC, not MSIL, as per point D. This indicates that SMC is the parent company, with MSIL possibly being another subsidiary or related entity.

        [
            "Who is SMG?",
            "Who is the parent company of SMG ?",
            "HWhat is a wholly-owned subsidiary?",
            "How does the establishment of SMG affect SMC and MSIL?",
            "What is the significance of SMG being a subsidiary?",
            "Why was SMG established as a subsidiary?",
            "What is the relationship between SMC and MSIL?",
            "How does the establishment of SMG impact the business structure?",
            "What are the implications of SMG being a subsidiary?",
            "How does this affect the ownership structure?",
            "What are the benefits of being a wholly-owned subsidiary?",
            "What are the legal implications of this structure?",
            "How does this affect the operations of SMG?",
            "What is the significance of this establishment?",
            "What are the potential risks or challenges?",
            "How does this impact the stakeholders?",
            "What is the role of SMG within the larger organization?",
            "What are the responsibilities of SMG?",
            "What are the advantages of this structure?",
            "What are the disadvantages of this structure?",
            "How does this affect the financial structure?",
            "What are the tax implications of this structure?",
            "What are the regulatory implications of this structure?",
            "How does this affect the governance structure?",
            "What are the reporting requirements for SMG?",
            "What are the compliance requirements for SMG?",
            "How does this affect the decision-making process?",
            "What are the implications for risk management?",
            "How does this affect the strategic direction?"
        ]

         ### Important:
        - **if result is empty then return above array**
        
        """
    return PROMPT


def answer_question(content,question):
    PROMPT = f""" 
            Using {content} as context, answer the following question: {question}.
        """
    return PROMPT