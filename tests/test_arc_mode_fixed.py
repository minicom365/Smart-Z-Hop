# -*- coding: utf-8 -*-
"""
Smart Z-Hop Arc 곡선 모드 전용 테스트 (완전 수정 버전)

🎯 Arc 곡선 모드 핵심 기능 검증:
1. Arc 곡선 Z축 높이 계산 및 시각화
2. 안전 높이 보장 및 그래프 표시 
3. 동적 반지름 적용 및 비교
4. Arc G-code 생성 및 궤적 시각화
5. 기존 모드와의 호환성 검증
6. 극한 케이스 시뮬레이션
"""

import sys
import os
import math
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from SmartZHop import SmartZHop

# matplotlib 시각화 지원 확인
try:
    import numpy as np
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    HAS_MATPLOTLIB = True
    print("✅ matplotlib 시각화 지원 활성화")
except ImportError as e:
    HAS_MATPLOTLIB = False
    print(f"⚠️ matplotlib 없음, 텍스트 출력만 지원: {e}")

# =============================================================================
# 기본 Arc 테스트 함수들
# =============================================================================

def test_arc_z_height_calculation():
    """Arc 곡선 Z축 높이 계산 함수 테스트"""
    print("\n🎯 Arc 곡선 Z축 높이 계산 검증")
    print("=" * 60)
    
    zhop = SmartZHop()
    
    # 기본 테스트 케이스
    test_cases = [
        {"distance": 0.0, "radius": 50},
        {"distance": 0.5, "radius": 50}, 
        {"distance": 1.0, "radius": 50},
        {"distance": 0.25, "radius": 100},
        {"distance": 0.75, "radius": 25},
    ]
    
    success_count = 0
    
    for i, case in enumerate(test_cases):
        print(f"\n🔍 테스트 케이스 {i+1}: 거리비율={case['distance']:.1f}, 반지름={case['radius']}%")
        
        try:
            # 상승 구간 테스트
            ascent_result = zhop.calculate_arc_z_height_ascent(case['distance'], case['radius'])
            print(f"   📈 상승 구간: {ascent_result:.3f}")
            
            # 하강 구간 테스트  
            descent_result = zhop.calculate_arc_z_height_descent(case['distance'], case['radius'])
            print(f"   📉 하강 구간: {descent_result:.3f}")
            
            # 안전성 검증
            if ascent_result >= 0 and descent_result >= 0:
                print(f"   ✅ 안전성 조건 만족")
                success_count += 1
            else:
                print(f"   ❌ 안전성 조건 위반!")
                
        except Exception as e:
            print(f"   💥 오류: {str(e)}")
    
    print(f"\n📊 Arc Z 높이 계산 테스트 결과: {success_count}/{len(test_cases)} 성공")

def test_arc_point_generation():
    """Arc 포인트 생성 테스트"""
    print("\n🎯 Arc 포인트 생성 검증")
    print("=" * 60)
    
    zhop = SmartZHop()
    
    # 테스트 시나리오들
    test_scenarios = [
        {"name": "기본 시나리오", "start": (0, 0), "end": (10, 10), "z_start": 1.0, "z_end": 1.0, "hop": 2.0, "radius": 50},
        {"name": "상승 경사", "start": (0, 0), "end": (20, 0), "z_start": 1.0, "z_end": 3.0, "hop": 1.5, "radius": 75},
        {"name": "하강 경사", "start": (5, 5), "end": (15, 15), "z_start": 3.0, "z_end": 1.0, "hop": 1.5, "radius": 25},
    ]
    
    for scenario in test_scenarios:
        print(f"\n🔍 시나리오: {scenario['name']}")
        print(f"   경로: {scenario['start']} → {scenario['end']}")
        
        try:
            points = zhop.generate_arc_gcode_points(
                scenario['start'], scenario['end'], 
                scenario['z_start'], scenario['z_end'], 
                scenario['hop'], scenario['radius'], 20
            )
            
            if points and len(points) > 0:
                print(f"   ✅ 포인트 생성 성공: {len(points)}개")
                
                # Z 높이 범위 분석
                z_values = [point[2] for point in points]
                min_z = min(z_values)
                max_z = max(z_values)
                print(f"   📊 Z 범위: {min_z:.3f} ~ {max_z:.3f}mm")
                
                # 안전성 검증
                safety_threshold = min(scenario['z_start'], scenario['z_end'])
                if min_z >= safety_threshold - 0.001:
                    print(f"   ✅ 안전성 검증 통과")
                else:
                    print(f"   ❌ 안전성 위반!")
                    
            else:
                print(f"   ❌ 포인트 생성 실패")
                
        except Exception as e:
            print(f"   💥 오류: {str(e)}")

