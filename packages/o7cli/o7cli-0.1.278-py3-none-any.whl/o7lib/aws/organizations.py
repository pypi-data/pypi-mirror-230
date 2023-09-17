#************************************************************************
# Copyright 2023 O7 Conseils inc (Philippe Gosselin)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#************************************************************************
"""Module allows to view and access Organizations"""


#--------------------------------
#
#--------------------------------
import pprint
import logging


import o7lib.aws.base
import o7lib.util.displays


logger=logging.getLogger(__name__)



#*************************************************
#
#*************************************************
class Organizations(o7lib.aws.base.Base):
    """Class for Organizationr """

    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/organizations.html

    #*************************************************
    #
    #*************************************************
    def __init__(self, profile = None, region = None, session = None):
        super().__init__(profile=profile, region=region, session = session)
        self.organizations = self.session.client('organizations')



    #*************************************************
    #
    #*************************************************
    def load_accounts(self):
        """Load all linked accounts"""

        logger.info('load_parameters')

        paginator = self.organizations.get_paginator('list_accounts')
        linked_accounts = []

        for page in paginator.paginate():
            accounts = page.get('Accounts', [])
            logger.info(f'load_accounts: Number of Secret found {len(accounts)}')
            linked_accounts.extend(accounts)

        return linked_accounts

    #*************************************************
    #
    #*************************************************
    def display_accounts(self, accounts):
        """Diplay Accounts"""
        self.console_title(left='Linked Account List')
        print('')
        params = {
            'columns' : [
                {'title' : 'i',     'type': 'i',    'minWidth' : 4  },
                {'title' : 'Id',    'type': 'str',  'dataName': 'Id'},
                {'title' : 'Name',  'type': 'str',  'dataName': 'Name'},
                {'title' : 'Status', 'type': 'str', 'dataName': 'Status'},
            ]
        }
        o7lib.util.displays.Table(params, accounts)



#*************************************************
#
#*************************************************
if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)-5.5s] [%(name)s] %(message)s"
    )

    the_obj = Organizations()
    the_accounts = the_obj.load_accounts()
    the_obj.display_accounts(the_accounts)
    # pprint.pprint(the_accounts)

