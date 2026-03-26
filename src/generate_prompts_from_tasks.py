from generate_prompt import generate_prompt
import os
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate LLM prompts from scenario tasks"
    )

    parser.add_argument(
        "--tasks-folder",
        required=True,
        help="Folder containing scenario .txt files"
    )

    parser.add_argument(
        "--output-folder",
        required=True,
        help="Folder where generated prompts will be stored"
    )

    parser.add_argument(
        "--protocols",
        required=True,
        help="Comma-separated list of protocols (e.g. ngap,gtpu,pfcp)"
    )

    parser.add_argument(
        "--num-examples",
        default="1,5,7",
        help="Comma-separated list of example counts (default: 1,5,7)"
    )

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    TASKS_FOLDER = args.tasks_folder
    OUTPUT_FOLDER = args.output_folder
    protocol_list = [proto.strip() for proto in args.protocols.split(",")]
    num_examples_list = [int(num.strip()) for num in args.num_examples.split(",")]

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    for scenario_file in os.listdir(TASKS_FOLDER):
        if scenario_file.endswith(".txt"):
            scenario_path = os.path.join(TASKS_FOLDER, scenario_file)
            scenario_description = open(scenario_path).read().strip()

            for num_examples in num_examples_list:
                prompt = generate_prompt(scenario_description, protocol_list, num_examples=num_examples)
                output_filename = f"{scenario_file.replace('.txt', '')}_examples_{num_examples}.txt"
                output_path = os.path.join(OUTPUT_FOLDER, output_filename)
                with open(output_path, "w") as file:
                        file.write(prompt)