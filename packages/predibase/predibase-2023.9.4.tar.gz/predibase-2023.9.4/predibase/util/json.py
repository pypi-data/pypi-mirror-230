from typing import Dict


def max_epochs_of_model_response(model: Dict):
    if "modelRun" in model and "renderedConfig" in model["modelRun"]:
        return model["modelRun"]["renderedConfig"]["trainer"]["epochs"]
    return None
