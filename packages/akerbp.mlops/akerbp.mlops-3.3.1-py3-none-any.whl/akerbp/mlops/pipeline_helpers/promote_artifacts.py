import os
import argparse
import akerbp.mlops.model_manager as mm


def main():
    parser = argparse.ArgumentParser(
        description="Promote artifacts to specified target environment"
    )
    parser.add_argument("model_name", type=str, help="Name of the model to promote")
    args = parser.parse_args()
    model_name = args.model_name
    env = os.environ.get("MODEL_ENV", None)
    if env is None:
        raise Exception("Environment variabel 'MODEL_ENV' is not set")

    if env == "dev":
        target_env = "test"
    elif env == "test":
        target_env = "prod"
    else:
        raise Exception(
            "Cannot infer target env from environment variable 'MODEL_ENV'={env}"
        )

    mm.setup()
    mm.promote_model(
        model_name=model_name,
        promote_to=target_env,
        confirm=False,
    )


if __name__ == "__main__":
    main()  # type: ignore
