import random
import time
import pandas as pd
import requests
from datetime import datetime

def load_dataframe(csv_path, example_col_start=None, example_col_name=None):
    """
    Load a DataFrame from a CSV file and extract combined examples from a specified column index or name.

    Args:
        csv_path (str): Path to the CSV file.
        example_col_start (int, optional): Starting index of the columns to combine. Defaults to None.
        example_col_name (str, optional): Name of the starting column to combine. Defaults to None.

    Returns:
        pd.DataFrame: DataFrame with an additional 'combined_examples' column.

    Raises:
        ValueError: If neither `example_col_start` nor `example_col_name` is provided.
    """
    df = pd.read_csv(csv_path)
    if example_col_start is not None:
        df["combined_examples"] = _combine_examples(df.iloc[:, example_col_start:])
    elif example_col_name is not None:
        col_start = df.columns.get_loc(example_col_name)
        df["combined_examples"] = _combine_examples(df.iloc[:, col_start:])
    else:
        raise ValueError("Provide either example_col_start or example_col_name")
    return df

def load_garaterm_dataframe(csv_path):
    """
    Load a Garaterm DataFrame from a CSV file and extract combined examples starting from the 'Garaterm example' column.

    Args:
        csv_path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: DataFrame with an additional 'combined_examples' column.
    """
    df = pd.read_csv(csv_path)
    col_start = df.columns.get_loc("Garaterm example")
    df["combined_examples"] = _combine_examples(df.iloc[:, col_start:])
    return df

def _combine_examples(columns):
    """
    Combine non-empty, non-NaN string values from multiple columns into a list.

    Args:
        columns (pd.DataFrame): Columns to combine.

    Returns:
        pd.Series: Series of lists containing combined examples.
    """
    return columns.apply(
        lambda row: [x for x in row if pd.notna(x) and isinstance(x, str) and x.strip() != ""], axis=1
    )

def prepare_garaterm_pairs(df):
    """
    Prepare a Garaterm DataFrame by filtering rows with examples, deduplicating terms, and selecting relevant columns.

    Args:
        df (pd.DataFrame): Input DataFrame.

    Returns:
        pd.DataFrame: Filtered and deduplicated DataFrame.
    """
    df = df[df["combined_examples"].str.len() > 0]
    df = df[["term", "translation", "context", "combined_examples"]]
    return filter_and_pair_terms(df, term_col="term")

def filter_and_pair_terms(df, term_col="term"):
    """
    Remove duplicate terms and pair them for translation tasks.

    Args:
        df (pd.DataFrame): Input DataFrame.
        term_col (str): Column name containing terms. Defaults to "term".

    Returns:
        pd.DataFrame: DataFrame with unique terms.
    """
    df_unique = df.drop_duplicates(subset=[term_col], keep="first")
    return df[df[term_col].isin(df_unique[term_col])]

def build_prompts(term, context_a, translation_a, example_a, context_b, translation_b, example_b, possible_examples, few_shot_examples, lang="en"):
    """
    Build a dictionary of prompts for translation tasks in different configurations.

    Args:
        term (str): Term to translate.
        context_a (str): Context for the first translation.
        translation_a (str): Translation of the term in the first context.
        example_a (str): Example sentence for the first context.
        context_b (str): Context for the second translation.
        translation_b (str): Translation of the term in the second context.
        example_b (str): Example sentence for the second context.
        possible_examples (list): List of possible examples for 1-shot prompts.
        few_shot_examples (list): List of examples for few-shot prompts.
        lang (str): Language code ("en", "es", or others). Defaults to "en".

    Returns:
        dict: Dictionary containing prompts for "0shot", "0shotplus", "1shot", and "fewshot".
    """
    prompts = {
        "0shot": _build_0shot_prompt(term, context_a, translation_a, example_a, context_b, translation_b, example_b, lang),
        "0shotplus": _build_0shotplus_prompt(term, context_a, translation_a, example_a, context_b, translation_b, example_b, lang),
        "1shot": _build_1shot_prompt(term, context_a, translation_a, context_b, translation_b, example_a, example_b, possible_examples, lang),
        "fewshot": _build_fewshot_prompt(term, context_a, translation_a, context_b, translation_b, example_a, example_b, few_shot_examples, lang)
    }
    return prompts

def _build_0shot_prompt(term, context_a, translation_a, example_a, context_b, translation_b, example_b, lang):
    if lang == "en":
        return f"Translate these contexts into English:\n1. {example_a}\n2. {example_b}"
    elif lang == "es":
        return f"Traduce estos contextos al español:\n1. {example_a}\n2. {example_b}"
    else:
        return f"Testuinguru hauek euskarara itzuli:\n1. {example_a}\n2. {example_b}"

def _build_0shotplus_prompt(term, context_a, translation_a, example_a, context_b, translation_b, example_b, lang):
    if lang == "en":
        return f"Translate these contexts into English taking into account that {term} translates as {translation_a} in {context_a} and as {translation_b} in {context_b}:\n1. {example_a}\n2. {example_b}"
    elif lang == "es":
        return f"Traduce estos contextos al español teniendo en cuenta que {term} se traduce como {translation_a} en {context_a} y como {translation_b} en {context_b}:\n1. {example_a}\n2. {example_b}"
    else:
        return f"Testuinguru hauek euskarara itzuli kontuan hartuta {term} hitza {translation_a} bezala itzultzen dela {context_a} arloan eta {translation_b} bezala {context_b} arloan:\n1. {example_a}\n2. {example_b}"

