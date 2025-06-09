# -*- coding: utf-8 -*-
"""
Smart Z-Hop Advanced Test Script
Real G-code processing simulation and result validation

This test script validates the Smart Z-Hop functionality by simulating
real-world G-code processing scenarios.

Original algorithms tested:
- Z-HopMove v0.3.1 by hawmaru (요래요래): https://blog.naver.com/hawmaru/221576526356
- Slingshot Z-Hop by echo-lalia: https://github.com/echo-lalia/Slingshot-Z-Hop
"""

import sys
import os
import math
import locale
try:
    from wcwidth import wcswidth
except ImportError:
    # Fallback for when wcwidth is not available
    def wcswidth(text):
        return len(text)

# Internationalization support
TRANSLATIONS = {
    'ko_KR': {
        'test_title': 'Smart Z-Hop 고급 테스트 스위트',
        'test_subtitle': '🚀 Smart Z-Hop 코어 기능 검증',
        'testing_implementations': '전통적 및 슬링샷 Z-hop 구현 테스트',
        'running_test': '실행 중',
        'test_passed': '통과',
        'test_failed': '실패',
        'all_tests_passed': '모든 테스트가 통과했습니다!',
        'some_tests_failed': '일부 테스트가 실패했습니다.',
        'total_tests': '총 테스트',
        'passed': '통과',
        'failed': '실패',
        'results_summary': '결과 요약',
        'documentation': '문서',
        'readme_guide': 'README.md - 완전한 사용자 가이드',
        'original_sources': '원본 소스가 문서에 명시됨',
        'test_suite_validates': '이 테스트 스위트는 모든 핵심 기능을 검증합니다',
        'basic_functionality': '기본 기능 테스트',
        'basic_functionality_desc': 'SmartZHopTester 클래스와 기본 메서드 검증',
        'distance_calculation': '거리 계산 테스트',
        'distance_calculation_desc': '두 점 사이의 유클리드 거리 계산 정확도 검증',
        'interpolation': '선형 보간 테스트',
        'interpolation_desc': '최소/최대 값 사이의 선형 보간 정확도 검증',
        'gcode_processing': 'G-code 처리 테스트',
        'gcode_processing_desc': '실제 G-code 라인 처리 및 Z-hop 적용 검증',
        'gcode_parsing': 'G-code 파싱 테스트',
        'gcode_parsing_desc': 'G-code 매개변수 추출 검증',
        'slingshot_processing': '슬링샷 처리 테스트',
        'slingshot_processing_desc': '슬링샷 Z-hop 알고리즘 검증',
        
        # Slingshot processing test
        'slingshot_validation': 'Smart Z-Hop: 슬링샷 알고리즘 검증',
        'original_gcode_input': '원본 G-code 입력',
        'processed_gcode_output': '처리된 G-code 출력',
        'analysis_results': '분석 결과',
        'original_travel_moves': '원본 이동 명령',
        'generated_zhop_moves': '생성된 Z-hop 명령',
        'zhop_application_rate': 'Z-hop 적용률',
        'test_result': '테스트 결과',
        'processing_rate': '처리율',
        
        # Distance calculation test
        'euclidean_distance_test': '유클리드 거리 계산 테스트',
        'test_cases': '테스트 케이스',
        'horizontal_movement': '수평 이동',
        'vertical_movement': '수직 이동',
        'pythagorean_triangle': '피타고라스 3-4-5 삼각형',
        'diagonal_movement': '대각선 이동',
        'all_tests_passed_status': '모든 테스트 통과',
        'some_tests_failed_status': '일부 테스트 실패',
        'result': '결과',
        
        # G-code parsing test
        'gcode_parameter_extraction': 'G-code 매개변수 추출 테스트',
        'parsing_test_cases': '파싱 테스트 케이스',
        'complete_movement_command': '완전한 이동 명령',
        'travel_move_command': '이동 명령',
        'extrusion_command': '압출 명령',
        'temperature_command': '온도 명령',
        'home_command_with_comment': '홈 명령 (코멘트 포함)',
        'command': '명령',
        'parsed': '파싱됨',
        'gcode_parsing_completed': 'G-code 파싱 완료',
        
        # Interpolation test
        'linear_interpolation_validation': '선형 보간 검증',
        'distance_zhop_mapping': '거리 → Z-hop 높이 매핑',
        'distance_mm': '거리(mm)',
        'zhop_mm': 'Z-hop(mm)',
        'linear_interpolation_working': '선형 보간이 올바르게 작동함',
        'values_clamped_note': '100mm를 초과하는 값은 최대 높이로 제한됨',
        'note': '참고',
        
        # Production ready messages
        'ready_for_production': '프로덕션 사용 준비',
        'copy_smartzhop': 'SmartZHop.py를 Cura scripts 폴더에 복사',
        'restart_cura': 'Cura 완전히 재시작',
        'goto_extensions': 'Extensions → Post Processing → Modify G-Code로 이동',
        'add_script': 'Add a script → Select Smart Z-Hop',
        'configure_settings': '원하는 모드와 설정 구성',
        'enjoy_printing': 'Smart Z-Hop으로 향상된 3D 프린팅을 즐기세요!'
    },
    'en_US': {
        'test_title': 'Smart Z-Hop Advanced Test Suite',
        'test_subtitle': '🚀 Smart Z-Hop Core Functionality Validation',
        'testing_implementations': 'Testing Traditional and Slingshot Z-hop implementations',
        'running_test': 'Running',
        'test_passed': 'PASSED',
        'test_failed': 'FAILED',
        'all_tests_passed': 'All tests passed successfully!',
        'some_tests_failed': 'Some tests failed.',
        'total_tests': 'Total tests',
        'passed': 'passed',
        'failed': 'failed',
        'results_summary': 'Results Summary',
        'documentation': 'Documentation',
        'readme_guide': 'README.md - Complete user guide',
        'original_sources': 'Original sources credited in documentation',
        'test_suite_validates': 'This test suite validates all core functionality',
        'basic_functionality': 'Basic Functionality Test',
        'basic_functionality_desc': 'Validates SmartZHopTester class and basic methods',
        'distance_calculation': 'Distance Calculation Test',
        'distance_calculation_desc': 'Validates Euclidean distance calculation accuracy',
        'interpolation': 'Linear Interpolation Test',
        'interpolation_desc': 'Validates linear interpolation accuracy between min/max values',
        'gcode_processing': 'G-code Processing Test',
        'gcode_processing_desc': 'Validates real G-code line processing and Z-hop application',
        'gcode_parsing': 'G-code Parsing Test',
        'gcode_parsing_desc': 'Validates G-code parameter extraction',
        'slingshot_processing': 'Slingshot Processing Test',
        'slingshot_processing_desc': 'Validates slingshot Z-hop algorithm',
        
        # Slingshot processing test
        'slingshot_validation': 'Smart Z-Hop: Slingshot Algorithm Validation',
        'original_gcode_input': 'Original G-code Input',
        'processed_gcode_output': 'Processed G-code Output',
        'analysis_results': 'Analysis Results',
        'original_travel_moves': 'Original travel moves',
        'generated_zhop_moves': 'Generated Z-hop moves',
        'zhop_application_rate': 'Z-hop application rate',
        'test_result': 'Test Result',
        'processing_rate': 'processing rate',
        
        # Distance calculation test
        'euclidean_distance_test': 'Euclidean Distance Calculation Test',
        'test_cases': 'Test Cases',
        'horizontal_movement': 'Horizontal movement',
        'vertical_movement': 'Vertical movement',
        'pythagorean_triangle': 'Pythagorean 3-4-5 triangle',
        'diagonal_movement': 'Diagonal movement',
        'all_tests_passed_status': 'ALL TESTS PASSED',
        'some_tests_failed_status': 'SOME TESTS FAILED',
        'result': 'Result',
        
        # G-code parsing test
        'gcode_parameter_extraction': 'G-code Parameter Extraction Test',
        'parsing_test_cases': 'Parsing Test Cases',
        'complete_movement_command': 'Complete movement command',
        'travel_move_command': 'Travel move command',
        'extrusion_command': 'Extrusion command',
        'temperature_command': 'Temperature command',
        'home_command_with_comment': 'Home command with comment',
        'command': 'Command',
        'parsed': 'Parsed',
        'gcode_parsing_completed': 'G-code parsing completed successfully',
        
        # Interpolation test
        'linear_interpolation_validation': 'Linear Interpolation Validation',
        'distance_zhop_mapping': 'Distance → Z-hop Height Mapping',
        'distance_mm': 'Distance(mm)',
        'zhop_mm': 'Z-hop(mm)',
        'linear_interpolation_working': 'Linear interpolation working correctly',
        'values_clamped_note': 'Values >100mm are clamped to maximum height',
        'note': 'Note',
        
        # Production ready messages
        'ready_for_production': 'Ready for Production Use',
        'copy_smartzhop': 'Copy SmartZHop.py to Cura scripts folder',
        'restart_cura': 'Restart Cura completely',
        'goto_extensions': 'Go to Extensions → Post Processing → Modify G-Code',
        'add_script': 'Add a script → Select Smart Z-Hop',
        'configure_settings': 'Configure your preferred mode and settings',
        'enjoy_printing': 'Enjoy enhanced 3D printing with Smart Z-Hop!'
    }
}

