# Step 01: CARLA 설치

> 참고 영상: [Self-driving with a Sim. Step 1 - download Carla](https://youtu.be/jIK9sanumuU)

## 1. CARLA 다운로드

CARLA 공식 GitHub Releases 페이지에서 최신 버전을 다운로드합니다.

```
https://github.com/carla-simulator/carla/releases
```

**추천 버전**: CARLA 0.9.15 (안정화)
**최신 버전**: CARLA 0.9.16

Windows의 경우 `CARLA_0.9.xx.zip` 파일을 다운로드합니다.

## 2. 압축 해제

```
다운로드한 zip 파일을 원하는 위치에 압축 해제
예: C:\CARLA_0.9.15\
```

압축 해제 후 디렉토리 구조:
```
CARLA_0.9.15/
├── CarlaUE4.exe          # 시뮬레이터 실행 파일
├── PythonAPI/            # Python API
├── Content/              # 맵, 에셋
└── ...
```

## 3. 추가 맵 다운로드 (선택사항)

추가 맵(Town06, Town07)을 사용하려면 AdditionalMaps 패키지를 다운로드하여
`CARLA_0.9.15/` 디렉토리에 압축 해제합니다.

## 4. CARLA 실행

```powershell
# Windows
cd C:\CARLA_0.9.15
.\CarlaUE4.exe
```

처음 실행 시 Unreal Engine이 셰이더를 컴파일하므로 시간이 소요될 수 있습니다.

## 5. 실행 확인

- 시뮬레이터 창이 뜨면 성공
- 기본 맵(Town01)이 로드됨
- 키보드 조작:
  - `W` - 전진 `S` - 후진 `A/D` - 좌/우회전
  - `마우스` - 시점 전환
  - `Esc` - 종료

## 문제 해결

| 문제 | 해결 방법 |
|------|-----------|
| 실행 즉시 꺼짐 | GPU 드라이버 업데이트 |
| 낮은 FPS | 그래픽 설정 낮춤 (`CarlaUE4.exe -quality=Low`) |
| 포트 충돌 | `CarlaUE4.exe -carla-rpc-port=3000` |
| DLL 오류 | Visual C++ Redistributable 설치 |
