# WebChat

An anonymous chatting room service, based on python3, tornado, websocket

## ScreenShots

1. Working like this
   
   ![Alt text](/doc/main_window.png?raw=true "main_window")

## Install
   
```bash
# this will install 1 command: webchat
$ pip3 install webchat
```

## Run

### Configuration
```yaml
log_level: NOSET                              # NOSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
log_path: /home/pi/Develop/tmp/webchat/logs   # log file directory, can auto generate by webchat
http_host: 0.0.0.0                            # http host
http_port: 9000                               # http port
data_path: /home/pi/Develop/tmp/webchat/data  # data store directory, can auto generate by webchat
```

### Run
```bash
# generate configuration file & scripts
mkdir ./webchat
cd ./webchat
# this will generate configuration.yml and other scripts
webchat -g ./

# run manually
webchat -c ./configuration.yml or nohup webchat -c ./configuration.yml > /dev/null 2>&1 &

# install systemd service, user and group set to use which user and group to run webchat
sudo ./install_systemd_service.sh user group

# start
systemctl start webchat

# stop
systemctl stop webchat

# uninstall systemd service
sudo ./uninstall_systemd_service.sh

# test
# use firefox or chrome open http://localhost:8060
```
