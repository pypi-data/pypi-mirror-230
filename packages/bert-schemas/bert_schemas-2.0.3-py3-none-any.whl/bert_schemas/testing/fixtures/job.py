"""Pytest fixtures for jobs"""

import pytest

from ..factories.helpers import add_notes
from ..factories import job as JobFactories
from collections import namedtuple


@pytest.fixture
def post_bec_job():
    job = JobFactories.BecJobPostFactory.build()
    yield job


@pytest.fixture
def post_barrier_job():
    job = JobFactories.BarrierJobPostFactory.build()
    yield job


@pytest.fixture
def post_paint1d_job():
    job = JobFactories.Paint1dJobPostFactory.build()
    yield job


@pytest.fixture
def pending_bec_job():
    job = JobFactories.BecJobPendingFactory.build()
    job = add_notes(job)
    yield job


@pytest.fixture
def running_bec_job():
    job = JobFactories.BecJobRunningFactory.build()
    job = add_notes(job)
    yield job


@pytest.fixture
def complete_bec_job():
    job = JobFactories.BecJobCompleteFactory.build()
    job = add_notes(job)
    yield job


@pytest.fixture
def complete_barrier_job():
    job = JobFactories.BarrierJobCompleteFactory.build()
    job = add_notes(job)
    yield job


@pytest.fixture
def complete_paint_1d_job():
    job = JobFactories.Paint1dJobCompleteFactory.build()
    job = add_notes(job)
    yield job


@pytest.fixture
def failed_bec_job():
    job = JobFactories.BecJobFailedFactory.build()
    job = add_notes(job)
    yield job


@pytest.fixture
def post_bec_batch_job():
    job = JobFactories.BecBatchJobPostFactory.build()
    yield job


@pytest.fixture
def pending_bec_batch_job():
    job = JobFactories.BecBatchJobPendingFactory.build()
    job = add_notes(job)
    yield job


@pytest.fixture
def running_bec_batch_job():
    job = JobFactories.BecBatchJobRunningFactory.build()
    job = add_notes(job)
    yield job


@pytest.fixture
def complete_bec_batch_job():
    job = JobFactories.BecBatchJobCompleteFactory.build()
    job = add_notes(job)
    yield job


@pytest.fixture
def failed_bec_batch_job():
    job = JobFactories.BecBatchJobFailedFactory.build()
    job = add_notes(job)
    yield job


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
