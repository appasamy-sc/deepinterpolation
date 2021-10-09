import argschema
import json
from pathlib import Path

from deepinterpolation.cli.schemas import TrainingInputSchema
from deepinterpolation.generic import ClassLoader


class Training(argschema.ArgSchemaParser):
    default_schema = TrainingInputSchema

    def run(self):
        self.logger.name = type(self).__name__

        outdir = Path(self.args['training_params']['output_path'])
        if self.args["output_full_args"]:
            full_args_path = outdir / "training_full_args.json"
            with open(full_args_path, "w") as f:
                json.dump(self.args, f, indent=2)
            self.logger.info(f"wrote {full_args_path}")
        uid = self.args['run_uid']

        # We create the output model filename if empty
        if self.args['training_params']["model_string"] == "":
            self.args['training_params']["model_string"] = (
                self.args["network_params"]["name"] + "_" +
                self.args["training_params"]["loss"]
            )

        # We pass on the uid
        self.args["training_params"]["run_uid"] = uid

        # We pass on folder
        self.args["training_params"]["output_dir"] = self.args['training_params']['output_path']

        # We convert to old schema
        self.args['training_params']['nb_gpus'] = 2 * \
            int(self.args['training_params']['multi_gpus'])

        # Forward parameters to the training agent
        self.args['training_params']['steps_per_epoch'] = \
            self.args['generator_params']['steps_per_epoch']
        self.args['training_params']['batch_size'] = \
            self.args['generator_params']['batch_size']

        # save the json parameters to 2 different files
        training_json_path = outdir / f"{uid}_training.json"
        with open(training_json_path, "w") as f:
            json.dump(self.args['training_params'], f,  indent=2)
        self.logger.info(f"wrote {training_json_path}")

        generator_json_path = outdir / f"{uid}_generator.json"
        with open(generator_json_path, "w") as f:
            json.dump(self.args['generator_params'], f, indent=2)
        self.logger.info(f"wrote {generator_json_path}")

        network_json_path = outdir / f"{uid}_network.json"
        with open(network_json_path, "w") as f:
            json.dump(self.args['network_params'], f, indent=2)
        self.logger.info(f"wrote {network_json_path}")

        test_generator_json_path = outdir / f"{uid}_test_generator.json"
        with open(test_generator_json_path, "w") as f:
            json.dump(self.args['test_generator_params'], f, indent=2)
        self.logger.info(f"wrote {test_generator_json_path}")

        generator_obj = ClassLoader(generator_json_path)
        data_generator = generator_obj.find_and_build()(generator_json_path)

        test_generator_obj = ClassLoader(test_generator_json_path)
        data_test_generator = test_generator_obj.find_and_build()(
            test_generator_json_path
        )

        network_obj = ClassLoader(network_json_path)
        data_network = network_obj.find_and_build()(network_json_path)

        training_obj = ClassLoader(training_json_path)

        training_class = training_obj.find_and_build()(
            data_generator,
            data_test_generator,
            data_network,
            training_json_path
        )

        self.logger.info("created objects for training")
        training_class.run()

        self.logger.info("training job finished - finalizing output model")
        training_class.finalize()


if __name__ == "__main__":  # pragma: nocover
    infer = Training()
    infer.run()
