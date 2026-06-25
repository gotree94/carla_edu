# Step 10: 최종 프로젝트 — Tesla-style 자율주행 통합 시스템

## 프로젝트 목표

Tesla처럼 **8개의 카메라**를 활용하여:
1. RGB 영상 획득 (다중 시점)
2. Semantic Segmentation (객체 인식)
3. Depth Map (거리 정보)
4. Visual SLAM 기반 위치 추정
5. 통합 자율주행

## 시스템 아키텍처

```
                     ┌──────────────────────┐
                     │    CARLA Simulator    │
                     └──────────┬───────────┘
                                │
         ┌──────────────────────┼──────────────────────┐
         │                      │                      │
    ┌────┴────┐          ┌─────┴─────┐          ┌─────┴────┐
    │ 8x RGB  │          │ 8x Seg    │          │ 8x Depth │
    │Cameras  │          │ Cameras   │          │ Cameras  │
    └────┬────┘          └─────┬─────┘          └─────┬────┘
         │                    │                    │
    ┌────┴────────────────────┴────────────────────┴────┐
    │               Sensor Fusion Hub                    │
    │  - RGB 이미지 저장                                   │
    │  - Segmentation 맵 생성                              │
    │  - Depth to Point Cloud 변환                        │
    └────────────────────┬───────────────────────────────┘
                         │
    ┌────────────────────┴───────────────────────────────┐
    │              Perception Layer                       │
    │  - 차선 검출 (Segmentation 기반)                     │
    │  - 장애물 검출 (Depth + Segmentation)                │
    │  - Feature Extraction (ORB/SIFT)                   │
    └────────────────────┬───────────────────────────────┘
                         │
    ┌────────────────────┴───────────────────────────────┐
    │              Localization & Mapping                 │
    │  - Visual SLAM (ORB-SLAM style)                    │
    │  - GPS 보정                                        │
    │  - Occupancy Grid Map                              │
    └────────────────────┬───────────────────────────────┘
                         │
    ┌────────────────────┴───────────────────────────────┐
    │              Planning & Control                     │
    │  - 경로 계획 (Waypoint 기반)                        │
    │  - PID 제어 (조향, 속도)                             │
    │  - 장애물 회피                                      │
    └────────────────────────────────────────────────────┘
```

## 프로젝트 파일 구조

```
src/10_final_project/
├── main.py                    # 메인 실행 파일
├── config.py                  # 설정 파일
├── sensors.py                 # 센서 관리
├── perception.py              # 인지 (Segmentation, 차선)
├── slam.py                    # Visual SLAM
├── controller.py              # PID 제어
└── utils.py                   # 유틸리티 함수
```

## 실행 방법

```powershell
# 1. CARLA 시뮬레이터 실행 (별도 창)
cd C:\CARLA_0.9.15
.\CarlaUE4.exe

# 2. 다른 터미널에서 프로젝트 실행
cd C:\carla_edu\src\10_final_project
python main.py
```

## 주요 기능별 설명

### 1. 센서 모듈 (sensors.py)
- 8대의 RGB, Segmentation, Depth 카메라를 차량에 부착
- Tesla의 실제 카메라 위치를 참고한 배치
- 각 센서 데이터를 동기화하여 수집

### 2. 인지 모듈 (perception.py)
- Segmentation 맵에서 차선, 도로, 차량, 보행자 영역 추출
- Depth 맵에서 3D 포인트 클라우드 생성
- 장애물까지의 거리 계산

### 3. SLAM 모듈 (slam.py)
- ORB 특징점 추출 및 매칭
- Essential Matrix 계산을 통한 상대姿态 추정
- 3D 맵 포인트 triangulation
- 번들 조정을 통한 최적화

### 4. 제어 모듈 (controller.py)
- 경로 추종을 위한 PID 제어
- 장애물 회피 로직
- 속도 프로파일 관리

## 확장 아이디어

1. **딥러닝 통합**: YOLO 객체 검출 + Segmentation
2. **Lane Keeping**: 차선 유지 보조 시스템
3. **End-to-End Learning**: CNN으로 직접 제어
4. **ROS Integration**: ROS bridge로 실제 로봇에 적용
5. **Multi-Agent**: 여러 차량协同 주행
