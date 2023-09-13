import copy
import json
import tempfile
from typing import Any, Optional

import strangeworks as sw
from strangeworks.core.client.backends import Backend
from strangeworks.core.client.jobs import Job
from strangeworks.core.errors.error import StrangeworksError
from strangeworks_core.types.job import Status
from strangeworks_optimization_models.problem_models import (
    StrangeworksModel,
    StrangeworksModelFactory,
)
from strangeworks_optimization_models.solution_models import (
    StrangeworksSolution,
    StrangeworksSolutionFactory,
)
from strangeworks_optimization_models.solver_models import (
    StrangeworksSolver,
    StrangeworksSolverFactory,
)
from strangeworks_optimization_models.strangeworks_models import (
    StrangeworksOptimizationJob,
    StrangeworksOptimizationModel,
    StrangeworksOptimizationSolution,
    StrangeworksOptimizationSolver,
)


class StrangeworksOptimizer:
    """Strangeworks optimization controller."""

    model: StrangeworksModel | None = None
    solver: StrangeworksSolver | None = None
    solution: StrangeworksSolution | None = None
    job: Job | None = None
    resource_slug: str | None = None

    def __init__(
        self,
        model: Any | None = None,
        solver: Any | None = None,
        options: dict | None = None,
        solution: Any | None = None,
        resource_slug: str | None = None,
    ) -> None:
        self.model = StrangeworksModelFactory.from_model(model) if model else None
        self.solver = StrangeworksSolverFactory.from_solver(solver)
        self.options = options
        self.solution = StrangeworksSolutionFactory.from_solution(solution)
        self.resource_slug = resource_slug  # This is here so a user can pass in a resource slug if they want to

        self._init_resource()

    def _init_resource(self):
        if self.resource_slug:
            self.resource = sw.resources(slug=self.resource_slug)[0]
        else:
            rsc_list = sw.resources()
            for rr in range(len(rsc_list)):
                if rsc_list[rr].product.slug == "optimization":
                    self.resource = rsc_list[rr]

        if self.solver:
            product = self.solver.provider
            rsc_list = sw.resources()
            for rr in range(len(rsc_list)):
                if product.lower() in rsc_list[rr].product.name.lower():
                    self.sub_rsc = rsc_list[rr]

            self.solver.strangeworks_parameters = {
                "sub_product_slug": self.sub_rsc.product.slug,
                "sub_resource_slug": self.sub_rsc.slug,
            }

    def run(self) -> Job | None:
        solver = StrangeworksOptimizationSolver.from_solver(self.solver)

        if self.options and not isinstance(self.options, dict):  # check for backwards compatibility
            # Transform options class to dict and remove entries that are None
            options = copy.deepcopy(self.options.__dict__)
            for k, v in self.options.__dict__.items():
                if not v:
                    options.pop(k)
        else:
            options = self.options
        solver.solver_options = json.dumps(options) if self.options else json.dumps(None)

        strangeworks_optimization_job = StrangeworksOptimizationJob(
            model=StrangeworksOptimizationModel.from_model(self.model),
            solver=solver,
            solution=StrangeworksOptimizationSolution.from_solution(self.solution) if self.solution else None,
        )
        res = sw.execute(self.resource, payload=strangeworks_optimization_job.dict(), endpoint="run")

        job_slug = json.loads(res["solution"]["strangeworks_parameters"])["job_slug"]
        self.job = sw.jobs(slug=job_slug)[0]
        return self.job

    def results(self, sw_job_slug):
        endpoint = f"results/{sw_job_slug}"
        solution = sw.execute(self.resource, endpoint=endpoint)
        solution = StrangeworksOptimizationSolution(**solution)

        if solution.solution == "running":
            raise StrangeworksError("Job not complete")

        return solution.deserialize()

    def status(self, sw_job_slug) -> Status:
        endpoint = f"status/{sw_job_slug}"
        resp = sw.execute(self.resource, endpoint=endpoint)
        return Status(resp)

    def upload_model(self, model=None) -> str | None:
        strangeworks_optimization_model = StrangeworksOptimizationModel.from_model(model=model or self.model)
        with tempfile.NamedTemporaryFile(mode="w+") as t:
            t.write(strangeworks_optimization_model.json())

            f = sw.upload_file(t.name)
        return f.url if isinstance(f.url, str) else None

    def backends(self) -> Optional[Backend]:
        """List of optimization backends."""
        # get resources associated with this workspace
        resources = sw.resources()
        # if workspace has no resources, return an empty list.
        if not resources:
            return []
        # generate list of product slugs to use for filtering backends.
        product_slugs = [x.product.slug for x in resources]
        backends = sw.backends(
            product_slugs=product_slugs,
            backend_type_slugs=["optimization"],
        )

        return backends
