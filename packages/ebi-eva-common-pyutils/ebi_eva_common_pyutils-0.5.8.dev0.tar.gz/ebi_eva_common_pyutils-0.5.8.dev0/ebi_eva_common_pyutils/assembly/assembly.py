# Copyright 2019 EMBL - European Bioinformatics Institute
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from functools import lru_cache

from ebi_eva_common_pyutils.logger import logging_config
from ebi_eva_common_pyutils.network_utils import json_request
from ebi_eva_common_pyutils.taxonomy.taxonomy import get_normalized_scientific_name_from_ensembl

logger = logging_config.get_logger(__name__)


def get_supported_asm_from_ensembl(tax_id: int) -> str:
    logger.info(f'Query Ensembl for species name using taxonomy {tax_id}')
    scientific_name_api_param = get_normalized_scientific_name_from_ensembl(tax_id)
    ENSEMBL_REST_API_URL = "http://rest.ensembl.org/info/assembly/{0}?content-type=application/json".format(
        scientific_name_api_param)
    response = json_request(ENSEMBL_REST_API_URL)
    assembly_accession_attribute = 'assembly_accession'
    if assembly_accession_attribute in response:
        return str(response.get(assembly_accession_attribute))
    return None


@lru_cache
def get_ensembl_rapid_release_data():
    list_data = json_request('https://ftp.ensembl.org/pub/rapid-release/species_metadata.json')
    return {
        d['taxonomy_id']: d['assembly_accession']
        for d in list_data
    }


def get_supported_asm_from_ensembl_rapid_release(tax_id: int) -> str:
    rapid_release_data = get_ensembl_rapid_release_data()
    return rapid_release_data.get(tax_id, None)
