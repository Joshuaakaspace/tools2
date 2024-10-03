# ... (previous code remains the same)

# Update the entity_prompt to use double curly braces for JSON formatting
entity_prompt = PromptTemplate(
    input_variables=["name", "context"],
    template="""From the provided context, extract details about {name} who is explicitly listed as sanctioned.
    Ignore any mentions of other individuals or entities not under sanctions, even if their details are provided.
    Extract the following fields into a JSON format only, using the exact structure as below:
    {{{{
        "name": "{name}",
        "DOB": "",
        "POB": "",
        "Position": "",
        "rank": "",
        "nationality": "",
        "gender": "",
        "passport_number": "",
        "reasons": "",
        "date_of_listing": "",
        "Address": "",
        "Also known As": "",
        "other_details": ""
    }}}}
    If no relevant information is available for a field, leave it blank.
    Important Guidelines:
    Accuracy is critical: Ensure all details are captured accurately and completely. Do not capture incorrect or inferred information.
    Context: {context}"""
)

# ... (code for extracting names remains the same)

print("Extracted Names:", all_names)

# Updated extract_entity_details function with better error handling
def extract_entity_details(name: str):
    try:
        result = qa_chain.run(entity_prompt.format(name=name, context=f"Information about {name}"))
        # Remove any leading/trailing whitespace and newlines
        result = result.strip()
        # If the result doesn't start and end with curly braces, wrap it
        if not (result.startswith('{') and result.endswith('}')):
            result = '{' + result + '}'
        return json.loads(result)
    except json.JSONDecodeError as e:
        print(f"JSON decode error for {name}: {e}")
        print(f"Raw result: {result}")
        return {"name": name, "error": "Failed to parse JSON"}
    except Exception as e:
        print(f"Unexpected error for {name}: {e}")
        return {"name": name, "error": str(e)}

results = []
with ThreadPoolExecutor(max_workers=5) as executor:
    future_to_name = {executor.submit(extract_entity_details, name): name for name in all_names}
    for future in as_completed(future_to_name):
        name = future_to_name[future]
        try:
            result = future.result()
            results.append(result)
        except Exception as exc:
            print(f'Unexpected error when processing {name}: {exc}')
            results.append({"name": name, "error": str(exc)})

# Print results
print("\nExtracted Entity Details:")
for result in results:
    print(json.dumps(result, indent=2))

# Optional: Save results to a file
with open('extracted_entities.json', 'w') as f:
    json.dump(results, f, indent=2)
print("\nResults saved to 'extracted_entities.json'")