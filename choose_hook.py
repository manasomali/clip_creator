import os

def extract_sentences(file_content):
    """Extract three sentences from the content."""
    lines = file_content.splitlines()
    sentences = []
    for line in lines:
        if line.strip().startswith(("1.", "2.", "3.")):
            sentence = line.split(".", 1)[1].strip().strip('"')
            sentences.append(sentence)
    return sentences

def process_txt_file(file_path):
    """Process a single txt file to let user choose one sentence."""
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    sentences = extract_sentences(content)
    if not sentences:
        print(f"No valid sentences found in {file_path}. Skipping...")
        return

    print(f"\nSentences in {file_path}:")
    for i, sentence in enumerate(sentences, 1):
        print(f"{i}. {sentence}")

    while True:
        try:
            choice = int(input("Select the number of the sentence you want to keep (1-3): "))
            if 1 <= choice <= len(sentences):
                chosen_sentence = sentences[choice - 1]
                break
            else:
                print("Invalid choice. Please choose a number between 1 and 3.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(chosen_sentence)

    print(f"Updated {file_path} with the chosen sentence.")

def main(directory):
    """Main function to process all txt files in a directory."""
    txt_files = [f for f in os.listdir(directory) if f.endswith(".txt")]

    if not txt_files:
        print("No .txt files found in the specified directory.")
        return

    for txt_file in txt_files:
        file_path = os.path.join(directory, txt_file)
        process_txt_file(file_path)

if __name__ == "__main__":
    dir_path = input("Enter the directory path containing the txt files: ").strip()
    if os.path.isdir(dir_path):
        main(dir_path)
    else:
        print("Invalid directory path. Please try again.")
