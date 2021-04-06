import argschema
import json
from pathlib import Path

from deepinterpolation.cli.schemas import InferenceInputSchema
from deepinterpolation.generic import ClassLoader


class Inference(argschema.ArgSchemaParser):
    default_schema = InferenceInputSchema

    def run(self):
        self.logger.name = type(self).__name__

        outdir = Path(self.args['inference_params']['output_file']).parent
        uid = self.args['run_uid']

        # save the json parameters to 2 different files
        inference_json_path = outdir / f"{uid}_inference.json"
        with open(inference_json_path, "w") as f:
            json.dump(self.args['inference_params'], f,  indent=2)
        self.logger.info(f"wrote {inference_json_path}")

        generator_json_path = outdir / f"{uid}_generator.json"
        with open(generator_json_path, "w") as f:
            json.dump(self.args['generator_params'], f, indent=2)
        self.logger.info(f"wrote {generator_json_path}")

        generator_obj = ClassLoader(generator_json_path)
        data_generator = generator_obj.find_and_build()(generator_json_path)

        inferrence_obj = ClassLoader(inference_json_path)
        inferrence_class = inferrence_obj.find_and_build()(
                inference_json_path,
                data_generator)

        self.logger.info("created objects for inference")

        inferrence_class.run()


if __name__ == "__main__":
    infer = Inference()
    infer.run()