# tg-housing
Housing services' TG bot



# Install and run

## Upload config files
```shell
TARGET_SERVER="remote-server"
TARGET_DIR="/opt/tg-housing"
ssh ${TARGET_SERVER} -C  "mkdir -P ${TARGET_DIR}"
scp etc/* ${TARGET_SERVER}:${TARGET_DIR}
```

## Prepare service
```shell
TARGET_SERVER="remote-server"
TARGET_DIR="/opt/tg-housing"

ssh ${TARGET_SERVER}

# on the remote server
sudo su
cp ${TARGET_DIR}/tg-housing.service /etc/systemd/system/tg-housing.service
systemctl daemon-reload
systemctl start tg-housing.service
```


nano <path_to_project>/resourses/jenkins_job.service

# copy config to sysremd
mkdir ~/.config/systemd/user/
cp <path_to_project>/resourses/jenkins_job.service ~/.config/systemd/user/
cd ~/.config/systemd/user/
chmod 754 . 

# reload config
systemctl --user daemon-reload

# setup new service and enable him
systemctl --user enable jenkins_job.service

# run new service
systemctl --user start jenkins_job.service

# check state
systemctl --user status jenkins_job.service

# need reload
systemctl --user restart jenkins_job.service