def _build_1shot_prompt(term, context_a, translation_a, context_b, translation_b, example_a, example_b, possible_examples, lang):
    if not possible_examples:
        return ""
    ex1 = possible_examples[0]
    if lang == "en":
        return (
            f"Translate these contexts into English taking into account that {term} translates as {translation_a} in {context_a}, as seen in:\n{ex1[0]}"
            f"\nand as {translation_b} in {context_b}, as seen in:\n{ex1[1]}\n\nNow translate:\n1. {example_a}\n2. {example_b}"
        )
    elif lang == "es":
        return (
            f"Traduce estos contextos al español teniendo en cuenta que {term} se traduce como {translation_a} en {context_a}, como se ve en:\n{ex1[0]}"
            f"\ny como {translation_b} en {context_b}, como se ve en:\n{ex1[1]}\n\nAhora traduce:\n1. {example_a}\n2. {example_b}"
        )
    else:
        return (
            f"Testuinguru hauek euskarara itzuli kontuan hartuta {term} hitza {translation_a} bezala itzultzen dela {context_a} arloan, eta horren adibidea hau da:\n{ex1[0]}"
            f"\nEta {translation_b} bezala {context_b} arloan, eta horren adibidea hau da:\n{ex1[1]}\n\nItzuli:\n1. {example_a}\n2. {example_b}"
        )

def _build_fewshot_prompt(term, context_a, translation_a, context_b, translation_b, example_a, example_b, few_shot_examples, lang):
    if not few_shot_examples:
        return ""
    if lang == "en":
        return (
            f"Translate these contexts into English taking into account the following examples:\n\n"
            f"In {context_a}, where {term} translates as {translation_a}:\n"
            + "\n".join([f"{i+1}. {e[0]}" for i, e in enumerate(few_shot_examples)]) + "\n\n"
            f"In {context_b}, where {term} translates as {translation_b}:\n"
            + "\n".join([f"{i+1}. {e[1]}" for i, e in enumerate(few_shot_examples)]) + "\n\n"
            f"Now translate:\n1. {example_a}\n2. {example_b}"
        )
    elif lang == "es":
        return (
            f"Traduce estos contextos al español teniendo en cuenta los siguientes ejemplos:\n\n"
            f"En {context_a}, donde {term} se traduce como {translation_a}:\n"
            + "\n".join([f"{i+1}. {e[0]}" for i, e in enumerate(few_shot_examples)]) + "\n\n"
            f"En {context_b}, donde {term} se traduce como {translation_b}:\n"
            + "\n".join([f"{i+1}. {e[1]}" for i, e in enumerate(few_shot_examples)]) + "\n\n"
            f"Ahora traduce:\n1. {example_a}\n2. {example_b}"
        )
    else:
        return (
            f"Testuinguru hauek euskarara itzuli, ondorengo adibideak kontuan hartuta:\n\n"
            f"{context_a} arloan, non {term} hitza {translation_a} bezala itzultzen den:\n"
            + "\n".join([f"{i+1}. {e[0]}" for i, e in enumerate(few_shot_examples)]) + "\n\n"
            f"{context_b} arloan, non {term} hitza {translation_b} bezala itzultzen den:\n"
            + "\n".join([f"{i+1}. {e[1]}" for i, e in enumerate(few_shot_examples)]) + "\n\n"
            f"Orain itzuli adibide hauek:\n1. {example_a}\n2. {example_b}"
        )

def latxa_system_prompt():
    """
    Generate a system prompt for the Latxa AI assistant.

    Returns:
        str: System prompt string.
    """
    today = datetime.now().strftime('%Y-%m-%d')
    return (
        f"You are a helpful Artificial Intelligence assistant called Latxa, "
        f"created and developed by HiTZ, the Basque Center for Language Technology research center. "
        f"Every conversation will be conducted in standard Basque. "
        f"Today is {today}."
    )

def latxa_api_request(prompt, config, retries=4, base_delay=5):
    """
    Make a request to the Latxa API with retry logic.

    Args:
        prompt (str): User prompt to send to the API.
        config (object): Configuration object containing LATXA_MODEL and LATXA_URL.
        retries (int, optional): Number of retry attempts. Defaults to 4.
        base_delay (int, optional): Base delay in seconds between retries. Defaults to 5.

    Returns:
        str: Response content from the API or failure message.
    """
    payload = {
        "model": config.LATXA_MODEL,
        "messages": [
            {"role": "system", "content": latxa_system_prompt()},
            {"role": "user", "content": prompt}
        ]
    }
    headers = {"Content-Type": "application/json"}
    for attempt in range(retries):
        try:
            response = requests.post(config.LATXA_URL, json=payload, headers=headers, timeout=90)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                print(f"⚠️ HTTP Error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"⚠️ Attempt {attempt+1} failed: {e}")
        wait_time = base_delay * (attempt + 1) + random.uniform(0, 3)
        print(f"⏳ Retrying in {wait_time:.2f} seconds...")
        time.sleep(wait_time)
    return "❌ Failure after multiple attempts"
