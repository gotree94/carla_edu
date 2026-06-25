# CARLA Self-Driving Simulation 교육 자료

이 저장소는 [Carla Basics YouTube Playlist](https://www.youtube.com/playlist?list=PL3lTgNaX8q9o451vRwjeKrRDI76yb8WLT)와
[Self-driving with a simulator](https://www.youtube.com/playlist?list=PL3lTgNaX8q9p_FJWUJHPrYYC5KE5_FaQo)를 기반으로
CARLA 시뮬레이터를 활용한 자율주행 교육을 위해 만들어졌습니다.

## 목차

| 단계 | 주제 | 설명 |
|------|------|------|
| **00** | 개요 및 소개 | 자율주행과 CARLA 소개 |
| **01** | CARLA 설치 | 시뮬레이터 다운로드 및 설치 |
| **02** | Python 환경 구성 | Python API 클라이언트 설정 |
| **03** | Positioning on Map | 맵에서 차량 위치 지정 |
| **04** | Driving Straight | 직진 주행 구현 |
| **05** | Navigation Basics | 경로 탐색 기초 |
| **06** | Route Following | 경로 추종 구현 |
| **07** | Map Capture | 주행 중 맵 캡처 |
| **08** | Follow a Car | 앞차 추종 주행 |
| **09** | Camera Sensors | 카메라, Segmentation, Depth 센서 |
| **10** | **최종 프로젝트** | Tesla-style Camera + Segmentation + Depth + SLAM |

## 참고 영상

- [Self-driving cars need your help](https://youtu.be/jIK9sanumuU)
- [Step 1 - download Carla](https://youtu.be/jIK9sanumuU)
- [Step 2 - Python configuration](https://youtu.be/jIK9sanumuU)
- [Positioning on the map](https://youtu.be/jIK9sanumuU)
- [Tutorial 4 Driving Straight](https://youtu.be/jIK9sanumuU)
- [Navigation - The Fun Part](https://youtu.be/jIK9sanumuU)
- [Final touches to route following](https://youtu.be/jIK9sanumuU)
- [How to capture the Map as you drive](https://youtu.be/jIK9sanumuU)
- [How to follow a car in Carla Simulator](https://youtu.be/jIK9sanumuU)

## 사전 요구사항

- Windows 10/11 (또는 Ubuntu 20.04/22.04)
- NVIDIA GPU (RTX 2070 이상 권장, 8GB VRAM)
- 20GB 이상의 디스크 공간
- Python 3.7 ~ 3.12

## 프로젝트 구조

```
carla_edu/
├── README.md              # 이 파일
├── docs/                  # 문서 디렉토리
│   ├── 00_introduction.md
│   ├── 01_installation.md
│   ├── 02_python_setup.md
│   ├── 03_positioning.md
│   ├── 04_driving_straight.md
│   ├── 05_navigation.md
│   ├── 06_route_following.md
│   ├── 07_map_capture.md
│   ├── 08_follow_car.md
│   ├── 09_camera_sensors.md
│   └── 10_final_project.md
└── src/                   # 소스 코드
    ├── 01_hello_carla/
    ├── 02_python_config/
    ├── 03_positioning/
    ├── 04_driving_straight/
    ├── 05_navigation/
    ├── 06_route_following/
    ├── 07_map_capture/
    ├── 08_follow_car/
    ├── 09_camera_sensors/
    └── 10_final_project/
```
