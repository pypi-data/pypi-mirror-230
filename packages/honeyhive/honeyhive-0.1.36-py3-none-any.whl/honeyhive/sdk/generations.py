from typing import Dict, List, Optional, Any
from honeyhive.api.models.generations import (
    GenerateQuery,
    GenerationsQuery,
    GenerationResponse,
    ListGenerationResponse,
    GenerationLoggingQuery,
)
from honeyhive.sdk.init import honeyhive_client
import pandas as pd


def generate(
    project: str,
    input: Dict[str, str],
    prompts: Optional[List[str]] = None,
    model_id: Optional[str] = None,
    best_of: Optional[int] = None,
    metric: Optional[str] = None,
    sampling: Optional[str] = None,
    user_properties: Optional[Dict[str, Any]] = None,
    source: Optional[str] = None,
    stream: Optional[bool] = False
) -> GenerationResponse:
    """Generate completions"""
    client = honeyhive_client()

    if stream == False:
        return client.generate(
            generation=GenerateQuery(
                task=project,
                input=input,
                prompts=prompts,
                model_id=model_id,
                best_of=best_of,
                metric=metric,
                sampling=sampling,
                user_properties=user_properties,
                source=source,
            )
        )
    else:
        return client.generate_stream(
            generation=GenerateQuery(
                task=project,
                input=input,
                prompts=prompts,
                model_id=model_id,
                best_of=best_of,
                metric=metric,
                sampling=sampling,
                user_properties=user_properties,
                source=source,
                stream=stream
            )
        )


def get_generations(project: Optional[str] = None, query: Optional[Dict[str, Any]] = None, limit: Optional[int] = None):
    """Get all generations"""
    client = honeyhive_client()
    generations_list = client.get_generations(
        query=GenerationsQuery(
            task=project
        )
    )
    
    if query == None:
        query = {}
    
    print(generations_list["pagination"])

    # go through the pages and get all the generations
    while generations_list["pagination"]["nextPage"] != None:
        query["page"] = generations_list["pagination"]["nextPage"]
        page=query["page"]
        #print("page", page)
        next_page = client.get_generations(
            query=GenerationsQuery(
                task=project,
                page=page
            )
        )
        generations_list["generations"] += next_page["generations"]
        generations_list["pagination"]["nextPage"] = next_page["pagination"]["nextPage"]
        #print(generations_list["pagination"])

        if limit != None and len(generations_list["generations"]) >= limit:
            break
    
    import pandas as pd

    df = pd.DataFrame(generations_list["generations"])
    return df


def log(
    project: str,
    model: str,
    generation: str,
    hyperparameters: Dict[str, Any],
    source: Optional[str] = None,
    version: Optional[str] = None,
    prompt_template: Optional[str] = None,
    inputs: Optional[Dict[str, Any]] = None,
    prompt: Optional[str] = None,
    ground_truth: Optional[str] = None,
    usage: Optional[Dict[str, Any]] = None,
    latency: Optional[float] = None,
    user_properties: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    feedback: Optional[Dict[str, Any]] = None,
) -> GenerationResponse:
    # log generation via honeyhive
    client = honeyhive_client()

    if prompt == None:
        prompt = prompt_template
        if inputs == None and prompt_template == None:
            # throw an exception
            return Exception(
                "Please provide either a complete prompt or prompt template with inputs"
            )

    honeyhive_response = client.log_generation(
        generation=GenerationLoggingQuery(
            task=project,
            version=version,
            model=model,
            prompt=prompt,
            inputs=inputs,
            hyperparameters=hyperparameters,
            generation=generation,
            usage=usage,
            latency=latency,
            source=source,
            user_properties=user_properties,
            metadata=metadata,
            ground_truth=ground_truth,
            feedback=feedback,
        )
    )

    return honeyhive_response


__all__ = ["generate", "log", "get_generations"]