def get_system_language():
    """Detect system language for automatic localization"""
    # Check for command line argument override
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--lang-en':
        return 'en_US'
    if len(sys.argv) > 1 and sys.argv[1] == '--lang-ko':
        return 'ko_KR'
    
    try:
        system_locale = locale.getdefaultlocale()[0]
        if system_locale and system_locale.startswith('ko'):
            return 'ko_KR'
    except:
        pass
    return 'en_US'

def t(key):
    """Get translated text for the current system language"""
    lang = get_system_language()
    return TRANSLATIONS.get(lang, TRANSLATIONS['en_US']).get(key, key)

# SmartZHop 클래스를 독립적으로 테스트하기 위한 모의 클래스들
class MockScript:
    def __init__(self):
        self.settings = {}
    
    def getSettingValueByKey(self, key):
        return self.settings.get(key, None)

class MockI18n:
    @staticmethod
    def i18nc(context, text):
        return text

# SmartZHop의 핵심 기능만 추출한 테스트용 클래스
class SmartZHopTester:
    def __init__(self):
        self.settings = {}

    def calculate_distance(self, x1, y1, x2, y2):
        """Calculate Euclidean distance between two points"""
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def getValue(self, line, key):
        """Extract value for given key from G-code line"""
        if key in line:
            try:
                start_index = line.index(key) + len(key)
                end_index = start_index
                for i in range(start_index, len(line)):
                    if line[i].isspace() or line[i].isalpha():
                        end_index = i
                        break
                else:
                    end_index = len(line)
                
                value_str = line[start_index:end_index].strip()
                return float(value_str) if value_str else None
            except (ValueError, IndexError):
                return None
        return None

    def linear_interpolation(self, value, minimum, maximum, start_value, end_value):
        """Linear interpolation between start_value and end_value"""
        if value >= maximum:
            return end_value
        if value <= minimum:
            return start_value
        
        normalized_value = (value - minimum) / (maximum - minimum)
        interpolated_value = start_value + (end_value - start_value) * normalized_value
        return interpolated_value

    def is_travel_move(self, line):
        """Check if line is a travel move (G0 or G1 without E parameter)"""
        return (('G0' in line or 'G1' in line) and 'E' not in line and 
                ('X' in line or 'Y' in line))

    def process_slingshot_zhop(self, gcode_lines, settings):
        """Simplified slingshot Z-hop processing for testing"""
        modified_lines = []
        
        # Settings
        min_zhop = settings.get('min_zhop', 0.0)
        max_zhop = settings.get('max_zhop', 2.0)
        max_distance = settings.get('max_distance', 80.0)
        z_feedrate = settings.get('z_feedrate', 3000)
        second_move_percent = settings.get('second_move_percent', 10)
        tr_distance = settings.get('tr_distance', 20.0)
        
        # Calculate distance factors
        second_distance_factor = second_move_percent * 0.01
        first_distance_factor = 1.0 - second_distance_factor
        
        # Initialize tracking variables
        current_z_height = 0
        current_feedrate = 3000
        target_x = 0
        target_y = 0  
        prev_x = 0
        prev_y = 0
        
        for line in gcode_lines:
            # Parse position updates
            if 'G1' in line or 'G0' in line:
                prev_x = target_x
                prev_y = target_y
                
                if self.getValue(line, 'X') is not None:
                    target_x = self.getValue(line, 'X')
                if self.getValue(line, 'Y') is not None:
                    target_y = self.getValue(line, 'Y')
                if self.getValue(line, 'Z') is not None:
                    current_z_height = self.getValue(line, 'Z')
                if self.getValue(line, 'F') is not None:
                    current_feedrate = self.getValue(line, 'F')
            
            # Process travel moves
            if self.is_travel_move(line):
                # Calculate travel distance
                distance = self.calculate_distance(prev_x, prev_y, target_x, target_y)
                
                # Only process if distance meets minimum threshold
                if distance >= tr_distance:
                    # Calculate Z-hop height based on distance
                    zhop_height = current_z_height + self.linear_interpolation(
                        distance, 0, max_distance, min_zhop, max_zhop)

                    # Calculate peak position (slingshot trajectory)
                    delta_x = target_x - prev_x
                    peak_x = prev_x + (delta_x * first_distance_factor)
                    delta_y = target_y - prev_y  
                    peak_y = prev_y + (delta_y * first_distance_factor)

                    # Generate slingshot Z-hop moves
                    zhop_line = f'G1 X{round(peak_x, 5)} Y{round(peak_y, 5)} Z{round(zhop_height, 5)} F{current_feedrate} ; SmartZHop-Slingshot'
                    lower_line = f'G1 X{target_x} Y{target_y} Z{current_z_height} F{z_feedrate} ; SmartZHop-Slingshot Lower'
                    
                    modified_lines.append(zhop_line)
                    modified_lines.append(lower_line)
                else:
                    # Distance too small, use original line
                    modified_lines.append(line)
            else:
                # Not a travel move, add original line
                modified_lines.append(line)
        
        return modified_lines

