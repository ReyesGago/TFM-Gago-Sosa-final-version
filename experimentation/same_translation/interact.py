import os
import time
import random
import pandas as pd
import config
from together import Together
from utils import (
    load_dataframe, filter_and_pair_terms, build_prompts,
    latxa_api_request, load_garaterm_dataframe, prepare_garaterm_pairs
)

def api_request(prompt, model="gpt"):
    """
    Sends a request to the specified model's API and returns the response.

    Args:
        prompt (str): The input prompt for the model.
        model (str): The model to use ("gpt", "llama", "gemini", "latxa").

    Returns:
        str: The response from the model or an error message after retries.
    """
    if model == "gpt":
        import openai
        openai.api_key = config.OPENAI_API_KEY
        for attempt in range(3):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    request_timeout=60
                )
                return response.choices[0].message["content"].strip()
            except Exception as e:
                print(f"GPT error: {e}. Retry {attempt + 1}/3")
                time.sleep(5 * (attempt + 1))
        return "❌ Error after retries"
    elif model == "llama":
        client = Together(api_key=config.TOGETHER_API_KEY)
        for attempt in range(3):
            try:
                response = client.chat.completions.create(
                    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"LLaMA error: {e}. Retry {attempt + 1}/3")
                time.sleep(5 * (attempt + 1))
        return "❌ Error after retries"
    elif model == "gemini":
        import google.generativeai as genai
        genai.configure(api_key=config.GEMINI_API_KEY)
        model_g = genai.GenerativeModel("gemini-1.5-pro")
        for attempt in range(3):
            try:
                response = model_g.generate_content(prompt)
                if response and hasattr(response, 'text') and response.text:
                    return response.text
            except Exception as e:
                print(f"Gemini error: {e}. Retry {attempt + 1}/3")
                time.sleep(5 * (attempt + 1))
        return "❌ Error after retries"
    elif model == "latxa":
        return latxa_api_request(prompt, config)
    else:
        raise ValueError("Unknown model")

def process_and_save(csv_path, output_path, model="gpt", lang="en", example_col_name="Wikipedia usage examples", is_garaterm=False):
    """
    Processes input data, generates prompts, sends API requests, and saves the results.

    Args:
        csv_path (str): Path to the input CSV file.
        output_path (str): Path to save the output CSV file.
        model (str): The model to use for API requests.
        lang (str): Target language for prompts.
        example_col_name (str): Column name for examples (only for non-Garaterm data).
        is_garaterm (bool): Whether the input data is from Garaterm.
    """
    if is_garaterm:
        df = load_garaterm_dataframe(csv_path)
        df = prepare_garaterm_pairs(df)
    else:
        df = load_dataframe(csv_path, example_col_name=example_col_name)
        df = df[["term", "translation", "context", "combined_examples"]]
        df = filter_and_pair_terms(df)

    results = []
    batch_size = 50
    batch_count = 0

    for i in range(0, len(df), 2):
        if i + 1 >= len(df):
            break
        row_a = df.iloc[i]
        row_b = df.iloc[i + 1]
        examples_a = row_a["combined_examples"]
        examples_b = row_b["combined_examples"]

        if not examples_a or not examples_b:
            continue

        num_examples = min(len(examples_a), len(examples_b))
        for idx in range(num_examples):
            example_a = examples_a[idx]
            example_b = examples_b[idx]
            possible_examples = list(zip(
                examples_a[:idx] + examples_a[idx + 1:],
                examples_b[:idx] + examples_b[idx + 1:]
            ))
            few_shot_examples = random.sample(possible_examples, min(3, len(possible_examples))) if len(possible_examples) >= 3 else []
            prompts = build_prompts(
                row_a["term"], row_a["context"], row_a["translation"], example_a,
                row_b["context"], row_b["translation"], example_b,
                possible_examples, few_shot_examples, lang=lang
            )

            print(f"Processing term pair {i}//{len(df)} | Example {idx + 1}/{num_examples} | Term: {row_a['term']}")
            responses = {}
            for prompt_type, prompt_text in prompts.items():
                if prompt_text.strip():
                    responses[prompt_type] = api_request(prompt_text, model=model)
                else:
                    responses[prompt_type] = "⚠️ Prompt not built (missing examples)"
            print(f"Finished term pair {i}//{len(df)} | Example {idx + 1}/{num_examples} | Term: {row_a['term']}")

            results.append({
                "term": row_a["term"],
                "translation_pair": (row_a["translation"], row_b["translation"]),
                "response_0shot": responses["0shot"],
                "response_0shotplus": responses["0shotplus"],
                "response_1shot": responses["1shot"],
                "response_fewshot": responses["fewshot"]
            })

            batch_count += 1
            if batch_count % batch_size == 0:
                print("⏳ Waiting 60 seconds before continuing...")
                time.sleep(60)

    pd.DataFrame(results).to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"✅ Saved results to {output_path}")

