# Disaster-response-Xycar
Disaster response Xycar is disaster response robot that made out of Xycar.

## 창업연계공학설계입문 AD Project

### Team Infos

* 팀명: 5조
* 팀 멤버

| 이름   | 학번     |
|--------|----------|
| 윤상건 | 20191632 |
| 이민재 | 20191638 |
| 이연주 | 20191644 |
| 김인규 | 20150752 |

### About This Project

* 목표: 도로를 인식할 수 없는 상황에서 Xycar가 장애물(Stop sign)을 인식하고 사용자가 설정한 목적지까지 장애물을 피해 이동할 수 있는 경로를 계산하여 자율주행하도록 한다.

### 실행 방법

#### ROS 환경변수 설정
* Remote 부분

Remote부분(Xycar에 접속하는 컴퓨터)의 터미널에서 다음과 같이 환경변수를 설정한다.
```
export ROS_IP={Remote의 IP}
export ROS_MASTER_URI=http://10.42.0.1:11311/
```

Remote에서 Xycar로 토픽 메시지를 전송하기 위해 다음과 같이 방화벽을 비활성화 해준다.
```
sudo ufw disable
```

만약 Remote에서 package를 찾을 수 없다는 에러가 발생할 경우 다음의 코드를 Workspace 디렉토리에서 다음의 명령어를 입력해준다.
```
source devel setup.bash
```

* Xycar 부분

Xycar 터미널에서 다음과 같이 환경변수를 설정한다.
```
export ROS_HOSTNAME=10.42.0.1
```

#### ROS 노드 실행 방법

* Remote 부분

Remote부분에서 다음과 같이 사물 인식을 위한 노드를 실행한다.
```
rosrun xycar_ad_remote xycar_ad_remote.py
```

* Xycar 부분

Xycar부분에서 다음과 같이 패키지를 실행한다.
```
roslaunch xycar_ad xycar_ad.launch
```
