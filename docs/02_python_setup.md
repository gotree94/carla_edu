# Step 02: Python 환경 구성

> 참고 영상: [Self-driving with a sim: Step 2 - Python configuration](https://youtu.be/jIK9sanumuU)

## 1. Python 설치

CARLA는 Python 3.7 ~ 3.12를 지원합니다.

```powershell
# Python 설치 확인
python --version
```

## 2. 가상 환경 생성

```powershell
# CARLA 디렉토리로 이동
cd C:\CARLA_0.9.15

# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
.\venv\Scripts\activate
```

## 3. CARLA Python API 설치

```powershell
# pip 업그레이드
python -m pip install --upgrade pip

# carla 패키지 설치
pip install carla

# 또는 직접 wheel 파일 설치
pip install .\WindowsNoEditor\PythonAPI\carla\dist\carla-0.9.15-cp3xx-cp3xx-win_amd64.whl
```

## 4. 필요 패키지 설치

```powershell
# 기본 패키지
pip install numpy opencv-python pygame matplotlib

# requirements.txt로 설치
pip install -r .\WindowsNoEditor\PythonAPI\examples\requirements.txt
```

## 5. 연결 테스트

`src/01_hello_carla/hello_carla.py`를 실행하여 CARLA 연결을 확인합니다.

```python
import carla
import random

def main():
    # CARLA 서버에 연결 (시뮬레이터가 실행 중이어야 함)
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)

    # World 객체 가져오기
    world = client.get_world()

    # 블루프린트 라이브러리
    blueprint_library = world.get_blueprint_library()

    # 차량 스폰
    vehicle_bp = blueprint_library.filter('model3')[0]
    spawn_points = world.get_map().get_spawn_points()
    spawn_point = spawn_points[0]

    vehicle = world.spawn_actor(vehicle_bp, spawn_point)
    print(f"차량 스폰 성공: {vehicle.type_id}")

    # Spectator(관찰자) 위치를 차량으로 이동
    spectator = world.get_spectator()
    transform = carla.Transform(vehicle.get_transform().location +
                                carla.Location(z=50),
                                carla.Rotation(pitch=-90))
    spectator.set_transform(transform)

    # 5초 후 정리
    import time
    time.sleep(5)

    vehicle.destroy()
    print("차량 제거 완료")

if __name__ == '__main__':
    main()
```

## 6. 실행 순서

1. `CarlaUE4.exe` 실행 (시뮬레이터 먼저 실행)
2. Python 스크립트 실행
3. 시뮬레이터에서 차량이 스폰되는지 확인
