import os
import csv as csvmod
import time
import click
import random
from talc.evals import EvalsClient, TestCaseResponse, TestCaseWithRubric


talc_api_key: str | None = os.getenv("TALC_API_KEY", None)
talc_base_url: str | None = os.getenv("TALC_BASE_URL", "http://localhost:8000")


@click.group()
def evals():
    pass


@evals.command()
@click.option("--count", default=0, help="Number of cases to sample (0 for all).")
@click.option("--api_key", default=talc_api_key, help="Talc API key")
@click.option("--dataset", prompt="Dataset ID", help="The ID of the dataset to load.")
@click.option("--csv", default=None, help="Path to CSV file to save results to.")
def getdataset(count: int, dataset: str, api_key: str, csv: str) -> None:
    """Download or pretty print a test dataset from the server."""

    if api_key is None:
        raise click.UsageError(
            "No API key provided. Please set the TALC_API_KEY environment variable or provide the --api_key option."
        )

    client = EvalsClient(api_key, talc_base_url)
    data = client.get_dataset(dataset)

    if count == 0:
        count = len(dataset)

    random.shuffle(data)

    if csv is not None:
        with open(csv, "w", newline="") as csvfile:
            writer = csvmod.writer(csvfile)
            writer.writerow(["id", "content"])
            for case in data[:count]:
                writer.writerow([case.id, case.question])

    for case in data[:count]:
        print(case.question)


@evals.command()
@click.option("--api_key", default=talc_api_key, help="Talc API key")
@click.option(
    "--csv",
    prompt="Results CSV path",
    help="Path to CSV file to load results from. Columns should be 'id', 'result'. Header row is optional.",
)
@click.option("--print_failed", is_flag=True, help="Print the failed test cases.")
def grade(api_key: str, csv: str, print_failed: bool):
    """Grade a test run from a csv. Columns should be 'id', 'result'. Header row is optional."""

    if api_key is None:
        raise click.UsageError(
            "No API key provided. Please set the TALC_API_KEY environment variable or provide the --api_key option."
        )

    client = EvalsClient(api_key, talc_base_url)

    with open(csv, newline="") as csvfile:
        reader = csvmod.reader(csvfile)

        # Skip the first row. If it's not a header, we add it back later.
        row = next(reader, None)
        if row is None:
            raise click.UsageError("CSV file is empty.")

        results = [TestCaseResponse(id=row[0], response=row[1]) for row in reader]

        # If the first row is not a header, add it back to the results.
        if row[0] != "id" or row[1] != "result":
            results.append(TestCaseResponse(id=row[0], response=row[1]))

    run_info = client.start_run()
    client.submit_responses(results)
    print("Submitted results. Beginning grading for run ID: " + run_info.id)

    while True:
        run_info = client.get_results()
        print(f"Progress: {run_info.completion_progress * 100}%")
        if run_info.completion_progress >= 1:
            print("\n=============================================")
            print("Grading complete.")
            print(f"Accuracy: {run_info.grade_accuracy}")
            print(f"Hallucination: {run_info.grade_hallucination}")
            print("=============================================\n")
            if print_failed and run_info.failed_cases is not None:
                print("Failed cases:")
                for case in run_info.failed_cases:
                    print(
                        f"{case.id}: {case.question} -> {case.response} ({case.grade_reason})"
                    )
            break
        time.sleep(2)


@evals.command()
@click.option("--api_key", default=talc_api_key, help="Talc API key")
@click.option("--run_id", prompt="Run ID", help="The ID of the run to get results for.")
@click.option("--print_failed", is_flag=True, help="Print the failed test cases.")
def getresults(api_key: str, run_id: str, print_failed: bool):
    """Get the grades for a test run."""

    if api_key is None:
        raise click.UsageError(
            "No API key provided. Please set the TALC_API_KEY environment variable or provide the --api_key option."
        )

    client = EvalsClient(api_key, talc_base_url, run_id)
    run_grade = client.get_results()

    print(f"Accuracy: {run_grade.grade_accuracy}")
    print(f"Hallucination: {run_grade.grade_hallucination}")

    if print_failed and run_grade.failed_cases is not None:
        print("Failed cases:")
        for case in run_grade.failed_cases:
            print(
                f"{case.id}: {case.question} -> {case.response} ({case.grade_reason})"
            )


@evals.command()
@click.option("--api_key", default=talc_api_key, help="Talc API key")
@click.option(
    "--csv",
    prompt="CSV path",
    help="Path to CSV file to upload. Columns should be 'question' and 'expected answer'.",
)
@click.option("--name", prompt="Dataset name", help="The name of the dataset.")
def adddataset(api_key: str, csv: str, name: str):
    """Add a new dataset to the server."""

    if api_key is None:
        raise click.UsageError(
            "No API key provided. Please set the TALC_API_KEY environment variable or provide the --api_key option."
        )

    client = EvalsClient(api_key, talc_base_url)

    with open(csv, newline="") as csvfile:
        reader = csvmod.reader(csvfile)

        # Skip the first row. If it's not a header, we add it back later.
        header = next(reader, None)
        if header is None:
            raise click.UsageError("CSV file is empty.")

        dataset = [
            TestCaseWithRubric(
                question=row[0], expected_response=row[1], scenario_data={}, id=None
            )
            for row in reader
        ]

        # If the first row is not a header, add it back to the results.
        if header[0] != "question" or header[1] != "expected answer":
            dataset.append(
                TestCaseWithRubric(
                    question=header[0],
                    expected_response=header[1],
                    scenario_data={},
                    id=None,
                )
            )

    dataset_id = client.create_dataset(name, dataset)
    print(f"Dataset created with ID: {dataset_id}")


def main():
    evals()
