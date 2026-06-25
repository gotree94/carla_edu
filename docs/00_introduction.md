# Step 00: 자율주행과 CARLA 소개

## 자율주행차의 핵심 요소

자율주행 시스템은 크게 4가지 핵심 요소로 구성됩니다.

### 1. Localization (위치 인식)
- 차량의 정확한 위치를 센티미터 단위로 파악
- GPS, IMU, LiDAR, 카메라 데이터 융합
- HD Map과의 정합을 통해 정밀 측위

### 2. Perception (인지)
- 주변 객체 감지 및 추적
- 객체의 위치, 속도, 궤적 측정
- 차선, 신호등, 표지판 인식

### 3. Prediction (예측)
- 다른 도로 사용자의 움직임 예측
- 보행자, 자전거, 차량의 행동 패턴 분석
- 가장 어려운 과제 중 하나

### 4. Planning (판단/계획)
- 수집된 데이터 기반 의사 결정
- 경로 생성 및 충돌 회피
- 밀리초 단위의 빠른 판단

## CARLA 시뮬레이터란?

CARLA(CAR Learning to Act)는 자율주행 연구를 위한 **오픈소스 시뮬레이터**입니다.

### 주요 특징
- **Unreal Engine 4 기반**의 고품질 렌더링
- **도시 환경**: 거리, 건물, 차량, 보행자
- **다양한 센서**: 카메라, LiDAR, RADAR, GPS, IMU
- **날씨 제어**: 비, 안개, 시간대 변경
- **Traffic Manager**: NPC 차량/보행자 트래픽 제어
- **Python API**: 모든 기능을 Python으로 제어
- **ROS 통합**: ROS bridge 지원
- **OpenDRIVE**: 표준 맵 포맷 지원

### 시스템 요구사항
- **OS**: Windows 10/11 또는 Ubuntu 20.04/22.04
- **GPU**: NVIDIA RTX 2070 이상 (8GB VRAM 권장)
- **RAM**: 16GB 이상 (32GB 권장)
- **디스크**: 20GB 여유 공간
- **Python**: 3.7 ~ 3.12

## 교육 로드맵

```
01. CARLA 설치                     → 시뮬레이터 실행 환경 구축
02. Python 환경 구성               → API 클라이언트 설정
03. 맵에서 차량 위치 지정           → Transform, Waypoint 이해
04. 직진 주행                      → VehicleControl 기초
05. 경로 탐색 기초                 → Waypoint 기반 경로 생성
06. 경로 추종                      → PID 제어, 경로 추종 알고리즘
07. 맵 캡처                        → 주행 중 데이터 수집
08. 앞차 추종                      → 차량 간 거리 유지
09. 카메라 센서                    → RGB, Segmentation, Depth
10. 최종 프로젝트                  → 통합 자율주행 시스템
```
