import argparse
import json
from typing import List, Tuple

import numpy as np
import pandas as pd
from joblib import dump, load
from sklearn.base import BaseEstimator
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from radops.data_lake import File, add_from_url, file_creator


def add_iris():
    """adds the iris dataset to the datalake"""
    return add_from_url(
        url="https://gist.github.com/netj/8836201/raw/6f9306ad21398ea43cba4f7d537619d0e07d5ae3/iris.csv",
        output_uid="iris.csv",
    )


def load_df_from_file(f: File) -> pd.DataFrame:
    """helper method to load a dataframe from a file"""
    with f.open("r") as fileobj:
        df = pd.read_csv(fileobj)

    return df


def Xy_from_df(df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    X = df[
        ["sepal.length", "sepal.width", "petal.length", "petal.width"]
    ].to_numpy()
    y = df["variety"].to_numpy()

    return X, y


def load_model_from_file(model_file: File) -> BaseEstimator:
    with model_file.open("rb") as fileobj:
        model = load(fileobj)

    return model


@file_creator
def create_train_val_split(
    dataset: File,
    train_fraction: float,
    output_uids: List[str],
) -> List[File]:
    with dataset.open("r") as fileobj:
        df = pd.read_csv(fileobj)

    train_df = df.sample(frac=train_fraction)
    val_df = df.drop(train_df.index)

    train_file, val_file = File(output_uids[0]), File(output_uids[1])
    with train_file.open("w") as fileobj:
        train_df.to_csv(fileobj, index=False)

    with val_file.open("w") as fileobj:
        val_df.to_csv(fileobj, index=False)

    return [train_file, val_file]


@file_creator
def train(train_file: File, output_uid: str) -> File:
    """Trains a linear model and saves it to the data lake."""
    train_df = load_df_from_file(train_file)

    X, y = Xy_from_df(train_df)

    pipeline = Pipeline(
        [("scaler", StandardScaler()), ("linear_model", LogisticRegression())]
    )

    pipeline.fit(X, y)

    model_file = File(output_uid)
    with model_file.open("wb") as fileobj:
        dump(pipeline, fileobj)

    return model_file


def evaluate(model_file: File, val_file: File):
    val_df = load_df_from_file(val_file)
    X, y = Xy_from_df(val_df)

    model = load_model_from_file(model_file)

    preds = model.predict(X)
    print(classification_report(y, preds))


def add_model_to_chariot(
    model_file: File, project_name: str, subproject_name: str, version: str
) -> None:
    from chariot.client import connect
    from chariot.models import ArtifactType, TaskType, import_model

    for s in [project_name, version]:
        if s is None:
            raise ValueError("'project_name' and 'version' must be specified.")

    connect()

    model = load_model_from_file(model_file)

    input_info = [
        {
            "name": "Sepal length (cm)",
            "description": "Length of the iris's sepals. Sepals are the leaf-like structure surrounding the petals.",
        },
        {
            "name": "Sepal width (cm)",
            "description": "Width of the iris's sepals. Sepals are the leaf-like structures surrounding the petals.",
        },
        {
            "name": "Petal length (cm)",
            "description": "Length of the iris's petals.",
        },
        {
            "name": "Petal width (cm)",
            "description": "Width of the iris's petals.",
        },
    ]

    model = import_model(
        name="radops-iris-demo",
        project_name=project_name,
        subproject_name=subproject_name,
        version=version,
        artifact_type=ArtifactType.SKLEARN,
        task_type=TaskType.STRUCTURED_DATA_CLASSIFICATION,
        class_labels={c: i for i, c in enumerate(model.classes_)},
        summary=json.dumps({"radops.uid": model_file.uid}),
        input_info=input_info,
        model_object=model,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--add_to_chariot", action="store_true")
    parser.add_argument("--project_name", type=str)
    parser.add_argument("--subproject_name", type=str)
    parser.add_argument("--version", type=str, default="0.1.0")
    args = parser.parse_args()

    # run the data pre, training, and evaluation pipeline
    iris_dataset = add_iris()
    train_file, val_file = create_train_val_split(
        dataset=iris_dataset,
        train_fraction=0.8,
        output_uids=["iris_train.csv", "iris_val.csv"],
    )
    model_file = train(train_file=train_file, output_uid="iris_model.joblib")
    evaluate(model_file=model_file, val_file=val_file)

    if args.add_to_chariot:
        # upload the model to chariot
        add_model_to_chariot(
            model_file,
            project_name=args.project_name,
            subproject_name=args.subproject_name,
            version=args.version,
        )
