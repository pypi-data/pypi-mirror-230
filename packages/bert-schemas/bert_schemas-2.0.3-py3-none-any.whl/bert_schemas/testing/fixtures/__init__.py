from collections import namedtuple

import pytest

from .job import *


@pytest.fixture
def job_fixtures(
    post_bec_job,
    post_barrier_job,
    post_paint1d_job,
    pending_bec_job,
    running_bec_job,
    complete_bec_job,
    complete_barrier_job,
    complete_paint_1d_job,
    failed_bec_job,
    post_bec_batch_job,
    pending_bec_batch_job,
    running_bec_batch_job,
    complete_bec_batch_job,
    failed_bec_batch_job,
):
    JobFixtures = namedtuple(
        "JobFixtures",
        [
            "post_bec_job",
            "post_barrier_job",
            "post_paint1d_job",
            "pending_bec_job",
            "running_bec_job",
            "complete_bec_job",
            "complete_barrier_job",
            "complete_paint_1d_job",
            "failed_bec_job",
            "post_bec_batch_job",
            "pending_bec_batch_job",
            "running_bec_batch_job",
            "complete_bec_batch_job",
            "failed_bec_batch_job",
        ],
    )
    yield JobFixtures(
        post_bec_job,
        post_barrier_job,
        post_paint1d_job,
        pending_bec_job,
        running_bec_job,
        complete_bec_job,
        complete_barrier_job,
        complete_paint_1d_job,
        failed_bec_job,
        post_bec_batch_job,
        pending_bec_batch_job,
        running_bec_batch_job,
        complete_bec_batch_job,
        failed_bec_batch_job,
    )
