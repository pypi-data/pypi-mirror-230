import os
import importlib
import inspect
from abc import ABC
from typing import Dict, Type
from croydon import ctx
from croydon.models.storable_model import StorableModel
from croydon.models.counter import Counter
from croydon.command import Command


class Index(Command):

    NAME = "index"
    HELP = "Create indexes for the application models"

    async def run_async(self) -> None:
        models_dir = os.path.join(ctx.project_dir, "app/models")
        classes: Dict[str, Type['StorableModel']] = {
            "Counter": Counter
        }

        for directory, _, files in os.walk(models_dir):
            if "__pycache__" in directory:
                continue
            rel_directory = directory[len(ctx.project_dir) + 1:]

            for filename in files:
                if filename.endswith(".py") and not filename.startswith("__"):
                    modulename = filename[:-3]
                    tokens = rel_directory.split("/")
                    tokens.append(modulename)
                    module = importlib.import_module(".".join(tokens))

                    for attr in dir(module):
                        cls = getattr(module, attr)
                        should_index = (inspect.isclass(cls) and
                                        issubclass(cls, StorableModel) and
                                        ABC not in cls.__bases__ and
                                        cls is not StorableModel)
                        if should_index:
                            classes[cls.__name__] = cls

        for cls_name, cls in classes.items():
            ctx.log.debug(f"Creating index for model {cls_name}")
            await cls.ensure_indexes(loud=True)
