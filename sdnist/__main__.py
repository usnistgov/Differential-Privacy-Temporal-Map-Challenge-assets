import argparse
import pathlib

import pandas as pd

import sdnist


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Compute the k-marginal score of a given .csv dataset")
    parser.add_argument("dataset", type=argparse.FileType("r"),
                        help="Location of synthetic dataset to score (.csv file)")
    parser.add_argument("--challenge", choices=["census", "taxi"], default="census",
                        help="Select challenge for which to score the synthetic data file. \n"
                             "Default data file used by the census challenge: \"IL_OH_10Y_PUMS\".\n"
                             "Default data file used by the taxi challenge: \"taxi\"")
    parser.add_argument("--root", type=pathlib.Path,
                        help="Root of target dataset", default=pathlib.Path("data"))
    parser.add_argument("--test-dataset", choices=[_.name for _ in sdnist.load.TestDatasetName],
                        default="NONE",
                        help="Select test target dataset against which to score the synthetic data file."
                             "Test datasets for the census challenge: \n"
                             "[\"GA_NC_SC_10Y_PUMS\", \n"
                             "\"NY_PA_10Y_PUMS\"]. \n"
                             "Test datasets for the taxi challenge: \n"
                             "[\"taxi2016\", \n"
                             "\"taxi2020\"]")
    parser.add_argument("--download", type=bool, default=True,
                        help="Download all datasets in 'root' if the target dataset is not present")
    parser.add_argument("--html", type=bool, default=True,
                        help="Output the result to an html page (only available on the ACS public dataset). ")

    args = parser.parse_args()

    is_public = True if args.test_dataset == "NONE" else False

    # Load target dataset
    target, schema = sdnist.load.load_dataset(
        challenge=args.challenge,
        root=args.root,
        download=args.download,
        public=is_public,
        test=sdnist.load.TestDatasetName[args.test_dataset]
    )

    dataset_path = sdnist.load.build_name(challenge=args.challenge,
                                          root=args.root,
                                          public=is_public,
                                          test=sdnist.load.TestDatasetName[args.test_dataset])

    print(f'Loaded dataset at path: {dataset_path}')

    # Load actual dataset
    dtypes = {feature: desc["dtype"] for feature, desc in schema.items()}
    synthetic = pd.read_csv(args.dataset, dtype=dtypes)

    # Compute and print score
    score = sdnist.score(target, synthetic, 
                         schema=schema,
                         challenge=args.challenge)

    if args.html:
        score.html(target_dataset_path=dataset_path,
                   browser=True)
