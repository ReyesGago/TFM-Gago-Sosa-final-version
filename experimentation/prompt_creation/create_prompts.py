import os
import prompt_utils as pu

# Input CSV files containing context data for prompt generation
input_csv_files = [
    "experimentation/context_recopilation_test_es_en.csv",
    "experimentation/context_recopilation_test_es_ba.csv",
    "experimentation/context_recopilation_test_en_es.csv",
]

# Output directories where the generated prompts will be saved
output_directories = [
    "experimentation/prompt_creation/generated_prompts/results_es_en",
    "experimentation/prompt_creation/generated_prompts/results_es_ba",
    "experimentation/prompt_creation/generated_prompts/results_en_es",
]

# Language pairs corresponding to each input-output pair
language_pairs = [
    "es_en",  # Spanish to English
    "es_ba",  # Spanish to Basque
    "en_es",  # English to Spanish
]

if __name__ == "__main__":
    # Iterate through language pairs, input files, and output directories
    for lang_pair, input_csv, output_dir in zip(language_pairs, input_csv_files, output_directories):
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)
        # Generate prompts using the utility function
        pu.generate_prompts(input_csv, output_dir, lang_pair)