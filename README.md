# Smart Z-Hop V3.0

![image](https://github.com/user-attachments/assets/1e02e4e5-6eed-4230-9360-62c340d0c604)
![image](https://github.com/user-attachments/assets/6519c21a-836f-4e38-97e5-b93493f5f330)


혁신적인 **연속 곡선 Z-hop** 시스템을 완성한 Cura 포스트 프로세싱 스크립트입니다.

## 🎯 핵심 기능

- **🔥 연속 곡선 Z-hop**: 톱니파 문제 완전 해결
- **🎯 리트랙션 정확 감지**: 올바른 Z-hop 시작점
- **⚡ M203 속도 제어**: 하드웨어 호환성 보장
- **🔧 Two Modes**: Traditional (수직) + Slingshot (곡선)

## 🚀 설치 및 사용

### 설치
1. `SmartZHop.py` 다운로드
2. Cura scripts 폴더에 복사: `%APPDATA%\cura\[버전]\scripts\`
3. Cura 재시작
4. Extensions → Post Processing → Modify G-Code → Add Smart Z-Hop

### 추천 설정

**V3.0 연속 곡선 모드** (권장):
```
Z-Hop Mode: Smart Mode (Slingshot)
Z-Hop Height: 0.3mm
Travel Distance: 1.0mm (낮게 설정)
Z-Hop Speed: 15mm/s
Trajectory Mode: Percentage
Ascent/Descent Ratio: 25%
```

**Traditional 모드** (기존 호환):
```
Z-Hop Mode: Traditional
Z-Hop Height: 0.3mm
Travel Distance: 5.0mm
Z-Hop Speed: 15mm/s
```

## 🧪 테스트

독립 실행으로 Cura 없이 바로 테스트 가능:

```bash
# 기본 테스트
python SmartZHop.py

# 개별 테스트
python tests\test_simple_verification.py
python tests\test_v3_continuous_curve_verification.py
python tests\final_complete_verification.py
```

## 📊 V3.0의 혁신

### 문제 해결
- **기존**: 연속 travel move → 각각 Z-hop → 톱니파 패턴
- **V3.0**: 연속 travel move → 하나의 부드러운 곡선

### 결과
- 프린팅 품질 향상
- 더 빠른 이동 속도
- 하드웨어 친화적 제어

## 🎨 모드 비교

| 기능 | Traditional | Slingshot V3.0 |
|------|-------------|----------------|
| Z-hop 방식 | 수직 이동 | 곡선 궤적 |
| 연속 이동 처리 | 개별 처리 | 통합 곡선 |
| 프린팅 속도 | 빠름 | 최적화됨 |
| 품질 | 좋음 | 최고 |

## ⚙️ 고급 설정

- **Min Z-Hop**: 0.1mm (짧은 이동용)
- **Max Distance**: 100mm (참조 거리)
- **Custom Layers**: 특정 레이어만 적용
- **Layer Change Z-Hop**: 레이어 전환 시 Z-hop

---

**Smart Z-Hop V3.0** - 3D 프린팅의 새로운 차원! 🚀
