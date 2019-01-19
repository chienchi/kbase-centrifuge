# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import subprocess

from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.ReadsUtilsClient import ReadsUtils
#END_HEADER


class centrifuge:
    '''
    Module Name:
    centrifuge

    Module Description:
    A KBase module: centrifuge
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/chienchi/kbase-centrifuge.git"
    GIT_COMMIT_HASH = "4bf8c49dbcc55b21c98d222a6a8d4ec69223b2b2"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.scratch = config['scratch']
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #END_CONSTRUCTOR
        pass


    def run_centrifuge(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_centrifuge
        # Step 2 - Download the input data as a Fasta and
        # We can use the AssemblyUtils module to download a FASTA file from our Assembly data object.
        # The return object gives us the path to the file that was created.
        logging.info('Downloading reads data as a Fastq file.')
        readsUtil = ReadsUtils(self.callback_url)
        download_reads_output = readsUtil.download_reads({'read_libraries': params['input_refs']})
        # print(f"Input parameters {params['input_refs']}, {params['db_type']} download_reads_output {download_reads_output}")
        fastq_files = []
        for key,val in download_reads_output['files'].items():
            if 'fwd' in val['files'] and val['files']['fwd']:
                fastq_files.append(val['files']['fwd'])
            if 'rev' in val['files'] and val['files']['rev']:
                fastq_files.append(val['files']['rev'])
        print(f"fastq files {fastq_files}")
        fastq_files_string = ','.join(fastq_files)
        output_dir = os.path.join(self.scratch, 'centrifuge_out')
        os.makedirs(output_dir)
        cmd = ['/kb/module/lib/centrifuge/Utils/uge-centrifuge.sh', '-i', fastq_files_string, '-o', output_dir, '-p',
               'centrifuge', '-d', '/data/centrifuge/' + params['db_type']]
        logging.info('cmd {cmd}')
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        logging.info('subprocess {p.communicate()}')

        # Step 5 - Build a Report and return
        objects_created = []
        output_files = os.listdir(output_dir)
        output_files_list = []
        for output in output_files:
            output_files_list.append({'path': os.path.join(output_dir, output),
                                      'name': output
                                      })

        output_html_files = {'path': os.path.join(output_dir, 'centrifuge.krona.html'),
                             'name': 'centrifuge.krona.html'}
        report_params = {'message': 'Centrifuge run finished',
                         'workspace_name': params.get('workspace_name'),
                         'objects_created': objects_created,
                         'file_links': output_files_list,
                         'html_links': [output_html_files],
                         'direct_html_link_index': 0,
                         'html_window_height': 333}

        # STEP 6: contruct the output to send back
        kbase_report_client = KBaseReport(self.callback_url)
        report_info = kbase_report_client.create_extended_report(report_params)
        report_info['report_params'] = report_params        
        
        output = {
            'report_name': report_info['name'],
            'report_ref': report_info['ref']
        }
        #END run_centrifuge

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_centrifuge return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
