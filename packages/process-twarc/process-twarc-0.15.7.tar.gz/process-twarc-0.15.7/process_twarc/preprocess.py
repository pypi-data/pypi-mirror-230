
import pandas as pd
from process_twarc.util import get_file_type, get_output_path, save_to_parquet, load_dataset, get_all_files, concat_dataset, load_list_from_txt, load_tokenizer
import re
from datasets import Dataset

def process_twarc_file(file_path: str, output_dir: str=""):
    """
    Process a file acquired from Twarc2 and generate a parquet file with columns: tweet_id, text.

    Args:
        file_path (str): Path to the input file.
        output_dir (str): Directory where the generated parquet file will be saved.
    """
    file_type = get_file_type(file_path)

    if file_type == "jsonl":
        df = pd.read_json(file_path, lines=True, encoding="utf-8")
    elif file_type == "json" or file_type == "txt":
        df = pd.read_json(file_path, encoding="utf-8")
    else:
        raise ValueError("Unsupported file type: {}".format(file_type))

    if file_type == "txt":
        tweet_ids = df["id"].astype(str).tolist()
        texts = df["text"].tolist()
    else:
        tweet_ids = []
        texts = []

        for data in df["data"]:
            for item in data:
                tweet_ids.append(str(item["id"]))
                texts.append(item["text"])

    new_df = pd.DataFrame({"tweet_id": tweet_ids, "text": texts})

    if output_dir:
        output_path = get_output_path(file_path, output_dir, file_type="parquet")
        save_to_parquet(new_df, output_path)
    return new_df

def add_special_tokens(text: str):
    """
    Replaces URLs and usernames in the given text with special tokens.

    Args:
        text (str): The input text.

    Returns:
        str: The text with replaced URLs and usernames.
    """
    text = re.sub("https://t[^ ]+", "[URL]", text)
    text = re.sub("@[^ ]+", "[USER]", text)
    return text

def generate_masks(file_path, duplicate_text, output_dir:str="", duplicates=True, characters=True, patterns=True):
    """
    Generates masks based on various conditions for a given dataset.

    Args:
        file_path (str): Path to the dataset file.
        duplicate_text (Set[str]): Set of duplicate texts to check against.
        output_dir (str): Directory to save the output.

    Returns:
        pd.DataFrame: Processed dataset with added mask columns.

    """
    def check_duplicate(example:str, duplicate_text:set):
        """Checks if the text has been flagged as duplicate."""
        return example in duplicate_text

    def check_low_freq_char(example:str):
        """For training the tokenizer, checks if the dataset has a low frequency character."""
        return "[UNK]" in example
 
    def check_pattern(example:str):
        """Check if the text has one of the frequently occuring patterns defined below."""
        patterns = [
            "\AI('m| was) at.*in.*",
            "\(@ .*in.*\)"
            ]
        return any(re.search(pattern, example) for pattern in patterns)

    masked_dataset = load_dataset(file_path)
    masked_dataset["low_freq_char"], masked_dataset["duplicate"], masked_dataset["pattern"] = False, False, False
    for idx, row in masked_dataset.iterrows():
        text = row["text"]
        tokenized = row["tokenized"]
        masked_dataset.at[idx, "low_freq_char"] = check_low_freq_char(tokenized)
        masked_dataset.at[idx, "duplicate"] = check_duplicate(tokenized, duplicate_text)
        masked_dataset.at[idx, "pattern"] = check_pattern(text)
    
    masked_dataset = masked_dataset.remove_columns("tokenized")
    
    if output_dir:
        output_path = get_output_path(file_path, output_dir)
        save_to_parquet(masked_dataset, output_path)
    return masked_dataset


