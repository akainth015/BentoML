import logging

from bentoml.yatai.proto.repository_pb2 import BentoUri
from bentoml.yatai.client import get_yatai_client
from e2e_tests.sample_bento_service import SampleBentoService
from e2e_tests.yatai_server.utils import (
    execute_bentoml_run_command,
    local_yatai_server,
)

logger = logging.getLogger('bentoml.test')


def test_yatai_server_with_postgres_and_gcs(postgres_db_container_url):

    gcs_bucket_name = 'gs://bentoml-e2e-tests/'

    with local_yatai_server(
        db_url=postgres_db_container_url, repo_base_url=gcs_bucket_name
    ) as yatai_service_url:
        yc = get_yatai_client(yatai_service_url)
        logger.info('Saving bento service')
        svc = SampleBentoService()
        svc.save(yatai_url=yatai_service_url)
        bento_tag = f'{svc.name}:{svc.version}'
        logger.info('BentoService saved')

        logger.info("Display bentoservice info")
        bento = yc.repository.get(bento_tag)
        logger.info(bento)
        assert (
            bento.uri.type == BentoUri.GCS
        ), 'BentoService storage type mismatched, expect GCS'

        logger.info('Validate BentoService prediction result')
        run_result = execute_bentoml_run_command(bento_tag, '[]')
        assert 'cat' in run_result, 'Unexpected BentoService prediction result'

        logger.info(f'Deleting saved bundle {bento_tag}')
        yc.repository.delete(bento_tag=bento_tag)