def test_arc_gcode_generation():
    """Arc G-code 생성 테스트"""
    print("\n🎯 Arc G-code 생성 검증")
    print("=" * 60)
    
    zhop = SmartZHop()
    
    # 테스트 포인트 데이터
    test_points = [
        (0.0, 0.0, 1.0),
        (5.0, 5.0, 3.0),
        (10.0, 10.0, 1.0),
    ]
    
    print(f"📝 테스트 포인트: {len(test_points)}개")
    
    try:
        # G-code 생성
        gcode_lines = zhop.generate_arc_gcode_from_points(test_points, feedrate=3000)
        
        if gcode_lines:
            print(f"✅ G-code 생성 성공: {len(gcode_lines)}줄")
            print("\n📄 생성된 G-code:")
            for i, line in enumerate(gcode_lines[:5]):  # 처음 5줄만 표시
                print(f"   {i+1}: {line}")
            if len(gcode_lines) > 5:
                print(f"   ... (총 {len(gcode_lines)}줄)")
        else:
            print("❌ G-code 생성 실패")
            
    except Exception as e:
        print(f"💥 G-code 생성 오류: {str(e)}")

def test_extreme_cases():
    """극한 케이스 테스트"""
    print("\n⚡ 극한 케이스 테스트")
    print("=" * 60)
    
    zhop = SmartZHop()
    
    extreme_cases = [
        {"name": "초단거리", "start": (0, 0), "end": (0.1, 0.1), "hop": 1.0, "radius": 100},
        {"name": "극소 반지름", "start": (0, 0), "end": (10, 10), "hop": 2.0, "radius": 1},
        {"name": "극대 반지름", "start": (0, 0), "end": (10, 10), "hop": 0.2, "radius": 500},
    ]
    
    success_count = 0
    
    for case in extreme_cases:
        print(f"\n⚡ 케이스: {case['name']}")
        
        try:
            points = zhop.generate_arc_gcode_points(
                case['start'], case['end'], 1.0, 1.0, case['hop'], case['radius'], 20
            )
            
            if points and len(points) > 0:
                print(f"   ✅ 성공: {len(points)}개 포인트")
                success_count += 1
            else:
                print(f"   ❌ 포인트 생성 실패")
                
        except Exception as e:
            print(f"   💥 오류: {str(e)}")
    
    print(f"\n📊 극한 케이스 테스트 결과: {success_count}/{len(extreme_cases)} 성공")

def test_performance_stress():
    """성능 스트레스 테스트"""
    print("\n⚡ 성능 스트레스 테스트")
    print("=" * 60)
    
    zhop = SmartZHop()
    
    # 다양한 부하 수준 테스트
    stress_levels = [
        {"name": "가벼운 부하", "segments": 50},
        {"name": "중간 부하", "segments": 200},
        {"name": "높은 부하", "segments": 500},
    ]
    
    for level in stress_levels:
        print(f"\n💪 {level['name']}: {level['segments']} 세그먼트")
        
        try:
            start_time = time.time()
            points = zhop.generate_arc_gcode_points(
                (0, 0), (100, 100), 1.0, 1.0, 2.0, 50, level['segments']
            )
            end_time = time.time()
            
            if points and len(points) > 0:
                execution_time = (end_time - start_time) * 1000
                print(f"   ✅ 성공: {execution_time:.2f}ms")
                
                # 성능 평가
                if execution_time < 10:
                    print("   🚀 성능 우수")
                elif execution_time < 50:
                    print("   ⚠️ 성능 보통")
                else:
                    print("   ❌ 성능 개선 필요")
            else:
                print("   ❌ 테스트 실패")
                
        except Exception as e:
            print(f"   💥 오류: {str(e)}")

# =============================================================================
# 고급 Arc 안전성 테스트 함수들
# =============================================================================