if __name__ == "__main__":
    lang_pairs = [
        ("en_es", True), ("es_en", True),
        ("es_ba", True), ("en_ba", True),
        ("ba_es", False), ("ba_en", False)
    ]
    models = ["gpt", "llama", "gemini", "latxa"]

    configurations = []
    for model in models:
        for pair, needs_example_col in lang_pairs:
            conf = {"model_name": model, "lang_pair_key": pair}
            if needs_example_col:
                conf["example_col_name"] = "Wikipedia usage examples"
            configurations.append(conf)

    target_lang_map = {"en": "en", "es": "es", "ba": "eu"}
    config_file_dir = os.path.dirname(os.path.abspath(config.__file__))

    for conf in configurations:
        model = conf["model_name"]
        lang_pair = conf["lang_pair_key"]

        is_garaterm = False
        example_col = None

        if lang_pair in config.GARATERM_PATHS:
            is_garaterm = True
            relative_csv_path = config.GARATERM_PATHS[lang_pair]
        elif lang_pair in config.CSV_PATHS:
            is_garaterm = False
            relative_csv_path = config.CSV_PATHS[lang_pair]
            if "example_col_name" not in conf:
                print(f"⚠️ 'example_col_name' missing for non-Garaterm config with lang_pair_key '{lang_pair}'. Skipping.")
                continue
            example_col = conf["example_col_name"]
        else:
            print(f"⚠️ Path for lang_pair_key '{lang_pair}' not found in config.GARATERM_PATHS or config.CSV_PATHS. Skipping.")
            continue

        print(f"\n--- Processing: Model={model}, LangPair={lang_pair}, Garaterm={is_garaterm} ---")

        input_csv = os.path.abspath(os.path.join(config_file_dir, relative_csv_path))
        if not os.path.exists(input_csv):
            print(f"❌ Input file not found: {input_csv}. Skipping.")
            continue
        print(f"Input CSV: {input_csv}")

        try:
            target_key = lang_pair.split('_')[1]
            run_lang = target_lang_map[target_key]
        except (IndexError, KeyError) as e:
            print(f"❌ Could not determine target language for {lang_pair}: {e}. Skipping.")
            continue

        if model not in config.OUTPUT_DIRS:
            print(f"⚠️ Output directory for model {model} not found in config.OUTPUT_DIRS. Skipping.")
            continue
        output_dir_model = config.OUTPUT_DIRS[model]
        os.makedirs(output_dir_model, exist_ok=True)

        output_filename = f"results_{model}_{lang_pair}.csv"
        output_file_path = os.path.join(output_dir_model, output_filename)
        print(f"Output CSV: {output_file_path}")

        try:
            process_and_save(
                csv_path=input_csv,
                output_path=output_file_path,
                model=model,
                lang=run_lang,
                example_col_name=example_col,
                is_garaterm=is_garaterm
            )
        except Exception as e:
            print(f"❌ Error during processing for {model} {lang_pair}: {e}")

    print("\nAll configured tasks attempted.")