"""
Utility to split a JSON file into shards such that no shard is too
big or has too many keys.  Her, "too big" are "too many keys" are
parameterized, see command-line flags below.

Example Usage:

# Install dependencies
pip install fire
pip install json
pip install ijson

# Specify paths of input and output files
INPUT_PATH="/tmp/input.json"
OUTPUT_PATH_PREFIX=/tmp/output_"
MAX_BYTES_PER_SHARD=100000
MAX_KEYS_PER_SHARD=100

# Example Usage:
python trim_listing_batch.py \
    --input_path $INPUT_PATH \
    --output_path_prefix $OUTPUT_PATH_PREFIX \
    --max_bytes_per_shard $MAX_BYTES_PER_SHARD \
    --max_keys_per_shard $MAX_KEYS_PER_SHARD

# Expect: files with names starting with '/tmp/output_' such that
# no shard has more than 100000 bytes or 100 listings.

# See the `split_json` function definition below for detailed documentation.
"""

from typing import Any, Optional

import fire
import ijson
import json


def write_file(
    path_prefix: str,
    file_index: int,
    kv_pairs: list[str, Any],
):
    """Writes key-value pairs into an output file in JSON format.

    Args:
        path_prefix(str): The prefix for output filenames.
        file_index(int): An integer that is appended to `path_prefix` to
            construct the final name of the output file.
        kv_pairs(List[str, Any]): The key-value pairs that will be written
            into the output file.
    """

    output_filename = path_prefix + str(file_index) + ".json"

    output_file_path = f"{path_prefix}_{file_index}.json"
    try:
        with open(output_file_path, "w") as output_file:
            json.dump(dict(kv_pairs), output_file)
    except Exception as err:
        print(f"Exception: {repr(err)} while writing to {output_filename}")
        exit()
    print(f"Wrote {output_file_path} with {len(kv_pairs)} keys")


def split_json(
    input_path: str = None,
    output_path_prefix: str = None,
    max_keys_per_shard: Optional[int] = 10,
    max_bytes_per_shard: Optional[int] = 100000,
):
    """Truncate a batch of listings to a fixed maximum size.

    Args:
        input_path (str):
            The path to the input batch JSON file.
        output_path_prefix (str):
            The prefix for output filenames. If the output files exist,
            they will be overwritten.
        max_keys_per_shard (int):
            The maximum number of listings per output file.
        max_bytes_per_shard (int):
            The maximum number of bytes per output file.  Note that this
            is not guaranteed if there are key-value pairs whose size
            exceeds this argument.
    """

    # Track the number of files and the total number of JSON keys written.
    filenum = 0
    total_keys = 0

    try:
        # Open the input file as a stream and create an ijson iterator.
        with open(input_path, "rb") as input_file:
            listings = ijson.kvitems(input_file, prefix="")

            # Initialize variables for tracking the current shard.
            size = 0
            shard = []

            for k, v in listings:
                # Compute the size of the next (k, v) pair; add a bit of
                # padding to account for the JSON special characters {"":}.
                record_size = len(repr(k)) + len(repr(v)) + 10

                # Dump the current shard if we have enough keys,
                # or if adding this (k, v) pair would cause the shard to
                # become too large.
                if (
                    len(shard) >= max_keys_per_shard
                    or size + record_size > max_bytes_per_shard
                ):
                    # It's possible that the very first record is too large.
                    if len(shard) > 0:
                        write_file(output_path_prefix, filenum, shard)
                        size = 0
                        total_keys += len(shard)
                        filenum += 1
                        shard = []

                size += record_size
                shard.append((k, v))

            # Write any remaining items to a file
            if len(shard) > 0:
                write_file(output_path_prefix, filenum, shard)
                total_keys += len(shard)
                filenum += 1

    except Exception as err:
        print(f"Exception: {repr(err)} while reading {input_path}")
        return

    # Final summary
    print(f"Wrote {filenum} files with a total of {total_keys} keys")


if __name__ == "__main__":
    fire.Fire(split_json)
