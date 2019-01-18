#!/bin/bash

. /kb/deployment/user-env.sh

python ./scripts/prepare_deploy_cfg.py ./deploy.cfg ./work/config.properties

if [ -f ./work/token ] ; then
  export KB_AUTH_TOKEN=$(<./work/token)
fi

if [ $# -eq 0 ] ; then
  sh ./scripts/start_server.sh
elif [ "${1}" = "test" ] ; then
  echo "Run Tests"
  make test
elif [ "${1}" = "async" ] ; then
  sh ./scripts/run_async.sh
elif [ "${1}" = "init" ] ; then
  echo "Initialize module"
  
  mkdir -p /data/centrifuge
  cd /data/centrifuge
 
  echo "downloading: ftp://ftp.ccb.jhu.edu/pub/infphilo/centrifuge/data/p_compressed+h+v.tar.gz"
  wget -q ftp://ftp.ccb.jhu.edu/pub/infphilo/centrifuge/data/p_compressed+h+v.tar.gz
  tar -xvzf p_compressed+h+v.tar.gz
  rm p_compressed+h+v.tar.gz

  cd /data/centrifuge

  if [ -s "/data/centrifuge/p_compressed+h+v.1.cf" ] ; then
    echo "DATA DOWNLOADED SUCCESSFULLY"
    touch /data/__READY__
  else
    echo "Init failed"
  fi  
  
elif [ "${1}" = "bash" ] ; then
  bash
elif [ "${1}" = "report" ] ; then
  export KB_SDK_COMPILE_REPORT_FILE=./work/compile_report.json
  make compile
else
  echo Unknown
fi
