
from gfl import GFL, JobGenerator
from gfl.core.strategy import TrainerStrategy, AggregatorStrategy

import mnist_model as gfl_model


if __name__ == "__main__":
    generator = JobGenerator(gfl_model)
    generator.metadata.content = "job metadata"
    generator.job_config.with_trainer(TrainerStrategy.SUPERVISED).with_aggregator(AggregatorStrategy.FED_AVG)
    generator.train_config.with_model(gfl_model.Net).with_loss(gfl_model.CrossEntropyLoss)
    generator.train_config.with_optimizer(gfl_model.MnistOptimizer)
    generator.aggregate_config.with_round(10).with_loss(gfl_model.CrossEntropyLoss)
    job = generator.generate()
    g = GFL()
    print(g.is_connected())
    if g.is_connected():
        print(g.submit_job(job))