def update_mask(file_path, mask, path_to_masks, print_output=True, save_output=True):
    """
    Building masks was an iterative process.

    Given a masked dataset and a text file with updated mask IDs, this function updates the mask.

    Args:
        file_path (str): Path to the masked dataset.
        mask (str): The mask to be updated.
        path_to_masks (str): Path to the text file with updated mask IDs.
        print_output (bool, optional): Whether to print the number of IDs in the mask before and after the update.
        save_output (bool, optional): Whether to save the updated dataset to the same file path.

    Returns:
        pd.DataFrame: Updated dataset with the mask.
    """
    if mask == "low_freq_char":
        mask_ids = load_list_from_txt(f"{path_to_masks}/low-freq-char.txt")
    elif mask == "duplicate":
        mask_ids = load_list_from_txt(f"{path_to_masks}/duplicate.txt")
    elif mask == "pattern":
        mask_ids = load_list_from_txt(f"{path_to_masks}/pattern.txt")
    elif mask == "possibly_sensitive":
        mask_ids = load_list_from_txt(f"{path_to_masks}/possibly_sensitive.txt")
    else:
        raise ValueError("Please input a valid mask. 'low_freq_char', 'duplicate', or 'pattern'.")

    mask_ids = set(mask_ids)
    print( f"{mask} mask loaded. {len(mask_ids)} IDs.")

    dataset = load_dataset(file_path)
    old_mask = sum(dataset[mask])
    dataset[mask] = False

    mask_idx = dataset.loc[dataset["tweet_id"].isin(mask_ids)].index
    dataset.loc[mask_idx, mask] = True
    new_mask = sum(dataset[mask])

    if print_output:
        print("Old Mask:", old_mask)
        print("New Mask:", new_mask)
    
    if save_output:
        save_to_parquet(dataset, file_path)
    return dataset

def compile_duplicate_ids(masked_dir, path_to_output):
    """
    For record-keeping purposes, compiles the Tweet IDs that were flagged as duplicates.
    """
    file_paths = get_all_files(masked_dir)
    dataset = concat_dataset(file_paths, columns = ["tweet_id", "duplicate"])
    duplicate_ids = dataset[dataset["duplicate"]]
    duplicate_ids = duplicate_ids.drop(columns="duplicate").reset_index(drop=True)
    duplicate_ids.rename(columns={"tweet_id":"duplicate_id"}, inplace=True)
    save_to_parquet(duplicate_ids, path_to_output)
    print(f"Duplicate IDs compiled. Saved to {path_to_output}")
    return

def tokenize_for_masked_language_modeling(
        dataset: Dataset, 
        tokenizer: object, 
        path_to_output: str=""
        ):
    """
    The final step in preprocessing the data for masked language modeling.

    Duplicate rows are removed, and the text is tokenized.

    Afterwards, the tokenized text is filtered to remove examples that are too long.

    Args:
        file_path (str): Path to the dataset.
        path_to_tokenizer (str): Path to the tokenizer.
        output_dir (str): Directory to save the output.

    Returns:
        pd.DataFrame: Tokenized dataset.
    """
    def tokenize(example):
        return tokenizer.encode_plus(example["text"], max_length=280, truncation=True)
    
    tokenized_dataset = dataset.map(tokenize, remove_columns="text")
    tokenized_dataset = tokenized_dataset.filter(lambda example: len(example["input_ids"])<=117)

    if path_to_output:
        save_to_parquet(tokenized_dataset, path_to_output)
    return tokenized_dataset

def generate_splits(
        raw_datasets: Dataset,
        output_dir: str="",
        seed: int=42,
        test_size: float=0.1,
        validation_size: float= 0.05,
        development_size: float=0.1,
        print_details: bool=True):
    
    """
    The native train_test_split function from HuggingFace's Datasets library is limited in that it will only split the dataset into two parts.

    This function add the options to split into "validation" and "development" sets.

    Args:
        data_dir (str): Path to the dataset.
        seed (int, optional): Random seed for the split.
        test_size (float, optional): Size of the test set.
        validation_size (float, optional): Size of the validation set.
        development_size (float, optional): Size of the development set.
        print_details (bool, optional): Whether to print the details of the split.

    """
    print("Splitting datasets. . .")

    split_size = test_size + validation_size + development_size
    splits = raw_datasets.train_test_split(test_size = split_size, seed = seed)
    if validation_size:
        split = splits.pop("test")
        test_size = test_size/split_size
        validation_size = validation_size/split_size
        development_size = development_size/split_size
        split_size = test_size + development_size

        split_dataset = split.train_test_split(train_size = validation_size, test_size=split_size, seed = seed)
        splits["validation"], splits["test"] = split_dataset["train"], split_dataset["test"]

    if development_size:
        split = splits.pop("test")
        test_size = test_size/split_size
        development_size = development_size/split_size

        split_dataset = split.train_test_split(train_size=development_size, test_size=test_size, seed=seed)
        splits["development"], splits["test"] = split_dataset["train"], split_dataset["test"]

    if print_details:
        print(splits)

    if output_dir:
        for split in splits.keys():
            print ("Saving", split)
            path_to_output = f"{output_dir}/{split}.parquet"
            save_to_parquet(splits[split], path_to_output)
    return splits