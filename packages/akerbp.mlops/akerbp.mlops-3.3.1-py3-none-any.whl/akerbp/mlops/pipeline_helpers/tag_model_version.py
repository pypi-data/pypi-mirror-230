import os
import logging
import argparse
import subprocess
import akerbp.mlops.model_manager as mm


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("model_name", type=str, help="Name of model")
    args = parser.parse_args()
    model_name = args.model_name

    logging.disable()
    mm.setup()
    env = os.environ.get("MODEL_ENV")
    try:
        latest_deployed_model = (
            mm.get_model_version_overview(
                model_name=model_name,
                env=env,
                output_logs=False,
            )
            .sort_values(by="uploaded_time", ascending=False)
            .iloc[0]
        )
        version_number = latest_deployed_model.external_id.split("/")[-1]

        try:
            bash_script_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "tag_commit.sh"
            )
            subprocess.run(["chmod", "+x", bash_script_path])
            subprocess.run([bash_script_path, version_number])
        except subprocess.CalledProcessError as e:
            print(f"Tagging commit returned an error: {e}")
    except IndexError as e:
        raise Exception(
            f"No version of model {model_name} found in the model registry"
        ) from e


if __name__ == "__main__":
    main()  # type: ignore