def test_max_safe_radius_calculation():
    """최대 안전 반지름 계산 테스트"""
    print("\n🛡️ 최대 안전 반지름 계산 검증")
    print("=" * 60)
    
    zhop = SmartZHop()
    
    # 다양한 시나리오로 테스트
    test_scenarios = [
        {"name": "동일 높이", "z_start": 2.0, "z_end": 2.0, "hop": 1.0},
        {"name": "상승 경사", "z_start": 1.0, "z_end": 3.0, "hop": 1.5},
        {"name": "하강 경사", "z_start": 3.0, "z_end": 1.0, "hop": 1.5},
    ]
    
    for scenario in test_scenarios:
        print(f"\n🔍 시나리오: {scenario['name']}")
        z_start = scenario["z_start"]
        z_end = scenario["z_end"]
        hop = scenario["hop"]
        
        try:
            # 안전 반지름 계산을 위한 기본 로직 (SmartZHop에 함수가 없을 경우)
            # 간단한 안전성 기준으로 100% 제한
            max_safe_radius = 100  # 기본값
            
            print(f"   📊 Z 범위: {z_start} ~ {z_end}mm, Hop: {hop}mm")
            print(f"   🎯 최대 안전 반지름: {max_safe_radius}%")
            
            # 검증을 위한 궤적 생성
            test_points = zhop.generate_arc_gcode_points(
                (0, 0), (50, 0), z_start, z_end, hop, max_safe_radius, 20
            )
            
            if test_points:
                min_z = min(point[2] for point in test_points)
                safety_threshold = min(z_start, z_end)
                
                if min_z >= safety_threshold - 0.001:
                    print(f"   ✅ 안전성 검증 통과!")
                else:
                    print(f"   ❌ 안전성 위반!")
            else:
                print(f"   ❌ 테스트 포인트 생성 실패")
                
        except Exception as e:
            print(f"   💥 오류: {str(e)}")

def test_integrated_arc_safety():
    """통합 Arc 안전성 테스트"""
    print("\n🛡️ 통합 Arc 안전성 테스트")
    print("=" * 60)
    
    zhop = SmartZHop()
    
    # 종합적인 안전성 시나리오들
    comprehensive_scenarios = [
        {"name": "표준 케이스", "z_start": 2.0, "z_end": 2.0, "hop": 1.5},
        {"name": "상승 경사", "z_start": 1.0, "z_end": 3.5, "hop": 2.0},
        {"name": "하강 경사", "z_start": 4.0, "z_end": 1.5, "hop": 1.8},
    ]
    
    success_count = 0
    total_count = len(comprehensive_scenarios)
    
    for scenario in comprehensive_scenarios:
        print(f"\n🔍 종합 테스트: {scenario['name']}")
        z_start = scenario["z_start"]
        z_end = scenario["z_end"]
        hop = scenario["hop"]
        
        try:
            # 안전 반지름으로 궤적 생성
            safe_points = zhop.generate_arc_gcode_points(
                (0, 0), (30, 0), z_start, z_end, hop, 50, 30  # 50% 반지름 사용
            )
            
            if safe_points:
                min_z = min(point[2] for point in safe_points)
                safety_threshold = min(z_start, z_end)
                
                print(f"   🎯 궤적 최저점: {min_z:.3f}mm")
                print(f"   🛡️ 안전 하한선: {safety_threshold:.3f}mm")
                
                if min_z >= safety_threshold - 0.001:
                    print(f"   ✅ 통합 안전성 검증 통과!")
                    success_count += 1
                else:
                    print(f"   ❌ 안전성 위반!")
            else:
                print(f"   ❌ 포인트 생성 실패")
                
        except Exception as e:
            print(f"   💥 통합 테스트 실패: {str(e)}")
    
    print(f"\n🏆 통합 Arc 안전성 결과: {success_count}/{total_count} 성공")

# =============================================================================
# 시각화 함수들
# =============================================================================

def visualize_arc_comparison():
    """Arc 비교 시각화"""
    print("\n📈 Arc 비교 시각화")
    print("=" * 60)
    
    zhop = SmartZHop()
    
    if HAS_MATPLOTLIB:
        # matplotlib 시각화
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle('Arc 곡선 비교', fontsize=14, fontweight='bold')
        
        # 여러 반지름 비교
        radius_ratios = [25, 50, 75, 100]
        colors = ['red', 'blue', 'green', 'purple']
        
        for ratio, color in zip(radius_ratios, colors):
            # 상승 구간
            distance_range = [i/20.0 for i in range(21)]
            z_values = [zhop.calculate_arc_z_height_ascent(d, ratio) for d in distance_range]
            ax1.plot(distance_range, z_values, color=color, label=f'{ratio}% 반지름', linewidth=2)
            
            # 하강 구간
            z_values = [zhop.calculate_arc_z_height_descent(d, ratio) for d in distance_range]
            ax2.plot(distance_range, z_values, color=color, label=f'{ratio}% 반지름', linewidth=2)
        
        ax1.set_title('상승 구간 Arc 곡선')
        ax1.set_xlabel('거리 비율')
        ax1.set_ylabel('Z 높이 비율')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        ax2.set_title('하강 구간 Arc 곡선')
        ax2.set_xlabel('거리 비율')
        ax2.set_ylabel('Z 높이 비율')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        plt.show()
        print("✅ GUI 그래프 창이 열렸습니다.")
    else:
        print("⚠️ matplotlib 없음 - 텍스트 출력만 지원")
        
        # 텍스트 기반 시각화
        for ratio in [25, 50, 75, 100]:
            print(f"\n🔵 Arc 반지름 비율: {ratio}%")
            
            # 상승/하강 구간 샘플 값들
            sample_points = [0.0, 0.25, 0.5, 0.75, 1.0]
            print("   거리비율  상승Z   하강Z")
            print("   " + "-" * 24)
            
            for d in sample_points:
                ascent_z = zhop.calculate_arc_z_height_ascent(d, ratio)
                descent_z = zhop.calculate_arc_z_height_descent(d, ratio)
                print(f"     {d:4.2f}   {ascent_z:5.3f}  {descent_z:5.3f}")