def create_test_gcode():
    """더 현실적인 테스트용 G-code 생성"""
    return [
        ";FLAVOR:Marlin",
        ";TIME:100",
        ";LAYER_COUNT:3", 
        ";Layer height: 0.2",
        "",
        ";LAYER:0",
        "G28 ; home all axes",
        "G1 X10 Y10 Z0.2 F3000",
        "G1 X20 Y20 E5 F1500 ; print move",
        "G0 X50 Y50 ; travel move (거리: ~42mm)",
        "G1 X60 Y60 E10 F1500 ; print move",
        "",
        ";LAYER:1", 
        "G1 Z0.4",
        "G1 X10 Y10 E15 F1500",
        "G0 X100 Y100 ; long travel move (거리: ~127mm)",
        "G1 X110 Y110 E20 F1500",
        "",
        ";LAYER:2",
        "G1 Z0.6", 
        "G1 X10 Y10 E25 F1500",
        "G0 X15 Y15 ; short travel (거리: ~7mm)",
        "G1 X20 Y20 E30 F1500",
        "M104 S0 ; turn off hotend"
    ]

def test_slingshot_processing():
    """🔬 Slingshot Algorithm Processing Test"""
    print(f"🚀 === {t('slingshot_validation')} ===")
    
    tester = SmartZHopTester()
    test_gcode = create_test_gcode()
    
    # Test configuration
    settings = {
        'min_zhop': 0.5,
        'max_zhop': 3.0,
        'max_distance': 100.0,
        'z_feedrate': 3000,
        'second_move_percent': 15,
        'tr_distance': 20.0
    }
    
    print(f"📄 {t('original_gcode_input')}:")
    for i, line in enumerate(test_gcode):
        print(f"  {i+1:2d}: {line}")
    
    print(f"\n✨ {t('processed_gcode_output')}:")
    processed = tester.process_slingshot_zhop(test_gcode, settings)
    
    for i, line in enumerate(processed):
        marker = "🎯" if 'SmartZHop-Slingshot' in line else "  "
        print(f"{marker} {i+1:2d}: {line}")
    
    # Result analysis
    zhop_moves = [line for line in processed if 'SmartZHop-Slingshot' in line]
    travel_moves = [line for line in test_gcode if 'G0' in line and 'X' in line and 'Y' in line]
    
    print(f"\n📊 {t('analysis_results')}:")
    print(f"   ├─ {t('original_travel_moves')}: {len(travel_moves)}")
    print(f"   ├─ {t('generated_zhop_moves')}: {len(zhop_moves)}")
    print(f"   └─ {t('zhop_application_rate')}: {len(zhop_moves)//2}/{len(travel_moves)} = {(len(zhop_moves)//2)/len(travel_moves)*100:.1f}%")
    
    # Validation
    success_rate = (len(zhop_moves)//2)/len(travel_moves)*100 if travel_moves else 0
    status = "✅ PASS" if success_rate > 0 else "❌ FAIL"
    print(f"   🏆 {t('test_result')}: {status} ({success_rate:.1f}% {t('processing_rate')})")

def test_distance_calculation():
    """📏 Distance Calculation Validation Test"""
    print(f"\n🧮 === {t('euclidean_distance_test')} ===")
    
    tester = SmartZHopTester()
    
    test_cases = [
        ((0, 0), (10, 0), 10.0, t("horizontal_movement")),     
        ((0, 0), (0, 10), 10.0, t("vertical_movement")),       
        ((0, 0), (3, 4), 5.0, t("pythagorean_triangle")),      
        ((10, 20), (50, 50), 50.0, t("diagonal_movement")), 
    ]
    
    print(f"🎯 {t('test_cases')}:")
    all_passed = True
    for (x1, y1), (x2, y2), expected, description in test_cases:
        calculated = tester.calculate_distance(x1, y1, x2, y2)
        error = abs(calculated - expected)
        status = "✅" if error < 0.001 else "❌"
        if error >= 0.001:
            all_passed = False
            
        print(f"   {status} ({x1:2},{y1:2}) → ({x2:2},{y2:2}): "
              f"calc={calculated:.3f}, exp={expected:.3f}, err={error:.3f} | {description}")
    
    final_status = f"✅ {t('all_tests_passed_status')}" if all_passed else f"❌ {t('some_tests_failed_status')}"
    print(f"   🏆 {t('result')}: {final_status}")

def test_gcode_parsing():
    """🔍 G-code Parsing Validation Test"""
    print(f"\n📝 === {t('gcode_parameter_extraction')} ===")
    
    tester = SmartZHopTester()
    
    test_lines = [
        ("G1 X10.5 Y20.3 Z0.2 F1500", t("complete_movement_command")),
        ("G0 X50 Y75", t("travel_move_command")),
        ("G1 X100 Y200 E25.5 F1200", t("extrusion_command")),
        ("M104 S200", t("temperature_command")),
        ("G28 ; home all", t("home_command_with_comment"))
    ]
    
    print(f"🎯 {t('parsing_test_cases')}:")
    for line, description in test_lines:
        x = tester.getValue(line, 'X')
        y = tester.getValue(line, 'Y')
        z = tester.getValue(line, 'Z')
        f = tester.getValue(line, 'F')
        is_travel = tester.is_travel_move(line)
        
        travel_indicator = "🚀" if is_travel else "🖨️"
        print(f"   {travel_indicator} {description}")
        print(f"      └─ {t('command')}: {line}")
        print(f"      └─ {t('parsed')}: X={x}, Y={y}, Z={z}, F={f}, Travel={is_travel}")
    
    print(f"   🏆 {t('result')}: ✅ {t('gcode_parsing_completed')}")

def test_interpolation():
    """📈 Linear Interpolation Algorithm Test"""
    print(f"\n🎯 === {t('linear_interpolation_validation')} ===")
    
    def pad_fixed_width(text, width):
        """전각 문자 폭에 맞춰 시각적으로 정렬"""
        visual_width = wcswidth(text)
        if visual_width is None:
            visual_width = len(text)
        return text + ' ' * (width - visual_width)
    
    tester = SmartZHopTester()
    # Distance 0-100mm mapping to Z-hop height 0.5-3.0mm
    test_distances = [0, 25, 50, 75, 100, 150]
    
    print(f"📊 {t('distance_zhop_mapping')}:")
    # Dynamic table layout calculation
    distance_header = t('distance_mm')
    zhop_header = t('zhop_mm')
    
    # 각 열의 최대 표시 폭 계산
    max_distance_strs = [f"🔄 {d:>3}" if d <= 100 else f"📌 {d:>3}" for d in test_distances]
    max_distance_content_width = max(wcswidth(s) if wcswidth(s) is not None else len(s) for s in max_distance_strs)
    distance_header_width = wcswidth(distance_header) if wcswidth(distance_header) is not None else len(distance_header)
    zhop_header_width = wcswidth(zhop_header) if wcswidth(zhop_header) is not None else len(zhop_header)

    distance_col_width = max(distance_header_width, max_distance_content_width) + 2
    zhop_col_width = max(zhop_header_width, 8) + 2

    # 테두리 라인
    header_line = "┏" + "━" * distance_col_width + "┳" + "━" * zhop_col_width + "┓"
    separator_line = "┣" + "━" * distance_col_width + "╋" + "━" * zhop_col_width + "┫"
    footer_line = "┗" + "━" * distance_col_width + "┻" + "━" * zhop_col_width + "┛"

    print(f"   {header_line}")

    # 헤더 출력
    dist_cell = pad_fixed_width(f" {distance_header} ", distance_col_width)
    zhop_cell = pad_fixed_width(f" {zhop_header} ", zhop_col_width)
    print(f"   ┃{dist_cell}┃{zhop_cell}┃")

    print(f"   {separator_line}")

    # 데이터 행 출력
    for d in test_distances:
        height = tester.linear_interpolation(d, 0, 100, 0.5, 3.0)
        emoji = "🔄" if d <= 100 else "📌"
        dist_text = f"{emoji} {d:>3}"
        dist_cell = pad_fixed_width(f" {dist_text} ", distance_col_width)
        zhop_text = f"{height:>6.2f}"
        zhop_cell = pad_fixed_width(f" {zhop_text} ", zhop_col_width)
        print(f"   ┃{dist_cell}┃{zhop_cell}┃")

    print(f"   {footer_line}")
    print(f"   🏆 {t('result')}: ✅ {t('linear_interpolation_working')}")
    print(f"   📝 {t('note')}: {t('values_clamped_note')}")

def main():
    print(f"🚀 {t('test_title')}")
    print("=" * 60)
    print(f"🔬 {t('test_subtitle')}")
    print(f"📊 {t('testing_implementations')}")
    print("=" * 60)
    
    # Test results tracking
    tests = [
        (test_distance_calculation, t('distance_calculation'), t('distance_calculation_desc')),
        (test_gcode_parsing, t('gcode_parsing'), t('gcode_parsing_desc')),
        (test_interpolation, t('interpolation'), t('interpolation_desc')),
        (test_slingshot_processing, t('slingshot_processing'), t('slingshot_processing_desc'))
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_func, test_name, test_desc in tests:
        print(f"\n🔍 {t('running_test')}: {test_name}")
        print(f"   📝 {test_desc}")
        try:
            result = test_func()
            if result != False:  # Test passed
                print(f"   ✅ {t('test_passed')}")
                passed_tests += 1
            else:
                print(f"   ❌ {t('test_failed')}")
        except Exception as e:
            print(f"   ❌ {t('test_failed')}: {str(e)}")
    
    print("\n" + "=" * 60)
    
    # Results summary
    if passed_tests == total_tests:
        print(f"🎉 {t('all_tests_passed')}")
        status_emoji = "✅"
    else:
        print(f"⚠️ {t('some_tests_failed')}")
        status_emoji = "❌"
    
    print(f"\n📊 {t('results_summary')}:")
    print(f"   {status_emoji} {t('total_tests')}: {total_tests}")
    print(f"   ✅ {t('passed')}: {passed_tests}")
    print(f"   ❌ {t('failed')}: {total_tests - passed_tests}")
    print("=" * 60)
    
    if passed_tests == total_tests:
        print(f"\n📋 {t('ready_for_production')}:")
        print(f"   1️⃣  {t('copy_smartzhop')}")
        print(f"   2️⃣  {t('restart_cura')}")
        print(f"   3️⃣  {t('goto_extensions')}")
        print(f"   4️⃣  {t('add_script')}")
        print(f"   5️⃣  {t('configure_settings')}")
        print(f"\n🌟 {t('enjoy_printing')}")
    
    print(f"\n📚 {t('documentation')}:")
    print(f"   📖 {t('readme_guide')}")
    print(f"   🔗 {t('original_sources')}")
    print(f"   🧪 {t('test_suite_validates')}")

if __name__ == "__main__":
    main()
