# -*- coding: utf-8 -*-
import os
import time
import unittest
import subprocess
import logging
from configparser import ConfigParser

from centrifuge.centrifugeImpl import centrifuge
from centrifuge.centrifugeServer import MethodContext
from centrifuge.authclient import KBaseAuth as _KBaseAuth

from installed_clients.WorkspaceClient import Workspace


class centrifugeTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('centrifuge'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'centrifuge',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = Workspace(cls.wsURL)
        cls.serviceImpl = centrifuge(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        suffix = int(time.time() * 1000)
        cls.wsName = "test_ContigFilter_" + str(suffix)
        ret = cls.wsClient.create_workspace({'workspace': cls.wsName})  # noqa

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    def test_your_method(self):
        # Prepare test objects in workspace if needed using
        # self.getWsClient().save_objects({'workspace': self.getWsName(),
        #                                  'objects': []})
        #
        # Run your method by
        # ret = self.getImpl().your_method(self.getContext(), parameters...)
        #
        # Check returned data with
        # self.assertEqual(ret[...], ...) or other unittest methods
        result = self.serviceImpl.run_centrifuge(self.ctx, {'workspace_name': self.wsName,
                                                       'input_refs': ['22852/10/1'],
                                                       'db_type': 'p_compressed+h+v'
                                                       })
        report_params = result[0]
        logging.info(report_params)
        logging.info(result)
        #self.assertEqual(report_params['html_links'][0]['name'],
        #                  'centrifuge.krona.html')

    def test_centrifuge(self):
        # 'sh lib/gottcha2/src/uge-gottcha2.sh -i test/data/test.fastq -o test/data/output -p testing -d test/data/RefSeq-r90.cg.Viruses.species.fna'
        cmd = ['/kb/module/lib/centrifuge/Utils/uge-centrifuge.sh', '-i', '/data/test.fastq', '-o', '/kb/module/work/output', '-p',
               'testing', '-d', '/data/centrifuge/p_compressed+h+v']
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(p.communicate())
        #self.assertTrue(os.path.exists('/kb/module/work/output/testing.summary.tsv'))
        self.assertTrue(os.path.exists('/kb/module/work/output/testing.krona.html'))
        #with open('/kb/module/test/data/output/testing.summary.tsv', 'r') as fp:
        #    lines = fp.readlines()
        #    self.assertTrue('Zaire ebolavirus' in lines[5])