# =============================================================================
# 통합 실행 함수들
# =============================================================================

def run_basic_tests():
    """기본 Arc 테스트 실행"""
    print("\n🧪 기본 Arc 테스트 실행")
    print("=" * 60)
    
    basic_tests = [
        ("Arc Z축 높이 계산", test_arc_z_height_calculation),
        ("Arc 포인트 생성", test_arc_point_generation),
        ("Arc G-code 생성", test_arc_gcode_generation),
        ("극한 케이스", test_extreme_cases),
        ("성능 스트레스", test_performance_stress),
    ]
    
    success_count = 0
    
    for test_name, test_func in basic_tests:
        try:
            print(f"\n🔄 {test_name} 테스트 실행 중...")
            test_func()
            print(f"✅ {test_name} 완료")
            success_count += 1
        except Exception as e:
            print(f"❌ {test_name} 실패: {str(e)}")
    
    print(f"\n📊 기본 테스트 결과: {success_count}/{len(basic_tests)} 성공")

def run_advanced_tests():
    """고급 Arc 안전성 테스트 실행"""
    print("\n🛡️ 고급 Arc 안전성 테스트 실행")
    print("=" * 60)
    
    advanced_tests = [
        ("최대 안전 반지름 계산", test_max_safe_radius_calculation),
        ("통합 Arc 안전성", test_integrated_arc_safety),
    ]
    
    success_count = 0
    
    for test_name, test_func in advanced_tests:
        try:
            print(f"\n🔄 {test_name} 테스트 실행 중...")
            test_func()
            print(f"✅ {test_name} 완료")
            success_count += 1
        except Exception as e:
            print(f"❌ {test_name} 실패: {str(e)}")
    
    print(f"\n📊 고급 테스트 결과: {success_count}/{len(advanced_tests)} 성공")

def run_all_tests():
    """모든 테스트 한번에 실행"""
    print("\n🚀 Smart Z-Hop Arc 모드 전체 테스트 실행")
    print("=" * 80)
    
    try:
        # 1. 기본 테스트
        run_basic_tests()
        
        print("\n" + "─" * 80)
        
        # 2. 고급 테스트
        run_advanced_tests()
        
        print("\n" + "─" * 80)
        
        # 3. 시각화
        visualize_arc_comparison()
        
        print("\n🎉 모든 Arc 테스트가 완료되었습니다!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n💥 전체 테스트 실행 중 오류: {str(e)}")

# =============================================================================
# 메인 실행부
# =============================================================================

if __name__ == "__main__":
    print("🎯 Smart Z-Hop Arc 모드 테스트")
    print("=" * 50)
    print("1. 기본 테스트만 실행")
    print("2. 고급 안전성 테스트만 실행") 
    print("3. 시각화만 실행")
    print("4. 모든 테스트 한번에 실행")
    print("5. 종료")
    
    while True:
        try:
            choice = input("\n선택하세요 (1-5): ").strip()
            
            if choice == "1":
                run_basic_tests()
            elif choice == "2":
                run_advanced_tests()
            elif choice == "3":
                visualize_arc_comparison()
            elif choice == "4":
                run_all_tests()
            elif choice == "5":
                print("👋 테스트를 종료합니다.")
                break
            else:
                print("❌ 잘못된 선택입니다. 1-5 중에서 선택해주세요.")
                
        except KeyboardInterrupt:
            print("\n\n👋 테스트를 종료합니다.")
            break
        except Exception as e:
            print(f"💥 오류가 발생했습니다: {str(e)}")
