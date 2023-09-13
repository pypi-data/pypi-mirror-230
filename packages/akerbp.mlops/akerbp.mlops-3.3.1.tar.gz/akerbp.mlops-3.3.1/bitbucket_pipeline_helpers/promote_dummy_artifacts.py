import os
import akerbp.mlops.model_manager as mm

env = os.environ.get("MODEL_ENV", "dev")

if env == "dev":
    promote_to = "test"
elif env == "test":
    promote_to = "prod"
else:
    raise ValueError(f"Invalid environment {env}, must be either 'dev' or 'test'")

mm.setup()
mm.promote_model(
    model_name="mlopsdemo",
    promote_to=promote_to,
    confirm=False,
)
