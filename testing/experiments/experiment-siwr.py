#! /usr/bin/env python3

"""
Example experiment for running Singularity planner images.

Note that Downward Lab assumes that the evaluated algorithms are written
in good faith. It is not equipped to handle malicious code. For example,
it would be easy to write planner code that bypasses the time and memory
limits set within Downward Lab. If you're running untrusted code, we
recommend using cgroups to enforce resource limits.

A note on running Singularity on clusters: reading large Singularity
files over the network is not optimal, so we recommend copying the
images to a local filesystem (e.g., /tmp/) before running experiments.
"""

import os
from pathlib import Path

from downward import suites
from downward.reports.absolute import AbsoluteReport
from lab.experiment import Experiment
from lab.reports import Attribute, arithmetic_mean

import project


# Create custom report class with suitable info and error attributes.
class BaseReport(AbsoluteReport):
    INFO_ATTRIBUTES = []
    ERROR_ATTRIBUTES = [
        "domain",
        "problem",
        "algorithm",
        "unexplained_errors",
        "error",
        "node",
    ]


ATTRIBUTES = [
    "run_dir",
    "length",
    "cost",
    Attribute(name="coverage", absolute=True, min_wins=False),
    Attribute(name="valid_plan_value", absolute=True, min_wins=False),
    "error",
    "expanded",
    "generated",
    Attribute("maximum_effective_width", function=max),
    Attribute("average_effective_width", function=arithmetic_mean),
    Attribute("total_time_feature_evaluation", function=sum),
    Attribute(name="total_time", absolute=True, function=max),
]


DIR = Path(__file__).resolve().parent
BENCHMARKS_DIR = DIR.parent / "benchmarks"
SKETCHES_DIR = DIR.parent.parent / "learning" / "data_kr2023" / "sketches"
IMAGES_DIR = DIR.parent / "planners"
print(BENCHMARKS_DIR)
print(SKETCHES_DIR)
print(IMAGES_DIR)

TIME_LIMIT = 1800
MEMORY_LIMIT = 8000
if project.REMOTE:
    SUITE = ["blocks_4_clear", "blocks_4_on", "delivery", "gripper", "miconic", "reward", "spanner", "visitall"]
    ENV = project.TetralithEnvironment(
        email="dominik.drexler@liu.se",
        extra_options="#SBATCH --account=snic2022-5-341",
        memory_per_cpu="8G")
else:
    SUITE = ["blocks_4_clear:p-200-0.pddl", "blocks_4_on:p-200-0.pddl", "delivery:instance_20_25_40_0.pddl", "gripper:p01.pddl", "miconic:p01.pddl", "reward:instance_60x60_0.pddl", "spanner:pfile01-001.pddl", "visitall:p01.pddl"]
    ENV = project.LocalEnvironment(processes=16)
    TIME_LIMIT = 10

exp = Experiment(environment=ENV)
exp.add_step("build", exp.build)
exp.add_step("start", exp.start_runs)
exp.add_parse_again_step()
exp.add_fetcher(name="fetch")
exp.add_parser("parser-singularity-iw.py")


def get_image(name):
    planner = name.replace("-", "_")
    image = os.path.join(IMAGES_DIR, name + ".sif")
    assert os.path.exists(image), image
    return planner, image


IMAGES = [get_image("siwr")]

for planner, image in IMAGES:
    exp.add_resource(planner, image, symlink=True)

singularity_script = os.path.join(DIR, "run-singularity-siwr.sh")
exp.add_resource("run_singularity", singularity_script)

for planner, _ in IMAGES:
    for task in suites.build_suite(BENCHMARKS_DIR, SUITE):
        for w in range(0,3):
            sketch_name = f"{task.domain}_{w}.txt"
            sketch_filename = SKETCHES_DIR / task.domain / sketch_name
            if not sketch_filename.is_file(): continue
            run = exp.add_run()
            run.add_resource("domain", task.domain_file, "domain.pddl")
            run.add_resource("problem", task.problem_file, "problem.pddl")
            run.add_resource("sketch", sketch_filename)
            run.add_command(
                "run-planner",
                [
                    "{run_singularity}",
                    f"{{{planner}}}",
                    "{domain}",
                    "{problem}",
                    "{sketch}",
                    w,
                    "sas_plan",
                ],
                time_limit=TIME_LIMIT,
                memory_limit=MEMORY_LIMIT,
            )
            run.set_property("domain", task.domain)
            run.set_property("problem", task.problem)
            run.set_property("algorithm", f"{planner}_{w}")
            run.set_property("id", [f"{planner}_{w}", task.domain, task.problem])

report = os.path.join(exp.eval_dir, f"{exp.name}.html")
exp.add_report(BaseReport(attributes=ATTRIBUTES), outfile=report)

exp.run_steps()
