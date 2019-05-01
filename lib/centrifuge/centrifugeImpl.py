# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
import subprocess
import shutil

from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.ReadsUtilsClient import ReadsUtils
from installed_clients.DataFileUtilClient import DataFileUtil
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
    def _generate_DataTable(self, infile, outfile):
        f =  open(infile, "r")
        wf = open(outfile,"w")

        header = f.readline().strip()
        headerlist = [ x.strip() for x in header.split('\t')]

        wf.write("<head>\n")
        wf.write("<link rel='stylesheet' type='text/css' href='https://cdn.datatables.net/1.10.19/css/jquery.dataTables.css'>\n")
        wf.write("<script type='text/javascript' charset='utf8' src='https://code.jquery.com/jquery-3.3.1.js'></script>\n")
        wf.write("<script type='text/javascript' charset='utf8' src='https://cdn.datatables.net/1.10.19/js/jquery.dataTables.min.js'></script>\n")
        wf.write("</head>\n")
        wf.write("<body>\n")
        wf.write("""<script>
        $(document).ready(function() {
            $('#centrifuge_result_table').DataTable();
        } );
        </script>""")
        wf.write("<table id='centrifuge_result_table' class='display' style=''>\n")
        wf.write('<thead><tr>' + ''.join("<th>{0}</th>".format(t) for t in headerlist) + '</tr></thead>\n')
        wf.write("<tbody>\n")
        for line in f:
            if not line.strip():continue
            wf.write("<tr>\n")
            temp = [ x.strip() for x in line.split('\t')]
            wf.write(''.join("<td>{0}</td>".format(t) for t in temp))
            wf.write("</tr>\n")
        wf.write("</tbody>\n")
        wf.write("</table>")
        wf.write("</body>\n")
    def package_folder(self, folder_path, zip_file_name, zip_file_description):
        ''' Simple utility for packaging a folder and saving to shock '''
        if folder_path == self.scratch:
            raise ValueError ("cannot package scatch itself.  folder path: "+folder_path)
        elif not folder_path.startswith(self.scratch):
            raise ValueError ("cannot package folder that is not a subfolder of scratch.  folder path: "+folder_path)
        dfu = DataFileUtil(self.callback_url)
        if not os.path.exists(folder_path):
            raise ValueError ("cannot package folder that doesn't exist: "+folder_path)
        output = dfu.file_to_shock({'file_path': folder_path,
                                    'make_handle': 0,
                                    'pack': 'zip'})
        return {'shock_id': output['shock_id'],
                'name': zip_file_name,
                'label': zip_file_description}
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
        #print(f"Input parameters {params['input_refs']}, {params['db_type']} download_reads_output {download_reads_output}")
        fastq_files = []
        fastq_files_name = []
        for key,val in download_reads_output['files'].items():
            if 'fwd' in val['files'] and val['files']['fwd']:
                fastq_files.append(val['files']['fwd'])
                fastq_files_name.append(val['files']['fwd_name'])
            if 'rev' in val['files'] and val['files']['rev']:
                fastq_files.append(val['files']['rev'])
                fastq_files_name.append(val['files']['rev_name'])
        #logging.info(f"fastq files {fastq_files}")
        fastq_files_string = ','.join(fastq_files)
        output_dir = os.path.join(self.scratch, 'centrifuge_out')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        outprefix = "centrifuge"
        # Checking db 
        cmd0 = ["ls", "-al", '/data/centrifuge/']
        #logging.info(f'cmd {cmd0}')
        pls = subprocess.Popen(cmd0, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        logging.info(f'subprocess {pls.communicate()}')

        cmd = ['/kb/module/lib/centrifuge/Utils/uge-centrifuge.sh', '-i', fastq_files_string, '-o', output_dir, '-p',
               'centrifuge', '-d', '/data/centrifuge/' + params['db_type']]
        logging.info(f'cmd {cmd}')
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        logging.info(f'subprocess {p.communicate()}')
        summary_file = os.path.join(output_dir, outprefix + '.report.txt')

        # generate report directory and html file
        report_dir = os.path.join(output_dir, 'html_report')
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
        summary_file_dt = os.path.join(report_dir, 'centrifuge.datatable.html')

        self._generate_DataTable(summary_file,summary_file_dt)
        shutil.copy2('/kb/module/lib/centrifuge/Utils/index.html',os.path.join(report_dir,'index.html'))
        shutil.copy2(os.path.join(output_dir,outprefix+'.krona.html'),os.path.join(report_dir,'centrifuge.krona.html'))
        shutil.move(os.path.join(output_dir,outprefix+'.tree.svg'),os.path.join(report_dir,'centrifuge.tree.svg'))
        html_zipped = self.package_folder(report_dir, 'index.html', 'index.html')


        # Step 5 - Build a Report and return
        objects_created = []
        output_files = os.listdir(output_dir)
        output_files_list = []
        for output in output_files:
            output_files_list.append({'path': os.path.join(output_dir, output),
                                      'name': output
                                      })

        # not used
        output_html_files = [{'path': os.path.join(report_dir, 'index.html'),
                             'name': 'index.html'},
                             {'path': os.path.join(report_dir, 'centrifuge.krona.html'),
                             'name': 'centrifuge.krona.html'},
                             {'path': os.path.join(report_dir, 'centrifuge.datatable.html'),
                             'name': 'centrifuge.datatable.html'},
                             {'path': os.path.join(report_dir, 'centrifuge.tree.svg'),
                             'name': 'centrifuge.tree.svg'}
                            ]
        message = 'Centrifuge run finished on %s against %s.' % (','.join(fastq_files_name) , params['db_type'])
        report_params = {'message': message,
                         'workspace_name': params.get('workspace_name'),
                         'objects_created': objects_created,
                         'file_links': output_files_list,
                         'html_links': [html_zipped],
                         'direct_html_link_index': 0,
                         'html_window_height': 480}

        # STEP 6: contruct the output to send back
        kbase_report_client = KBaseReport(self.callback_url)
        report_info = kbase_report_client.create_extended_report(report_params)
        report_info['report_params'] = report_params        
        logging.info(report_info)

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
