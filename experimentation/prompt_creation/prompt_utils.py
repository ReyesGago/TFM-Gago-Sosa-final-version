import pandas as pd
import os
import random

def generate_0_shot(lang_pair: str, physics_example: str, engineering_example: str) -> str:
    """
    Generate a 0-shot prompt for translation.
    
    Args:
        lang_pair (str): The language pair for translation.
        physics_example (str): Example sentence from physics context.
        engineering_example (str): Example sentence from engineering context.
    
    Returns:
        str: The formatted 0-shot prompt.
    """
    res = ""
    if lang_pair == "es_en" or lang_pair == "es_ba":
        res = (
            f"Traduce estos contextos al inglés:\n"
            f"1. {physics_example}\n"
            f"2. {engineering_example}"
        )
    elif lang_pair == "en_es":
        res = (
            f"Translate these contexts into Spanish:\n"
            f"1. {physics_example}\n"
            f"2. {engineering_example}"
        )
    return res

def generate_0_shot_plus(
    lang_pair: str, term: str, physics_example: str, engineering_example: str,
    physics_translation: str, engineering_translation: str
) -> str:
    """
    Generate a 0-shot-plus prompt for translation with term-specific translations.
    
    Args:
        lang_pair (str): The language pair for translation.
        term (str): The term to translate.
        physics_example (str): Example from physics context.
        engineering_example (str): Example from engineering context.
        physics_translation (str): Translation in physics.
        engineering_translation (str): Translation in engineering.
    
    Returns:
        str: The formatted 0-shot-plus prompt.
    """
    res = ""

    if lang_pair == "es_en" or lang_pair == "es_ba":
        res = (
            f"Traduce estos contextos al inglés teniendo en cuenta que {term} se traduce como "
            f"{physics_translation} en física y como {engineering_translation} en ingeniería:\n"
            f"1. {physics_example}\n"
            f"2. {engineering_example}"
        )
    elif lang_pair == "en_es":
        res = (
            f"Translate these contexts into Spanish taking into account that {term} translates as "
            f"{physics_translation} in physics and as {engineering_translation} in engineering:\n"
            f"1. {physics_example}\n"
            f"2. {engineering_example}"
        )
    return res

def generate_1_shot(lang_pair: str,
    term: str, physics_context: str, engineering_context: str,
    physics_example_translated: str, engineering_example_translated: str,
    new_physics_example: str, new_engineering_example: str,
    physics_translation: str, engineering_translation: str
) -> str:
    """
    Generate a 1-shot prompt for translation with one example for each context.
    
    Args:
        lang_pair (str): The language pair for translation.
        term (str): The term to translate.
        physics_context (str): Physics context.
        engineering_context (str): Engineering context.
        physics_example_translated (str): Example translation in physics.
        engineering_example_translated (str): Example translation in engineering.
        new_physics_example (str): New example from physics to translate.
        new_engineering_example (str): New example from engineering to translate.
        physics_translation (str): Translation in physics.
        engineering_translation (str): Translation in engineering.
    
    Returns:
        str: The formatted 1-shot prompt.
    """
    res = ""
    if lang_pair == "es_en" or lang_pair == "es_ba":
        res = (
            f"Traduce estos contextos al inglés teniendo en cuenta que {term} se traduce como "
            f"{physics_translation} en {physics_context}, como muestra el siguiente ejemplo:\n"
            f"{physics_example_translated}\n"
            f"Y como {engineering_translation} en {engineering_context}, como muestra el siguiente ejemplo:\n"
            f"{engineering_example_translated}\n\n"
            f"Traduce:\n"
            f"1. {new_physics_example}\n"
            f"2. {new_engineering_example}"
        )
    elif lang_pair == "en_es":
        res = (
            f"Translate these contexts into Spanish taking into account that {term} translates as "
            f"{physics_translation} in {physics_context}, like the following example shows:\n"
            f"{physics_example_translated}\n"
            f"And as {engineering_translation} in {engineering_context}, like the following example shows:\n"
            f"{engineering_example_translated}\n\n"
            f"Translate:\n"
            f"1. {new_physics_example}\n"
            f"2. {new_engineering_example}"
        )
    return res

def generate_few_shot(lang_pair: str,
    term: str, physics_context: str, engineering_context: str,
    physics_examples: list, engineering_examples: list,
    physics_example_to_translate: str, engineering_example_to_translate: str,
    physics_translation: str, engineering_translation: str
) -> str:
    """
    Generate a few-shot prompt for translation with multiple examples for each context.
    
    Args:
        lang_pair (str): The language pair for translation.
        term (str): The term to translate.
        physics_context (str): Physics context.
        engineering_context (str): Engineering context.
        physics_examples (list): List of example sentences from physics.
        engineering_examples (list): List of example sentences from engineering.
        physics_example_to_translate (str): New physics example to translate.
        engineering_example_to_translate (str): New engineering example to translate.
        physics_translation (str): Translation in physics.
        engineering_translation (str): Translation in engineering.
    
    Returns:
        str: The formatted few-shot prompt.
    """
    physics_examples_text = "\n".join([f"{i+1}. {example}" for i, example in enumerate(physics_examples)])
    engineering_examples_text = "\n".join([f"{i+1}. {example}" for i, example in enumerate(engineering_examples)])
    
    res = ""
    if lang_pair == "en_es":
        res = (
            f"Translate these contexts into Spanish considering the following examples:\n\n"
            f"Examples in {physics_context}, where {term} translates as {physics_translation}:\n"
            f"{physics_examples_text}\n\n"
            f"Examples in {engineering_context}, where {term} translates as {engineering_translation}:\n"
            f"{engineering_examples_text}\n\n"
            f"Translate:\n"
            f"1. {physics_example_to_translate}\n"
            f"2. {engineering_example_to_translate}"
        )
    elif lang_pair == "es_ba" or lang_pair == "es_en":
        res = (
            f"Traduce estos contextos al inglés teniendo en cuenta los siguientes ejemplos:\n\n"
            f"Ejemplos en {physics_context}, donde {term} se traduce como {physics_translation}:\n"
            f"{physics_examples_text}\n\n"
            f"Ejemplos en {engineering_context}, donde {term} se traduce como {engineering_translation}:\n"
            f"{engineering_examples_text}\n\n"
            f"Ahora traduce estos nuevos ejemplos:\n"
            f"1. {physics_example_to_translate}\n"
            f"2. {engineering_example_to_translate}"
        )
    return res

