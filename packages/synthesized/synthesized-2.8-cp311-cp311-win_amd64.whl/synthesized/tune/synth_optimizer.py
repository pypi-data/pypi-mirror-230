from typing import Callable, Dict, Optional

from ax.modelbridge.generation_strategy import GenerationStep, GenerationStrategy
from ax.modelbridge.registry import Models
from ax.plot.contour import interact_contour
from ax.plot.slice import plot_slice
from ax.service.ax_client import AxClient
from ax.service.utils.best_point import (
    get_best_parameters_from_model_predictions,
    get_best_raw_objective_point,
)
from ax.utils.notebook.plotting import init_notebook_plotting, render
from ray import tune
from ray.tune.search.ax import AxSearch

from synthesized import HighDimSynthesizer


class SynthOptimizer:
    """A class for synthesizer optimization.

    Args:
        orig_df: The original dataframe used to train the synthesizer.
        build_and_train_fn (Callable): A function that builds and trains a synthetic model
            based on the given parameterization and the original dataframe.
            Must have signature (parameterization, orig_df)
        parameters (Dict): A dictionary of parameters and their value space for optimization.
        loss_name (Optional[str]): The name of the loss metric to use in the optimization. Defaults to None.
        custom_loss_fn (Optional[Callable]): A custom loss function.
            Defaults to None. If None is suppled then the "mean_loss" of the model is used.
        max_parallelism (int): The maximum number of parallel trials. Defaults to 4.
        num_cpus (int): The number of CPUs to use for optimization. Defaults to 4.
    """

    def __init__(
        self,
        orig_df,
        build_and_train_fn: Callable,
        parameters: Dict,
        loss_name: Optional[str] = None,
        custom_loss_fn: Optional[Callable] = None,
        max_parallelism: int = 4,
        num_cpus: int = 4,
    ):

        self.build_and_train_fn = build_and_train_fn
        self.parameters = parameters

        self.hyperparam_loss = custom_loss_fn if custom_loss_fn else self.default_loss_fn
        self.loss_name = loss_name if loss_name else "mean_loss"
        self.axc = self.create_parameter_client(
            loss_name=self.loss_name, max_parallelism=max_parallelism
        )

        self.train_evaluate = self.create_train_evaluate_func(
            self.build_and_train_fn, self.hyperparam_loss, orig_df
        )

        self.num_cpus = num_cpus

    @staticmethod
    def default_loss_fn(synth, orig_df):

        if isinstance(synth, HighDimSynthesizer):
            loss = synth.engine.history.history["total_loss"][-1].mean()
        else:
            loss = synth.history.history["total_loss"][-1].mean()

        global_step = synth.optimizer.iterations.numpy().item()

        return dict(
            mean_loss=loss,
            global_step=global_step,
        )

    @staticmethod
    def create_train_evaluate_func(build_and_train_fn, opt_func, orig_df):
        def train_func(parameterization):
            synth = build_and_train_fn(parameterization, orig_df)
            results = opt_func(synth, orig_df)
            return results

        return train_func

    def create_parameter_client(self, loss_name, max_parallelism=4):

        gs = GenerationStrategy(
            steps=[
                GenerationStep(
                    model=Models.SOBOL,
                    num_trials=10,
                    min_trials_observed=9,
                    max_parallelism=max_parallelism,
                    enforce_num_trials=True,
                    model_kwargs={"deduplicate": True, "seed": None},
                    model_gen_kwargs=None,
                ),
                GenerationStep(
                    model=Models.GPEI,
                    num_trials=-1,
                    min_trials_observed=0,
                    max_parallelism=max_parallelism,
                    enforce_num_trials=True,
                    model_kwargs=None,
                    model_gen_kwargs=None,
                ),
            ]
        )

        axc = AxClient(
            generation_strategy=gs, verbose_logging=False, enforce_sequential_optimization=False
        )
        axc.create_experiment(
            name="sdk_tuning", parameters=self.parameters, objective_name=loss_name, minimize=True
        )

        return axc

    def optimize(self, num_samples):
        """Performs optimization using the ray.tune library.

        Args:
            num_samples (int): The number of samples to evaluate.

        Returns:
            tune.Analysis: The analysis results of the optimization.
        """

        analysis = tune.run(
            self.train_evaluate,
            num_samples=num_samples,
            search_alg=AxSearch(
                ax_client=self.axc
            ),  # Note that the argument here is the `AxClient`.
            verbose=1,  # Set this level to 1 to see status updates and to 2 to also see trial results.
            # To use GPU, specify: resources_per_trial={"gpu": 1}.
            resources_per_trial={"cpu": self.num_cpus},
            max_failures=3,
            progress_reporter=tune.JupyterNotebookReporter(overwrite=True, max_progress_rows=100),
        )

        return analysis

    def get_best_params(self):
        """Retrieves the best parameters from the optimization trials.

        Returns:
            Dict: A dictionary containing the best raw and estimated parameters.
        """

        # Gets the best parameters from comparing all trials
        params_raw, params_raw_mean_value = get_best_raw_objective_point(self.axc.experiment)

        # Gets the parameters by predicting with the bayesian model
        params_estimate, (
            params_estimate_mean_value,
            params_estimate_variance,
        ) = get_best_parameters_from_model_predictions(self.axc.experiment, Models)

        return dict(
            params_raw=params_raw,
            params_raw_mean_value=params_raw_mean_value,
            params_estimate=params_estimate,
            params_estimate_mean_value=params_estimate_mean_value,
            params_estimate_variance=params_estimate_variance,
        )

    def plot_results(self, metric_name=None):
        """Plots the results of the optimization.

        Args:
            metric_name (str): The name of the metric to plot against each parameter.
            Defaults to "mean_loss" which is the default loss used if a custom_hyperparameter_loss is not defined.
        """

        init_notebook_plotting()
        render(self.axc.get_feature_importances())
        metric_name = self.loss_name if metric_name is None else metric_name

        param_names = [param["name"] for param in self.parameters]
        for param_name in param_names:
            try:
                render(
                    plot_slice(
                        self.axc.generation_strategy.model, param_name, metric_name=metric_name
                    )
                )
            except ValueError:
                pass

        render(interact_contour(self.axc.generation_strategy.model, metric_name=metric_name))

        render(self.axc.get_optimization_trace())

    def get_trial_results_as_df(self):
        """Retrieves the trial results as a pandas DataFrame.

        Returns:
            pandas.DataFrame: The trial results.
        """
        return self.axc.get_trials_data_frame()
