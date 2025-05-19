import prompt_utils as pu

# Directories containing the generated prompts
directories_to_read = [
    "experimentation/same_translation/results_es_en",
    "experimentation/same_translation/results_es_ba",
    "experimentation/same_translation/results_en_es",
]

# Types of prompts to process
prompt_categories = [
    "0shot",
    "0shotplus",
    "1shot"
]

if __name__ == "__main__":
    # Iterate through each directory and process the prompts
    for directory in directories_to_read:
        print(f"Reading prompts from {directory}")
        pu.read_generated_prompts(directory, prompt_categories)