def read_generated_prompts(output_dir, prompt_types=None):
    """
    Lee los archivos de prompts en el directorio dado y para cada uno imprime los prompts
    de los tipos indicados en prompt_types en el formato:
    === {term} ===
    =={prompt_type} ===
    == {prompt} ===
    """
    for filename in os.listdir(output_dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()

            term = None
            prompts = []
            current_type = None
            current_prompt = []
            for line in lines:
                if line.startswith("=== Term:"):
                    term = line.strip().replace("=== Term: ", "").replace(" ===", "")
                elif line.startswith("--- ") and line.endswith(" ---\n"):
                    if current_type and current_prompt:
                        prompts.append((current_type, "".join(current_prompt).strip()))
                    current_type = line.strip().replace("--- ", "").replace(" ---", "")
                    current_prompt = []
                elif line.strip() == "" and current_type:
                    if current_type and current_prompt:
                        prompts.append((current_type, "".join(current_prompt).strip()))
                        current_type = None
                        current_prompt = []
                elif current_type:
                    current_prompt.append(line)
            if current_type and current_prompt:
                prompts.append((current_type, "".join(current_prompt).strip()))

            for ptype, prompt in prompts:
                if (prompt_types is None) or (ptype in prompt_types):
                    print(f"\n===> {term} <===")
                    print(f"\n>> {ptype}")
                    print(f"\nPrompt: \n{prompt}")

def generate_prompts(input_csv, output_dir, lang_pair):
    """
    Main function to read the CSV, process term pairs, and generate prompt files.
    """
    # Read the CSV file containing context and example data
    df = pd.read_csv(input_csv)

    # Combine example columns into a single list for each row
    df["combined_examples"] = df.iloc[:, df.columns.get_loc("Wikipedia usage examples"):].apply(
        lambda row: [x for x in row if pd.notna(x)], axis=1
    )
    df = df[["term", "translation", "context", "combined_examples"]]

    # Remove duplicate terms, keeping the first occurrence
    unique_terms_df = df.drop_duplicates(subset=["term"], keep="first")

    # Select unique terms along with their pairs
    selected_terms = df[df["term"].isin(unique_terms_df["term"])]

    # Process term pairs (assumes physics and engineering alternate)
    for i in range(0, len(selected_terms), 2):
        if i + 1 >= len(selected_terms):
            break  # Ensure there is a pair

        # Extract term and context information for physics and engineering
        term = selected_terms.iloc[i]["term"]
        physics_context = selected_terms.iloc[i]["context"]
        physics_translation = selected_terms.iloc[i]["translation"]
        physics_examples = selected_terms.iloc[i]["combined_examples"]

        engineering_context = selected_terms.iloc[i + 1]["context"]
        engineering_translation = selected_terms.iloc[i + 1]["translation"]
        engineering_examples = selected_terms.iloc[i + 1]["combined_examples"]

        # Determine the number of examples to process (minimum of both contexts)
        num_examples = min(len(physics_examples), len(engineering_examples))
        for idx in range(num_examples):
            prompts = []
            prompt_titles = ["0shot", "0shotplus", "1shot", "fewshot"]

            # Select examples to translate
            physics_example_to_translate = physics_examples[idx]
            engineering_example_to_translate = engineering_examples[idx]

            # Generate possible examples for few-shot and 1-shot prompts (excluding current)
            possible_examples = list(zip(
                physics_examples[:idx] + physics_examples[idx+1:], 
                engineering_examples[:idx] + engineering_examples[idx+1:]
            ))
            few_shot_examples = (
                random.sample(possible_examples, min(3, len(possible_examples)))
                if len(possible_examples) >= 3 else []
            )

            # Generate prompts for each type
            prompts.append(generate_0_shot(lang_pair, physics_example_to_translate, engineering_example_to_translate))
            prompts.append(generate_0_shot_plus(lang_pair,
                term, physics_example_to_translate, engineering_example_to_translate, 
                physics_translation, engineering_translation
            ))
            if len(possible_examples) >= 1:
                one_shot_example = random.choice(possible_examples)
                prompts.append(generate_1_shot(lang_pair,
                    term, physics_context, engineering_context, 
                    one_shot_example[0], one_shot_example[1], 
                    physics_example_to_translate, engineering_example_to_translate, 
                    physics_translation, engineering_translation
                ))
            if few_shot_examples:
                prompts.append(generate_few_shot(lang_pair,
                    term, physics_context, engineering_context, 
                    [e[0] for e in few_shot_examples], [e[1] for e in few_shot_examples], 
                    physics_example_to_translate, engineering_example_to_translate, 
                    physics_translation, engineering_translation
                ))

            # Save prompts to a file
            output_filename = os.path.join(
                output_dir, f"prompts_term_{i//2 + 1}_example_{idx+1}.txt"
            )
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(f"=== Term: {term} ===\n\n")
                for p_idx, prompt in enumerate(prompts):
                    f.write(f"--- {prompt_titles[p_idx]} ---\n")
                    f.write(prompt + "\n\n")

            print(f"✅ Saved: {output_filename}")