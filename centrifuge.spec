/*
A KBase module: centrifuge
*/

module centrifuge {
    typedef structure {
        string report_name;
        string report_ref;
    } ReportResults;

    /*
        This example function accepts any number of parameters and returns results in a KBaseReport
    */
    funcdef run_centrifuge(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;
    funcdef exec_centrifuge(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;

};
