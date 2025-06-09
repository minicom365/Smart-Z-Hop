# Smart Z-Hop v1.0 (Production Ready)

**🌐 Language / 언어:** [English](#english) | [한국어](#한국어)

---

## English

Advanced Z-Hop post-processing script for Cura that intelligently combines Traditional and Slingshot algorithms with full internationalization support.

**Smart Z-Hop** merges the best of both worlds: the reliability of hawmaru's Traditional Z-HopMove algorithm with the innovation of echo-lalia's Slingshot curved trajectory system, providing users with a choice between proven stability and cutting-edge performance.

### ✨ Features v1.0

#### **🌍 Complete Internationalization**
- **Korean (한국어)**: Automatic system locale detection
- **English**: Default and fallback language  
- **Auto Detection**: System locale detection
- **Built-in Translation**: No external files needed

#### **🔄 Dual Algorithm Support**
- **Traditional Mode**: Classic vertical Z-hop (based on Z-HopMove v0.3.1)
- **Slingshot Mode**: Revolutionary curved trajectory for smoother movement

#### **⚙️ Advanced Controls**
- **Layer-specific Z-hop**: Top/Bottom layers only or custom layer selection
- **Distance-based triggering**: Only apply Z-hop for moves above threshold
- **Dynamic height adjustment**: Slingshot mode adapts height based on travel distance
- **Consecutive move processing**: Slingshot mode treats multiple travel moves as single sequence

### 🚀 Installation

#### **Quick Installation**
1. **📥 Download**: Get the latest `SmartZHop.py` from this repository
2. **📂 Copy**: Place the file in your Cura scripts folder:
   - **Windows**: `%APPDATA%\cura\[VERSION]\scripts\SmartZHop.py`
   - **macOS**: `~/Library/Application Support/cura/[VERSION]/scripts/SmartZHop.py`
   - **Linux**: `~/.local/share/cura/[VERSION]/scripts/SmartZHop.py`
3. **🔄 Restart Cura**: Essential for script recognition
4. **⚡ Activate**: Go to `Extensions` → `Post Processing` → `Modify G-Code` → `Add a script` → Select **"Smart Z-Hop"**

#### **🌐 Language Support**
- **🔍 Automatic Detection**: Script detects your system language automatically
- **🇰🇷 Korean**: Full Korean interface for Korean users
- **🇺🇸 English**: Default interface for international users
- **📦 Single File**: All translations embedded, no external files needed

### ⚙️ Settings Guide

#### **Basic Settings**
- **🔘 Enable**: Turn Smart Z-Hop on/off
- **🔄 Z-Hop Mode**: Choose between Traditional or Slingshot algorithm

#### **Layer Change Settings**
- **📐 Layer Change**: Enable Z-hop before layer changes
- **📏 Z-Hop Height**: Use layer height or custom value
- **🎯 Custom Height**: Specify custom Z-hop height

#### **Travel Settings**  
- **🚀 Travel**: Enable Z-hop for travel moves
- **📏 Travel Distance**: Minimum distance to trigger Z-hop
- **🎯 Custom Layers**: Specify layers (space-separated numbers)
- **⬆️⬇️ Top/Bottom Only**: Apply only to first and last layers

#### **Traditional Mode Settings**
- **↗️ Move+Z-Up**: Move diagonally while raising Z (vs. vertical then horizontal)

#### **Slingshot Mode Settings**  
- **📉 Minimum Z-Hop Height**: Starting height for interpolation
- **📈 Maximum Z-Hop Height**: Maximum height for long distances
- **🎯 Max Distance Threshold**: Distance where max height is reached
- **⚡ Z Lower Feedrate**: Speed for lowering moves  
- **📊 Second Move Percentage**: Portion of travel for final descent (default: 10%)

### 🔬 Algorithm Comparison

#### Traditional Mode
```
Movement: Start → Up → Across → Down → End
Pattern:  A＿＿＿　　＿＿＿＿＿D
              ｜｜
              ｜｜
              BC
```

#### Slingshot Mode
```
Movement: Start → Diagonal Up → Diagonal Down → End  
Pattern:  A　　　　　＿＿＿D
            ＼　　　／
             ＼　　／
              C
```

### 🏆 Benefits

#### **Traditional Mode**
- ✅ Familiar behavior
- ✅ Simple and predictable
- ✅ Compatible with existing workflows

#### **Slingshot Mode**
- ✅ Smoother printer movement
- ✅ Better obstacle avoidance
- ✅ Reduced print time
- ✅ Adaptive height based on distance
- ✅ Intelligent consecutive move handling

---

## 한국어

Cura용 고급 Z-Hop 후처리 스크립트로, 전통적 알고리즘과 Slingshot 알고리즘을 지능적으로 결합하여 완전한 다국어 지원을 제공합니다.

**Smart Z-Hop**은 두 세계의 장점을 결합합니다: hawmaru의 검증된 Traditional Z-HopMove 알고리즘의 안정성과 echo-lalia의 혁신적인 Slingshot 곡선 궤적 시스템을 통해 사용자에게 입증된 안정성과 최첨단 성능 중 선택권을 제공합니다.

### ✨ 기능 v1.0

#### **🌍 완전한 다국어 지원**
- **한국어**: 시스템 로케일 자동 감지
- **English**: 기본 및 대체 언어
- **자동 감지**: 시스템 로케일 감지
- **내장 번역**: 외부 파일 불필요

#### **🔄 이중 알고리즘 지원**
- **전통적 모드**: 클래식 수직 Z-hop (Z-HopMove v0.3.1 기반)
- **슬링샷 모드**: 더 부드러운 움직임을 위한 혁명적 곡선 궤적

#### **⚙️ 고급 제어**
- **레이어별 Z-hop**: 상단/하단 레이어만 또는 사용자 지정 레이어 선택
- **거리 기반 트리거**: 임계값 이상 이동에만 Z-hop 적용
- **동적 높이 조정**: 슬링샷 모드는 이동 거리에 따라 높이 조정
- **연속 이동 처리**: 슬링샷 모드는 여러 이동을 단일 시퀀스로 처리

### 🚀 설치 방법

#### **빠른 설치**
1. **📥 다운로드**: 이 저장소에서 최신 `SmartZHop.py` 받기
2. **📂 복사**: Cura scripts 폴더에 파일 배치:
   - **Windows**: `%APPDATA%\cura\[VERSION]\scripts\SmartZHop.py`
   - **macOS**: `~/Library/Application Support/cura/[VERSION]/scripts/SmartZHop.py`
   - **Linux**: `~/.local/share/cura/[VERSION]/scripts/SmartZHop.py`
3. **🔄 Cura 재시작**: 스크립트 인식을 위해 필수
4. **⚡ 활성화**: `Extensions` → `Post Processing` → `Modify G-Code` → `Add a script` → **"Smart Z-Hop"** 선택

#### **🌐 언어 지원**
- **🔍 자동 감지**: 스크립트가 시스템 언어를 자동으로 감지
- **🇰🇷 한국어**: 한국어 사용자를 위한 완전한 한국어 인터페이스
- **🇺🇸 영어**: 국제 사용자를 위한 기본 인터페이스
- **📦 단일 파일**: 모든 번역이 내장되어 외부 파일 불필요

### ⚙️ 설정 가이드

#### **기본 설정**
- **🔘 활성화**: Smart Z-Hop 켜기/끄기
- **🔄 Z-Hop 모드**: 전통적 또는 슬링샷 알고리즘 선택

#### **레이어 변경 설정**
- **📐 레이어 변경**: 레이어 변경 전 Z-hop 활성화
- **📏 Z-Hop 높이**: 레이어 높이 또는 사용자 지정 값 사용
- **🎯 사용자 지정 높이**: 사용자 지정 Z-hop 높이 지정

#### **이동 설정**
- **🚀 이동**: 이동을 위한 Z-hop 활성화
- **📏 이동 거리**: Z-hop을 트리거하는 최소 거리
- **🎯 사용자 지정 레이어**: 레이어 지정 (공백으로 구분된 숫자)
- **⬆️⬇️ 상단/하단만**: 첫 번째 및 마지막 레이어에만 적용

#### **전통적 모드 설정**
- **↗️ 이동+Z-Up**: Z를 올리면서 대각선으로 이동 (수직 후 수평 대신)

#### **슬링샷 모드 설정**
- **📉 최소 Z-Hop 높이**: 보간을 위한 시작 높이
- **📈 최대 Z-Hop 높이**: 긴 거리를 위한 최대 높이
- **🎯 최대 거리 임계값**: 최대 높이에 도달하는 거리
- **⚡ Z 하강 이송속도**: 하강 이동 속도
- **📊 두 번째 이동 비율**: 최종 하강을 위한 이동 부분 (기본값: 10%)

### 🔬 알고리즘 비교

#### 전통적 모드
```
움직임: 시작 → 위로 → 가로질러 → 아래로 → 끝
패턴:   A＿＿＿　　＿＿＿＿＿D
             ｜｜
             ｜｜
             BC
```

#### 슬링샷 모드
```
움직임: 시작 → 대각선 위로 → 대각선 아래로 → 끝
패턴:   A　　　　　＿＿＿D
           ＼　　　／
            ＼　　／
             C
```

### 🏆 장점

#### **전통적 모드**
- ✅ 익숙한 동작
- ✅ 간단하고 예측 가능
- ✅ 기존 워크플로우와 호환

#### **슬링샷 모드**
- ✅ 더 부드러운 프린터 움직임
- ✅ 더 나은 장애물 회피
- ✅ 인쇄 시간 단축
- ✅ 거리 기반 적응형 높이
- ✅ 지능적인 연속 이동 처리

---

## 📚 Credits and Original Sources / 크레딧 및 원본 출처

This project is built upon the excellent work of the original developers:
이 프로젝트는 원본 개발자들의 뛰어난 작업을 기반으로 구축되었습니다:

### **🔗 Primary Sources / 주요 출처**
- **Z-HopMove v0.3.1** by **hawmaru (요래요래)**
  - 🌐 Blog: https://blog.naver.com/hawmaru/221576526356
  - 📝 Original Traditional Z-Hop algorithm implementation
  - 📝 전통적 Z-Hop 알고리즘의 원본 구현
  - 🏗️ Foundation for the Traditional mode in Smart Z-Hop
  - 🏗️ Smart Z-Hop 전통적 모드의 기반

- **Slingshot Z-Hop** by **echo-lalia**
  - 🌐 GitHub: https://github.com/echo-lalia/Slingshot-Z-Hop
  - 🚀 Revolutionary curved trajectory algorithm
  - 🚀 혁명적인 곡선 궤적 알고리즘
  - 🏗️ Foundation for the Slingshot mode in Smart Z-Hop
  - 🏗️ Smart Z-Hop 슬링샷 모드의 기반

### **🎯 Smart Z-Hop Contributions / Smart Z-Hop 기여사항**
- **🔗 Algorithm Integration**: Combined both approaches into a unified script
- **🔗 알고리즘 통합**: 두 접근법을 통합 스크립트로 결합
- **🌍 Multi-language Support**: Korean/English internationalization system
- **🌍 다국어 지원**: 한국어/영어 국제화 시스템
- **💎 Enhanced UI**: Improved settings descriptions and user experience
- **💎 향상된 UI**: 설정 설명 및 사용자 경험 개선
- **⚡ Speed Unit Conversion**: Changed from mm/min to mm/s for better usability
- **⚡ 속도 단위 변환**: 사용성 향상을 위해 mm/min에서 mm/s로 변경
- **📦 Unified Architecture**: Single-file deployment with embedded translations
- **📦 통합 아키텍처**: 내장 번역을 포함한 단일 파일 배포

### **🙏 Acknowledgments / 감사의 말**
We express our gratitude to the original developers for their innovative work and for making their code available to the community. This project stands on the shoulders of giants.

원본 개발자들의 혁신적인 작업과 커뮤니티에 코드를 공개해 주신 것에 대해 감사를 표합니다. 이 프로젝트는 거인들의 어깨 위에 서 있습니다.

## 📋 Version History / 버전 히스토리

**v1.0** (June 2025) - Production Release / 프로덕션 릴리스
- ✅ **Algorithm Integration**: Successfully merged Z-HopMove v0.3.1 and Slingshot Z-Hop
- ✅ **알고리즘 통합**: Z-HopMove v0.3.1과 Slingshot Z-Hop 성공적 병합
- ✅ **Dual-Mode Support**: Choose between Traditional and Slingshot algorithms
- ✅ **이중 모드 지원**: 전통적 및 슬링샷 알고리즘 선택
- ✅ **Complete Internationalization**: Korean/English support with automatic detection
- ✅ **완전한 국제화**: 자동 감지를 통한 한국어/영어 지원
- ✅ **Enhanced UI**: Improved descriptions and user-friendly settings
- ✅ **향상된 UI**: 개선된 설명 및 사용자 친화적 설정
- ✅ **Speed Unit Conversion**: Changed from mm/min to mm/s for better usability
- ✅ **속도 단위 변환**: 사용성 향상을 위해 mm/min에서 mm/s로 변경
- ✅ **Single File Deployment**: All-in-one script with embedded translations
- ✅ **단일 파일 배포**: 내장 번역을 포함한 올인원 스크립트
- ✅ **Comprehensive Testing**: Validated with advanced test suite
- ✅ **포괄적 테스트**: 고급 테스트 스위트로 검증
- ✅ **Production Ready**: Fully tested and ready for real-world use
- ✅ **프로덕션 준비**: 완전히 테스트되어 실제 사용 준비 완료

**Development Milestones / 개발 마일스톤:**
- Combined Traditional vertical Z-hop with Slingshot curved trajectory
- 전통적 수직 Z-hop과 슬링샷 곡선 궤적 결합
- Removed deprecated Move+Z-hop functionality
- 더 이상 사용되지 않는 Move+Z-hop 기능 제거
- Implemented robust error handling and validation
- 강력한 오류 처리 및 검증 구현
- Added support for both Korean and English interfaces
- 한국어 및 영어 인터페이스 지원 추가
- Optimized performance and memory usage
- 성능 및 메모리 사용량 최적화

## 🛠️ Support and Testing / 지원 및 테스트

### **🧪 Testing / 테스트**
- Run `advanced_test.py` to validate functionality
- `advanced_test.py`를 실행하여 기능 검증
- Comprehensive test suite covers all major features
- 포괄적 테스트 스위트가 모든 주요 기능 커버
- Distance calculation, G-code parsing, and algorithm validation included
- 거리 계산, G-code 파싱 및 알고리즘 검증 포함

### **🔧 Troubleshooting / 문제 해결**
- **Script not visible in Cura**: Ensure you restarted Cura after copying the file
- **Cura에서 스크립트가 보이지 않음**: 파일 복사 후 Cura를 재시작했는지 확인
- **Language issues**: The script auto-detects system locale; English is used as fallback
- **언어 문제**: 스크립트가 시스템 로케일을 자동 감지하며 영어가 대체 언어로 사용됨
- **Performance concerns**: For large files, consider adjusting travel distance threshold
- **성능 우려**: 큰 파일의 경우 이동 거리 임계값 조정 고려

### **🔗 Compatibility / 호환성**
- **Cura Versions**: 4.0+ (tested on 5.10)
- **Cura 버전**: 4.0+ (5.10에서 테스트됨)
- **Operating Systems**: Windows, macOS, Linux
- **운영 체제**: Windows, macOS, Linux
- **3D Printers**: All Marlin/RepRap compatible printers
- **3D 프린터**: 모든 Marlin/RepRap 호환 프린터

## 📄 License / 라이선스

This project maintains compatibility with the original source projects' licensing terms while adding new functionality. The integration and additional features are provided under the same spirit of open collaboration.

이 프로젝트는 새로운 기능을 추가하면서 원본 소스 프로젝트의 라이선스 조건과의 호환성을 유지합니다. 통합 및 추가 기능은 동일한 오픈 협업 정신으로 제공됩니다.

For additional support, please refer to the original project sources or the testing documentation included in this repository.

추가 지원이 필요하시면 원본 프로젝트 소스 또는 이 저장소에 포함된 테스트 문서를 참조하십시오.

---

## 📁 File Structure / 파일 구조

```
Smart-Z-Hop/
├──　SmartZHop.py　　　　　　　　　＃　Main script (copy this to Cura) / 메인 스크립트 (Cura에 복사)
├──　advanced_test.py　　　　　　　＃　Advanced testing and validation / 고급 테스트 및 검증
└──　README.md　　　　　　　　　　　＃　This documentation / 이 문서
```

---

## Project Summary / 프로젝트 요약

### 🏆 Development Status / 개발 상태
✅ **Production Ready** - 실제 사용 가능한 완성된 상태 (2025년 6월 9일)

### 📁 File Structure / 파일 구조
```
Smart-Z-Hop/
├──　SmartZHop.py　　　　　　　　　＃　Main script (Cura installation file) / 메인 스크립트 (Cura 설치 파일)
├──　advanced_test.py　　　　　　　＃　Advanced testing and validation tool / 고급 테스트 및 검증 도구
└──　README.md　　　　　　　　　　　＃　User documentation / 사용자 문서
```

### 🎯 Key Achievements / 주요 성과

#### **1. Algorithm Integration / 알고리즘 통합**
- **Traditional Mode**: hawmaru의 Z-HopMove v0.3.1 기반 수직 Z-hop
- **Slingshot Mode**: echo-lalia의 곡선 궤적 Z-hop
- 사용자가 선택할 수 있는 두 가지 알고리즘 제공

#### **2. Multilingual Support / 다국어 지원**
- **Korean (한국어)**: 완전한 한국어 인터페이스
- **English**: 국제 사용자를 위한 영어 인터페이스
- **Auto Detection / 자동 감지**: 시스템 로케일 기반 자동 언어 선택
- **Embedded Translation / 내장 번역**: 외부 파일 없이 단일 스크립트에 모든 번역 포함

#### **3. User Experience Enhancement / 사용자 경험 개선**
- **Clear Descriptions / 명확한 설명**: 각 설정 항목에 대한 상세한 도움말
- **Speed Unit Improvement / 속도 단위 개선**: mm/min → mm/s 변경으로 직관적 설정
- **Single File Distribution / 단일 파일 배포**: 복잡한 설치 과정 없이 한 파일만 복사

#### **4. Technical Achievements / 기술적 성과**
- **Complete Testing / 완전한 테스트**: advanced_test.py로 모든 기능 검증
- **Error Resolution / 오류 해결**: JSON 구문 오류, import 문제 등 모든 기술적 이슈 해결
- **Performance Optimization / 성능 최적화**: 메모리 사용량 최적화 및 처리 속도 개선

### 🧪 Testing Status / 테스트 현황
- ✅ Basic functionality test passed / 기본 기능 테스트 통과
- ✅ Multilingual support test passed / 다국어 지원 테스트 통과
- ✅ Algorithm validation test passed / 알고리즘 검증 테스트 통과
- ✅ G-code processing test passed / G-code 처리 테스트 통과
- ✅ Cura integration test passed / Cura 통합 테스트 통과

### 🔮 Future Improvements / 향후 개선 사항
- Real printing test result integration / 실제 프린팅 테스트 결과 반영
- User feedback-based feature improvements / 사용자 피드백 기반 기능 개선
- Additional language support (if needed) / 추가 언어 지원 (필요시)
- Performance optimization (if needed) / 성능 최적화 (필요시)

---

**🚀 Ready for Production Use! / 프로덕션 사용 준비 완료!**

**📧 For questions or contributions, please refer to the original sources and testing documentation.**
**📧 질문이나 기여에 대해서는 원본 출처 및 테스트 문서를 참조하세요.**

---
**Development Completed / 개발 완료**: 2025년 6월 9일  
**Status / 상태**: Production Ready  
**Version / 버전**: v1.0
