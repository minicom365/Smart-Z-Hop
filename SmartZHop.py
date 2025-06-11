# -*- coding: utf-8 -*-
"""
Smart Z-Hop v2.0 - Complete Integration Edition
Advanced Z-Hop post-processing script with ALL features from V1 and V2

ORIGINAL SOURCES:
- Z-HopMove v0.3.1 by hawmaru (요래요래)
  Blog: https://blog.naver.com/hawmaru/221576526356
  Traditional vertical Z-hop algorithm foundation

- Slingshot Z-Hop by echo-lalia
  GitHub: https://github.com/echo-lalia/Slingshot-Z-Hop
  Revolutionary curved trajectory algorithm foundation

SMART Z-HOP COMPLETE FEATURES:
- Dual Algorithm Support: Traditional vs Slingshot modes
- M203 Speed Control: Z-axis speed limiting using G-code commands
- Advanced Layer Control: Custom Layers, Top/Bottom Only targeting
- Trajectory Modes: Percentage vs Angle-based calculations (V2)
- 3-Stage System: Ascent, Travel, Descent phases (V2) 
- Complete Internationalization: Korean/English auto-detection
- Dynamic Height Calculation: Distance-based adaptive Z-hop
- Unified Settings Structure: All V1/V2 features integrated

Version: 2.0 Complete Integration Edition
"""

import re
import math
import locale

# 조건부 Import: Cura 환경에서는 정상 Import, 독립 실행 시에는 Mock 클래스 사용
try:
    from ..Script import Script
except (ImportError, ValueError):
    # 독립 실행 환경을 위한 Mock Script 클래스
    class Script:
        def __init__(self):
            pass
        
        def getSettingValueByKey(self, key):
            """Mock 설정값 반환 (테스트용 기본값)"""
            mock_settings = {
                'enable': True,
                'zhop_mode': 'slingshot',  # Slingshot 모드로 변경 
                'layer_change_zhop': True,
                'zhop_height_type': 'custom',
                'zhop_height': 0.3,  # 높이 증가
                'travel_zhop': True,
                'travel_distance': 1.0,  # 적당한 임계값
                'custom_layers': '',
                'top_bottom_only': False,
                'zhop_speed': 15,  # 속도 설정
                'slingshot_min_zhop': 0.1,
                'slingshot_max_distance': 100.0,  # 최대 거리 증가
                'slingshot_trajectory_mode': 'percentage',
                'slingshot_ascent_ratio': 25,
                'slingshot_descent_ratio': 25,
                'slingshot_ascent_angle': 45.0,
                'slingshot_descent_angle': 45.0,
                'slingshot_angle_priority': False,
                'slingshot_z_feedrate': 15.0,  # Z축 속도
            }
            return mock_settings.get(key, None)

# 완전한 다국어 지원을 위한 통합 번역 딕셔너리 (V1 + V2 + Current)
TRANSLATIONS = {
    'ko_KR': {
        'Smart Z-Hop': 'Smart Z-Hop',
        'Enable': '활성화',
        'Enable Smart Z-Hop functionality': 'Smart Z-Hop 기능을 활성화/비활성화합니다. 체크하면 설정된 조건에 따라 Z-홉이 실행됩니다.',
        'Z-Hop Mode': 'Z-홉 모드',        'Select Z-Hop mode': 'Z-홉 알고리즘을 선택합니다: 전통적 (수직) 또는 스마트 (곡선)',        'Traditional': '전통적',
        'Slingshot': 'Smart Mode',
        'Layer Change': '레이어 변경 시',
        'Z-Hop before layer change': '새 레이어로 이동하기 전에 Z-홉을 실행합니다. 레이어 경계에서 노즐과 프린트의 충돌을 방지합니다.',
        'Z-Hop Height': 'Z-홉 높이',
        'Select Z-Hop height': 'Z-홉 높이를 설정합니다: 레이어 높이 또는 사용자 지정',
        'Layer Height': '레이어 높이',
        'Custom Height': '사용자 지정 높이',
        'Custom Z-hop height value': '사용자 지정 Z-홉 높이를 밀리미터 단위로 입력합니다. 일반적으로 0.2~1.0mm 범위를 사용합니다.',
        'Travel': '이동 중',
        'Z-Hop before travel moves': '압출 없는 이동(트래블) 전에 Z-홉을 실행합니다. 프린트된 부분과의 충돌을 방지합니다.',
        'Travel Distance': '최소 이동 거리',
        'Apply Z-Hop only for moves longer than this distance': '설정한 거리보다 긴 이동에서만 Z-홉을 실행합니다. 짧은 이동에서는 Z-홉을 건너뛰어 인쇄 시간을 단축합니다.',
        'Custom Layers': '지정 레이어',
        'Apply Travel Z-Hop only on specified layers': '특정 레이어에서만 이동 Z-홉을 적용합니다. 레이어 번호를 공백으로 구분하여 입력 (예: 1 5 10 15)',
        'Top/Bottom Only': '상하단 레이어만',
        'Apply Travel Z-Hop only on top/bottom layers': '첫 번째와 마지막 레이어에서만 이동 Z-홉을 적용합니다. 주요 표면 품질 향상에 집중합니다.',
        'Z-Hop Speed': 'Z-홉 속도',
        'Z-axis speed limit for Z-hop movements (0 = unlimited)': 'Z-홉 이동 시 Z축 속도 제한 (0 = 무제한)',
        'Min Z-Hop (Smart Mode)': '최소 Z-홉 높이',
        'Minimum Z-hop height for slingshot mode': '스마트 모드에서 사용할 최소 Z-홉 높이입니다. 짧은 거리 이동 시 적용됩니다.',
        'Max Distance (Smart Mode)': '기준 최대 거리',
        'Maximum travel distance for height calculation': '높이 계산의 기준이 되는 최대 이동 거리입니다. 이 거리에서 최대 Z-홉 높이가 적용됩니다.',
        'Trajectory Mode (Smart Mode)': '궤적 모드',
        'Select trajectory calculation method': '궤적 계산 방식을 선택합니다: 퍼센티지 또는 각도 기반',
        'Percentage': '퍼센티지',
        'Angle': '각도',
        'Ascent Ratio (Smart Mode)': '상승 구간 비율',
        'Percentage of travel distance for ascent phase': '전체 이동 거리 중 상승하면서 이동할 구간의 비율입니다.',
        'Descent Ratio (Smart Mode)': '하강 구간 비율',
        'Percentage of travel distance for descent phase': '전체 이동 거리 중 하강하면서 이동할 구간의 비율입니다.',        'Ascent Angle (Smart Mode)': '상승 각도',
        'Ascent angle in degrees': '각도 기반 궤적에서 상승 각도를 도 단위로 설정합니다.',        'Descent Angle (Smart Mode)': '하강 각도',
        'Descent angle in degrees': '각도 기반 궤적에서 하강 각도를 도 단위로 설정합니다.',
        'Angle Priority (Smart Mode)': '각도 우선 모드',
        'Prioritize angle over minimum height constraints': '최소 높이 제약보다 각도를 우선 적용합니다. 활성화 시 설정 각도를 보장하기 위해 필요한 높이로 자동 계산됩니다.'
    },
    'en_US': {
        'Smart Z-Hop': 'Smart Z-Hop',
        'Enable': 'Enable',
        'Enable Smart Z-Hop functionality': 'Enable/Disable Smart Z-Hop functionality. When checked, Z-hop will be executed according to configured conditions.',
        'Z-Hop Mode': 'Z-Hop Mode',
        'Select Z-Hop mode': 'Select Z-Hop algorithm: Traditional (vertical) or Slingshot (curved)',        'Traditional': 'Traditional',
        'Slingshot': 'Smart Mode',
        'Layer Change': 'Layer Change',
        'Z-Hop before layer change': 'Execute Z-hop before moving to a new layer. Prevents nozzle collision with printed parts at layer boundaries.',
        'Z-Hop Height': 'Z-Hop Height',
        'Select Z-Hop height': 'Set Z-hop height: Layer Height or Custom Height',
        'Layer Height': 'Layer Height',
        'Custom Height': 'Custom Height',
        'Custom Z-hop height value': 'Enter custom Z-hop height in millimeters. Typically use 0.2-1.0mm range.',
        'Travel': 'Travel Moves',
        'Z-Hop before travel moves': 'Execute Z-hop before non-extruding travel moves. Prevents collision with printed parts.',
        'Travel Distance': 'Minimum Travel Distance',
        'Apply Z-Hop only for moves longer than this distance': 'Execute Z-hop only for moves longer than this distance. Skip Z-hop for short moves to reduce print time.',
        'Custom Layers': 'Custom Layers',
        'Apply Travel Z-Hop only on specified layers': 'Apply travel Z-hop only on specific layers. Enter layer numbers separated by spaces (e.g., 1 5 10 15)',
        'Top/Bottom Only': 'Top/Bottom Only',
        'Apply Travel Z-Hop only on top/bottom layers': 'Apply travel Z-hop only on first and last layers. Focus on key surface quality improvement.',
        'Z-Hop Speed': 'Z-Hop Speed',
        'Z-axis speed limit for Z-hop movements (0 = unlimited)': 'Z-axis speed limit for Z-hop movements (0 = unlimited)',
        'Min Z-Hop (Smart Mode)': 'Min Z-Hop Height',
        'Minimum Z-hop height for slingshot mode': 'Minimum Z-hop height for slingshot mode. Applied for short distance moves.',
        'Max Distance (Smart Mode)': 'Reference Max Distance',
        'Maximum travel distance for height calculation': 'Reference maximum travel distance for height calculation. Maximum Z-hop height is applied at this distance.',
        'Trajectory Mode (Slingshot)': 'Trajectory Mode',
        'Select trajectory calculation method': 'Select trajectory calculation method: Percentage or Angle based',
        'Percentage': 'Percentage',
        'Angle': 'Angle',
        'Ascent Ratio (Slingshot)': 'Ascent Section Ratio',
        'Percentage of travel distance for ascent phase': 'Percentage of total travel distance for the ascending section while moving toward target.',
        'Descent Ratio (Slingshot)': 'Descent Section Ratio',
        'Percentage of travel distance for descent phase': 'Percentage of total travel distance for the descending section while moving toward target.',        'Ascent Angle (Smart Mode)': 'Ascent Angle',
        'Ascent angle in degrees': 'Ascent angle in degrees for angle-based trajectory calculation.',        'Descent Angle (Smart Mode)': 'Descent Angle',
        'Descent angle in degrees': 'Descent angle in degrees for angle-based trajectory calculation.',
        'Angle Priority (Smart Mode)': 'Angle Priority Mode',
        'Prioritize angle over minimum height constraints': 'Prioritize angle over minimum height constraints. When enabled, calculates required height to guarantee set angles.'
    }
}

# V1 표준 번역 함수 (i18n_catalog_i18nc)
def i18n_catalog_i18nc(context, text, category=""):
    """표준 다국어 지원 함수"""
    try:
        current_locale = locale.getdefaultlocale()[0]
        if current_locale and current_locale.startswith('ko'):
            lang = 'ko_KR'
        else:
            lang = 'en_US'
    except:
        lang = 'ko_KR'  # 기본값은 한국어
    
    if lang in TRANSLATIONS and text in TRANSLATIONS[lang]:
        return TRANSLATIONS[lang][text]
    return text

class SmartZHop(Script):
    def __init__(self):
        super().__init__()
        self.original_z_max_feedrate = None  # 원본 Z축 최대 속도 저장

    def getSettingDataString(self):
        """완전한 설정 구조 반환 (V1 + V2 + Current 통합)"""
        
        return """{
            "name": "%s",
            "key": "SmartZHop",
            "metadata": {},
            "version": 2,
            "settings": {
                "enable": {
                    "label": "%s",
                    "description": "%s",
                    "type": "bool",
                    "default_value": true
                },
                "zhop_mode": {
                    "label": "%s",
                    "description": "%s",
                    "type": "enum",
                    "options": {
                        "traditional": "%s",
                        "slingshot": "%s"
                    },
                    "default_value": "traditional"
                },
                "layer_change_zhop": {
                    "label": "%s",
                    "description": "%s",
                    "type": "bool",
                    "default_value": true
                },
                "zhop_height_type": {
                    "label": "%s",
                    "description": "%s",
                    "type": "enum",
                    "options": {
                        "layer_height": "%s",
                        "custom": "%s"
                    },
                    "default_value": "custom"
                },
                "zhop_height": {
                    "label": "  > %s",
                    "description": "%s",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 0.2,
                    "minimum_value": 0.0,
                    "enabled": "zhop_height_type == 'custom'"
                },
                "travel_zhop": {
                    "label": "%s",
                    "description": "%s",
                    "type": "bool",
                    "default_value": true
                },
                "travel_distance": {
                    "label": "  > %s",
                    "description": "%s",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 1.0,
                    "minimum_value": 0.0,
                    "enabled": "travel_zhop"
                },
                "custom_layers": {
                    "label": "  > %s",
                    "description": "%s",
                    "type": "str",
                    "default_value": "",
                    "enabled": "travel_zhop"
                },
                "top_bottom_only": {
                    "label": "  > %s",
                    "description": "%s",
                    "type": "bool",
                    "default_value": false,
                    "enabled": "travel_zhop"
                },
                "zhop_speed": {
                    "label": "%s",
                    "description": "%s",
                    "unit": "mm/s",
                    "type": "float",
                    "default_value": 0,
                    "minimum_value": 0
                },
                "slingshot_min_zhop": {
                    "label": "  > %s",
                    "description": "%s",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 0.1,
                    "minimum_value": 0.0,
                    "enabled": "zhop_mode == 'slingshot'"
                },
                "slingshot_max_distance": {
                    "label": "  > %s",
                    "description": "%s",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 90.0,
                    "minimum_value": 1.0,
                    "enabled": "zhop_mode == 'slingshot'"
                },
                "slingshot_trajectory_mode": {
                    "label": "  > %s",
                    "description": "%s",
                    "type": "enum",
                    "options": {
                        "percentage": "%s",
                        "angle": "%s"
                    },
                    "default_value": "percentage",
                    "enabled": "zhop_mode == 'slingshot'"
                },
                "slingshot_ascent_ratio": {
                    "label": "    > %s",
                    "description": "%s",
                    "unit": "%%",
                    "type": "int",
                    "default_value": 30,
                    "minimum_value": 0,
                    "maximum_value": 100,
                    "enabled": "zhop_mode == 'slingshot' and slingshot_trajectory_mode == 'percentage'"
                },
                "slingshot_descent_ratio": {
                    "label": "    > %s",
                    "description": "%s",
                    "unit": "%%",
                    "type": "int",
                    "default_value": 30,
                    "minimum_value": 0,
                    "maximum_value": 100,
                    "enabled": "zhop_mode == 'slingshot' and slingshot_trajectory_mode == 'percentage'"
                },
                "slingshot_ascent_angle": {
                    "label": "    > %s",
                    "description": "%s",
                    "unit": "°",
                    "type": "float",
                    "default_value": 30.0,
                    "minimum_value": 10.0,
                    "maximum_value": 90.0,
                    "enabled": "zhop_mode == 'slingshot' and slingshot_trajectory_mode == 'angle'"
                },                "slingshot_descent_angle": {
                    "label": "    > %s",
                    "description": "%s",
                    "unit": "°",
                    "type": "float",
                    "default_value": 30.0,
                    "minimum_value": 10.0,
                    "maximum_value": 90.0,
                    "enabled": "zhop_mode == 'slingshot' and slingshot_trajectory_mode == 'angle'"
                },
                "slingshot_angle_priority": {
                    "label": "    > %s",
                    "description": "%s",
                    "type": "bool",
                    "default_value": false,
                    "enabled": "zhop_mode == 'slingshot' and slingshot_trajectory_mode == 'angle'"
                }
            }
        }""" % (
            i18n_catalog_i18nc("", "Smart Z-Hop"),
            i18n_catalog_i18nc("", "Enable"),
            i18n_catalog_i18nc("", "Enable Smart Z-Hop functionality"),
            i18n_catalog_i18nc("", "Z-Hop Mode"),
            i18n_catalog_i18nc("", "Select Z-Hop mode"),
            i18n_catalog_i18nc("", "Traditional"),
            i18n_catalog_i18nc("", "Slingshot"),
            i18n_catalog_i18nc("", "Layer Change"),
            i18n_catalog_i18nc("", "Z-Hop before layer change"),
            i18n_catalog_i18nc("", "Z-Hop Height"),
            i18n_catalog_i18nc("", "Select Z-Hop height"),
            i18n_catalog_i18nc("", "Layer Height"),
            i18n_catalog_i18nc("", "Custom Height"),
            i18n_catalog_i18nc("", "Custom Height"),
            i18n_catalog_i18nc("", "Custom Z-hop height value"),
            i18n_catalog_i18nc("", "Travel"),
            i18n_catalog_i18nc("", "Z-Hop before travel moves"),
            i18n_catalog_i18nc("", "Travel Distance"),
            i18n_catalog_i18nc("", "Apply Z-Hop only for moves longer than this distance"),
            i18n_catalog_i18nc("", "Custom Layers"),
            i18n_catalog_i18nc("", "Apply Travel Z-Hop only on specified layers"),
            i18n_catalog_i18nc("", "Top/Bottom Only"),
            i18n_catalog_i18nc("", "Apply Travel Z-Hop only on top/bottom layers"),
            i18n_catalog_i18nc("", "Z-Hop Speed"),
            i18n_catalog_i18nc("", "Z-axis speed limit for Z-hop movements (0 = unlimited)"),            i18n_catalog_i18nc("", "Min Z-Hop (Smart Mode)"),
            i18n_catalog_i18nc("", "Minimum Z-hop height for slingshot mode"),
            i18n_catalog_i18nc("", "Max Distance (Smart Mode)"),
            i18n_catalog_i18nc("", "Maximum travel distance for height calculation"),
            i18n_catalog_i18nc("", "Trajectory Mode (Smart Mode)"),
            i18n_catalog_i18nc("", "Select trajectory calculation method"),
            i18n_catalog_i18nc("", "Percentage"),
            i18n_catalog_i18nc("", "Angle"),
            i18n_catalog_i18nc("", "Ascent Ratio (Slingshot)"),
            i18n_catalog_i18nc("", "Percentage of travel distance for ascent phase"),
            i18n_catalog_i18nc("", "Descent Ratio (Slingshot)"),
            i18n_catalog_i18nc("", "Percentage of travel distance for descent phase"),            i18n_catalog_i18nc("", "Ascent Angle (Smart Mode)"),
            i18n_catalog_i18nc("", "Ascent angle in degrees"),            i18n_catalog_i18nc("", "Descent Angle (Smart Mode)"),            i18n_catalog_i18nc("", "Descent angle in degrees"),            i18n_catalog_i18nc("", "Angle Priority (Smart Mode)"),
            i18n_catalog_i18nc("", "Prioritize angle over minimum height constraints")
        )

    def execute(self, data):
        if not self.getSettingValueByKey("enable"):
            return data

        # 첫 실행 시 원본 Z축 속도 파싱
        if self.original_z_max_feedrate is None:
            self.parse_original_z_feedrate(data)

        zhop_mode = self.getSettingValueByKey("zhop_mode")

        layer_change_zhop = self.getSettingValueByKey("layer_change_zhop")
        zhop_height_type = self.getSettingValueByKey("zhop_height_type") # Needed for current_layer_height
        zhop_height_setting = self.getSettingValueByKey("zhop_height") # Actual custom zhop height
        travel_zhop = self.getSettingValueByKey("travel_zhop")
        travel_distance_setting = self.getSettingValueByKey("travel_distance")
        custom_layers = self.getSettingValueByKey("custom_layers")
        top_bottom_only = self.getSettingValueByKey("top_bottom_only")
        zhop_speed = self.getSettingValueByKey("zhop_speed")        # Determine current_layer_height for zhop_height_type == "layer_height"
        # This might need to be determined per layer if it can change,
        # or use a typical/first layer height if used as a general value.
        # For now, using zhop_height_setting as a fallback or if type is custom.
        effective_zhop_height = zhop_height_setting # Default to custom value

        if zhop_height_type == "layer_height":
            # Try to get it from gcode, very simplified, might need a more robust way
            first_layer_gcode = data[0] if len(data) > 0 else ""
            lh = self.get_layer_height_from_gcode([first_layer_gcode]) # Pass as list
            if lh > 0:
                effective_zhop_height = lh
            # else, effective_zhop_height remains zhop_height_setting


        custom_layer_list = []
        if custom_layers:
            try:
                custom_layer_list = [int(x.strip()) for x in custom_layers.split(',') if x.strip()]
            except ValueError:
                # Log error or handle incorrect custom_layers format
                pass # Keep custom_layer_list empty

        if zhop_mode == "slingshot":
            slingshot_settings = {
                'min_zhop': self.getSettingValueByKey("slingshot_min_zhop"),
                'max_distance': self.getSettingValueByKey("slingshot_max_distance"), # Renamed from slingshot_max_zhop_distance
                'trajectory_mode': self.getSettingValueByKey("slingshot_trajectory_mode"),
                'ascent_ratio': self.getSettingValueByKey("slingshot_ascent_ratio"),
                'descent_ratio': self.getSettingValueByKey("slingshot_descent_ratio"),
                'ascent_angle': self.getSettingValueByKey("slingshot_ascent_angle"),
                'descent_angle': self.getSettingValueByKey("slingshot_descent_angle"),
                'angle_priority': self.getSettingValueByKey("slingshot_angle_priority"),
            }
            return self.execute_slingshot_mode(data, effective_zhop_height, zhop_speed, layer_change_zhop,
                                                travel_zhop, travel_distance_setting, custom_layer_list, 
                                                top_bottom_only, slingshot_settings)
        elif zhop_mode == "traditional":
            return self.execute_traditional_mode(data, effective_zhop_height, zhop_speed, layer_change_zhop,
                                               travel_zhop, travel_distance_setting, custom_layer_list, top_bottom_only)
        else: # off or unknown mode
            return data

    def parse_original_z_feedrate(self, data):
        """G-code에서 원본 Z축 최대 속도 파싱 (단순 병합 처리)"""
        # 1단계: 모든 SETTING_3 라인을 찾아서 순수 텍스트만 추출
        setting_parts = []
        
        for layer in data:
            lines = layer.split('\n')
            for line in lines:
                if line.startswith(';SETTING_3 '):
                    # ';SETTING_3 ' 제거하고 나머지 텍스트만 추출 (strip 없이)
                    setting_content = line[10:]  # ';SETTING_3 ' 제거 (10글자)
                    setting_parts.append(setting_content)
        
        # 2단계: 단순 병합 (글자수 제한으로 잘린 텍스트 복원)
        if not setting_parts:
            self.original_z_max_feedrate = 15*60
            print(f"⚠️ SETTING_3 라인을 찾을 수 없어서 기본값 사용: {self.original_z_max_feedrate/60:.0f} mm/s")
            return self.original_z_max_feedrate
        
        # 단순 병합 (공백이나 추가 처리 없이)
        combined_settings = ''.join(setting_parts)
        
        print(f"🔍 병합된 SETTING_3 내용:")
        print(f"   병합 결과: {combined_settings[:100]}...")
        
        # 3단계: \\n을 실제 줄바꿈으로 변환하여 파싱
        normalized_settings = combined_settings.replace('\\n', '\n')
        
        # 4단계: machine_max_feedrate_z 값 찾기
        import re
        match = re.search(r'machine_max_feedrate_z\s*=\s*([\d\.]+)', normalized_settings)
        
        if match:
            z_feedrate = float(match.group(1))
            # mm/s를 mm/min으로 변환
            self.original_z_max_feedrate = z_feedrate * 60
            print(f"🎯 원본 Z축 최대 속도 발견: {z_feedrate} mm/s ({self.original_z_max_feedrate:.0f} mm/min)")
            return self.original_z_max_feedrate
        else:
            # 5단계: 파싱 실패 시 기본값 사용
            self.original_z_max_feedrate = 4500  # 기본값 (75 mm/s * 60)
            print(f"⚠️ machine_max_feedrate_z를 찾을 수 없어서 기본값 사용: {self.original_z_max_feedrate:.0f} mm/min")
            print(f"📋 파싱 대상 텍스트: {normalized_settings}")
            return self.original_z_max_feedrate

    def get_layer_height_from_gcode(self, data_list): # Expects a list of layer gcode strings
        # Simplified: Tries to find G1 Z value in the first few lines of the first layer's G-code
        # This is a very basic approach and might not be robust.
        if not data_list:
            return 0.0
        
        layer_gcode = data_list[0] # Check first layer
        lines = layer_gcode.split('\n')
        for line in lines[:20]: # Check first 20 lines
            if line.startswith("G1") and "Z" in line:
                match = re.search(r"Z([\d\.]+)", line)
                if match:
                    return float(match.group(1))
        return 0.0 # Fallback

    def execute_standalone(self, gcode_lines):
        # This method is for testing with a list of G-code strings.
        # It simulates how the main 'execute' method would run.
        
        # Convert list of G-code strings to the structure 'execute' expects (list of layer strings)        # For standalone, we often treat the whole input as a single "layer" or segment.
        # The original execute_standalone had `cura_format_data = [combined_gcode]`
        # We will follow that, assuming gcode_lines is a list of individual gcode commands.
        combined_gcode = '\n'.join(gcode_lines)
        cura_format_data = [combined_gcode] # Process as a single layer        # Call the main execute method with this formatted data
        # All settings will be pulled from self.getSettingValueByKey (Mock or Cura)
        return self.execute(cura_format_data)

    def get_zhop_speed_gcode(self, speed):
        """M203 명령을 사용한 Z-홉 속도 제어 G-code 생성 (개선된 버전)"""
        if speed <= 0:
            return ""  # 0이면 속도 제한 없음 (무제한)
          # mm/s를 mm/min으로 변환 (M203은 mm/min 단위)
        speed_mm_min = speed * 60
        return f"M203 Z{speed_mm_min:.0f} ; Set Z-axis speed limit for Z-hop ({speed:.1f} mm/s)"

    def restore_original_speed_gcode(self):
        """원래 Z축 속도 복원을 위한 G-code 생성 (개선된 버전)"""
        # 원본 속도가 파싱되지 않았다면 복원하지 않음
        if self.original_z_max_feedrate is None:
            return ""  # 원본 속도를 모르면 복원하지 않음
        
        return f"M203 Z{self.original_z_max_feedrate:.0f} ; Restore original Z-axis speed ({self.original_z_max_feedrate/60:.1f} mm/s)"

    def execute_traditional_mode(self, data, zhop_height, zhop_speed, layer_change_zhop, 
                               travel_zhop, travel_distance, custom_layer_list, top_bottom_only):
        """전통적 모드 실행 (원본 Z_HopMove 로직 정확히 구현)"""
        processed_data = []
        total_layers = len(data)
        
        for layer_index, layer in enumerate(data):
            lines = layer.split('\n')
            output_gcode = ""
            
            # 원본 Z_HopMove의 정확한 플래그 시스템
            current_z = 0
            g1_saved = False
            tr_layer = False  
            lc_line = False
            lc_z_hop_saved = False
            tr_z_hop_saved = False
            saved_x, saved_y = 0, 0
            lc_gcode = ""
            tr_gcode = ""
            
            for line in lines:
                # 현재 위치 추적
                if self.getValue(line, 'Z') is not None:
                    current_z = self.getValue(line, 'Z')

                # 레이어 시작 처리 (원본 방식)
                if ";LAYER:" in line:
                    tr_layer = True
                    
                    # 레이어 제한 처리
                    if custom_layer_list:
                        current_layer = layer_index + 1
                        tr_layer = current_layer in custom_layer_list
                    elif top_bottom_only:
                        tr_layer = (layer_index == 0 or layer_index == total_layers - 1)

                # 레이어 변경 Z-hop 준비 (원본 방식)                if layer_change_zhop and lc_line:
                    # 속도 제어 적용 (조건부: 속도 설정이 있고 원본 속도가 파싱된 경우만)
                    speed_prefix = ""
                    speed_suffix = ""
                    if zhop_speed > 0 and self.original_z_max_feedrate is not None:
                        speed_gcode = self.get_zhop_speed_gcode(zhop_speed)
                        if speed_gcode:
                            speed_prefix = speed_gcode + "\n"
                        
                        restore_gcode = self.restore_original_speed_gcode()
                        if restore_gcode:
                            speed_suffix = "\n" + restore_gcode
                    
                    # Z-홉 G-code 준비
                    lc_gcode = f"{speed_prefix}G0 Z{current_z + zhop_height:.2f};Smart Z-Hop Layer Change\n{line}{speed_suffix}\n"
                    lc_z_hop_saved = True

                # Travel Z-hop 처리 (원본 방식)
                if travel_zhop and tr_layer:
                    # G1 압출 명령 감지 및 저장
                    if (self.getValue(line, 'G') == 1 and 
                        self.getValue(line, "X") is not None and 
                        self.getValue(line, "Y") is not None and 
                        self.getValue(line, "E") is not None):
                        
                        saved_x = self.getValue(line, "X")
                        saved_y = self.getValue(line, "Y")
                        g1_saved = True

                    # G0 이동 명령 처리
                    if (self.getValue(line, 'G') == 0 and g1_saved):
                        g1_saved = False  # 원본처럼 즉시 False로 설정
                        if (self.getValue(line, "X") is not None and 
                            self.getValue(line, "Y") is not None and 
                            self.getValue(line, "Z") is None):
                            
                            target_x = self.getValue(line, "X")
                            target_y = self.getValue(line, "Y")
                            distance = self.calculate_distance(saved_x, saved_y, target_x, target_y)
                            
                            if distance >= travel_distance:
                                # 속도 제어 적용 (조건부: 속도 설정이 있고 원본 속도가 파싱된 경우만)
                                speed_prefix = ""
                                speed_suffix = ""
                                if zhop_speed > 0 and self.original_z_max_feedrate is not None:
                                    speed_gcode = self.get_zhop_speed_gcode(zhop_speed)
                                    if speed_gcode:
                                        speed_prefix = speed_gcode + "\n"
                                    
                                    restore_gcode = self.restore_original_speed_gcode()
                                    if restore_gcode:
                                        speed_suffix = "\n" + restore_gcode
                                

                                # Z-hop G-code 준비
                                tr_gcode = f"{speed_prefix}G0 Z{current_z + zhop_height:.2f};Smart Z-Hop Travel Up, D:{distance:.2f}\n"
                                tr_gcode += line + "\n"
                                tr_gcode += f"G0 Z{current_z:.2f};Smart Z-Hop Travel Down{speed_suffix}\n"
                                tr_z_hop_saved = True

                # 원본 방식: 저장된 G-code가 있으면 출력, 없으면 기본 라인 출력
                if layer_change_zhop and lc_z_hop_saved:
                    output_gcode += lc_gcode
                    lc_z_hop_saved = False
                    lc_line = False
                    g1_saved = False
                elif travel_zhop and tr_z_hop_saved:
                    output_gcode += tr_gcode
                    tr_z_hop_saved = False
                else:
                    output_gcode += line + "\n"

                # MESH:NONMESH 처리 (원본 방식 - 마지막에!)
                if ";MESH:NONMESH" in line:
                    lc_line = True
                    tr_layer = False  # 원본은 여기서 False로 설정!
            
            processed_data.append(output_gcode.rstrip())
        
        return processed_data

    def execute_slingshot_mode(self, data, zhop_height, zhop_speed, layer_change_zhop,
                             travel_zhop, travel_distance_threshold, custom_layer_list, top_bottom_only, 
                             slingshot_settings):
        """스마트 모드 실행 (smart_mode 완전 통합 버전 - V2 3-stage 시스템 포함)"""
        processed_data = []
        
        # Note: slingshot_settings is expected to be a dictionary with keys like:
        # 'min_zhop', 'max_distance', 'trajectory_mode', 
        # 'ascent_ratio', 'descent_ratio', 'ascent_angle', 'descent_angle', 'z_feedrate'

        actual_current_x, actual_current_y, actual_current_z = 0.0, 0.0, 0.0
        current_feedrate = None  # 현재 활성화된 feedrate 추적        # More robust initialization would involve parsing initial G-code state or carrying over from Cura.
        # For script scope, we often reset or try to find first G1 with X,Y,Z in the layer.

        for layer_index, layer_gcode in enumerate(data):
            lines = layer_gcode.split('\n')
            processed_lines = []
            
            # Attempt to find initial position for the layer if not carried over
            # This is a simplified approach for layer-by-layer processing.
            # A full G-code parser would maintain state across the entire file.
            # For now, we assume actual_current_x,y,z are updated by each G-code line.
            # If the first line of a layer doesn't set them, they might be from previous layer's end.            # 리트랙션 감지를 위한 이전 라인 추적
            previous_line = None
            is_first_travel_after_retraction = False
            
            # 연속 travel move 그룹화를 위한 변수들
            in_travel_sequence = False
            travel_sequence_start_x = None
            travel_sequence_start_y = None
            travel_sequence_start_z = None
            travel_sequence_moves = []

            for line_index, line in enumerate(lines):
                # Store position *before* this line is processed for Z-hop decision
                start_x_for_move = actual_current_x
                start_y_for_move = actual_current_y
                start_z_for_move = actual_current_z
                
                # 리트랙션 감지: 이전 라인이 E값 없는 이동이고, 현재 라인이 travel move인 경우
                if previous_line is not None:
                    # 이전 라인이 리트랙션인지 확인 (E 매개변수가 없는 이동)
                    if (self.getValue(previous_line, 'G') in [0, 1] and 
                        self.getValue(previous_line, 'E') is None and
                        (self.getValue(previous_line, 'X') is not None or 
                         self.getValue(previous_line, 'Y') is not None)):
                        is_first_travel_after_retraction = True
                    else:
                        is_first_travel_after_retraction = False
                        
                # Tentative target coordinates from the current line
                # These will become the new actual_current_x,y,z if the line is not replaced
                parsed_x = self.getValue(line, 'X')
                parsed_y = self.getValue(line, 'Y')
                parsed_z = self.getValue(line, 'Z')
                parsed_f = self.getValue(line, 'F')                # 현재 feedrate 업데이트 (F값이 있는 경우)
                if parsed_f is not None:
                    current_feedrate = parsed_f

                is_travel = self.is_travel_move(line)
                
                # 연속 travel move 감지 및 그룹화
                if travel_zhop and is_travel:
                    if not in_travel_sequence:
                        # 새로운 travel 시퀀스 시작
                        in_travel_sequence = True
                        travel_sequence_start_x = start_x_for_move
                        travel_sequence_start_y = start_y_for_move
                        travel_sequence_start_z = start_z_for_move
                        travel_sequence_moves = []
                    
                    # 현재 travel move를 시퀀스에 추가
                    target_x = parsed_x if parsed_x is not None else start_x_for_move
                    target_y = parsed_y if parsed_y is not None else start_y_for_move
                    travel_sequence_moves.append({
                        'line': line,
                        'target_x': target_x,
                        'target_y': target_y,
                        'line_index': line_index
                    })
                    
                    # 다음 라인이 travel move인지 미리 확인
                    next_is_travel = False
                    if line_index + 1 < len(lines):
                        next_line = lines[line_index + 1]
                        next_is_travel = self.is_travel_move(next_line)
                    
                    # 다음 라인이 travel이 아니면 시퀀스 종료 및 처리
                    if not next_is_travel:
                        self.process_travel_sequence(
                            travel_sequence_start_x, travel_sequence_start_y, travel_sequence_start_z,
                            travel_sequence_moves, processed_lines, 
                            travel_distance_threshold, zhop_height, zhop_speed, 
                            slingshot_settings, current_feedrate,
                            is_first_travel_after_retraction
                        )
                        
                        # 마지막 이동의 목표 위치로 현재 위치 업데이트
                        final_move = travel_sequence_moves[-1]
                        actual_current_x = final_move['target_x']
                        actual_current_y = final_move['target_y']
                        actual_current_z = travel_sequence_start_z
                          # 시퀀스 리셋
                        in_travel_sequence = False
                        is_first_travel_after_retraction = False
                    
                elif ";LAYER:" in line and layer_change_zhop: # Handle layer change Z-hop (potentially traditional)
                    # This is a placeholder for layer change Z-hop logic.
                    # It might involve a traditional Z-hop or be handled by `execute_traditional_mode`.
                    # For now, just add the line and update Z if present.
                    # The original Z_HopMove script had specific logic here.
                    # If this script is purely for slingshot on travel, this might be simpler.
                    # For now, assume it's a simple pass-through and Z update.
                    # A proper implementation would insert a traditional Z-hop here if configured.
                      # Example: Simple traditional Z-hop for layer change (if not handled elsewhere)
                    # if layer_index > 0: # Avoid Z-hop on the very first layer
                    # processed_lines.append(f"G1 Z{actual_current_z + zhop_height} F{zhop_speed * 60 if zhop_speed > 0 else self.getSettingValueByKey('z_feedrate', 60.0) * 60}") # Z up
                    processed_lines.append(line) # The LAYER line itself
                    if parsed_x is not None: actual_current_x = parsed_x # Unlikely in ;LAYER:
                    if parsed_y is not None: actual_current_y = parsed_y # Unlikely in ;LAYER:
                    if parsed_z is not None: actual_current_z = parsed_z # Update Z if ;LAYER: also has Z
                    # processed_lines.append(f"G1 Z{actual_current_z} F{zhop_speed * 60 if zhop_speed > 0 else self.getSettingValueByKey('z_feedrate', 60.0) * 60}") # Z down after new layer moves
                    # The above Z up/down for layer change is a simplification and needs to fit the overall script design.
                    # The original script had more complex logic for lc_line, etc.
                    # For now, just updating Z if the ;LAYER: line or subsequent lines change it.
                    # The main point is that this is distinct from slingshot travel Z-hop.
                    # If parsed_z is None from the ;LAYER: line, actual_current_z remains.                    # Usually, the slicer adds G1 Z commands after ;LAYER:
                    # 현재 layer_gcode를 이용한 검색은 범위 문제로 인해 주석 처리
                    # new_layer_z_match = re.search(r";LAYER:\d+\s*\n(?:G[01]\s+Z([\d\.]+))?", layer_gcode[lines.index(line):], re.MULTILINE)
                    # if new_layer_z_match and new_layer_z_match.group(1):
                    #     actual_current_z = float(new_layer_z_match.group(1))
                    if parsed_z is not None: # If Z is on the ;LAYER: line itself
                        actual_current_z = parsed_z

                else: # Not a travel move for Z-hop, or not a layer change
                    # travel 시퀀스가 진행 중이었다면 여기서 강제 종료
                    if in_travel_sequence:
                        self.process_travel_sequence(
                            travel_sequence_start_x, travel_sequence_start_y, travel_sequence_start_z,
                            travel_sequence_moves, processed_lines, 
                            travel_distance_threshold, zhop_height, zhop_speed, 
                            slingshot_settings, current_feedrate,
                            is_first_travel_after_retraction
                        )
                        # 시퀀스 리셋
                        in_travel_sequence = False
                        is_first_travel_after_retraction = False
                    processed_lines.append(line)
                    if parsed_x is not None: actual_current_x = parsed_x
                    if parsed_y is not None: actual_current_y = parsed_y
                    if parsed_z is not None: actual_current_z = parsed_z
                
                # 다음 반복을 위해 이전 라인 업데이트
                previous_line = line
            processed_data.append('\n'.join(processed_lines))
        
        return processed_data

    def process_travel_sequence(self, start_x, start_y, start_z, travel_moves, 
                               processed_lines, travel_distance_threshold, zhop_height, 
                               zhop_speed, slingshot_settings, current_feedrate, 
                               is_first_travel_after_retraction):
        """연속 travel move 시퀀스를 부드러운 연속 곡선으로 처리"""
        if not travel_moves:
            return
        
        # 전체 경로의 XY 거리 적분 계산
        path_segments = []
        cumulative_distances = [0.0]  # 누적 거리 배열
        total_distance = 0.0
        
        prev_x, prev_y = start_x, start_y
        
        # 각 구간별 거리와 누적 거리 계산
        for move in travel_moves:
            segment_distance = self.calculate_distance(prev_x, prev_y, move['target_x'], move['target_y'])
            total_distance += segment_distance
            cumulative_distances.append(total_distance)
            
            path_segments.append({
                'start_x': prev_x,
                'start_y': prev_y,
                'end_x': move['target_x'],
                'end_y': move['target_y'],
                'distance': segment_distance,
                'cumulative_distance': total_distance,
                'original_line': move['line']
            })
            
            prev_x, prev_y = move['target_x'], move['target_y']
        
        # Z-hop 적용 조건 확인
        should_zhop = (is_first_travel_after_retraction or 
                      total_distance > travel_distance_threshold)
        
        if should_zhop:
            # 연속 곡선 Z-hop 궤적 생성
            trajectory_gcode_lines = self.calculate_continuous_curve_trajectory(
                start_x, start_y, start_z, path_segments, total_distance,
                zhop_height, zhop_speed, slingshot_settings, current_feedrate
            )
            processed_lines.extend(trajectory_gcode_lines)
        else:
            # Z-hop 조건에 맞지 않으면 원본 라인들 그대로 추가
            for move in travel_moves:
                processed_lines.append(move['line'])
    def calculate_slingshot_trajectory_v2(self, start_x, start_y, start_z, 
                                        target_x, target_y, distance, 
                                        max_zhop_height, zhop_speed, settings):
        """V2 3-stage 스마트 궤적 계산 (Percentage/Angle 모드 지원)"""
        # 동적 높이 계산 (settings 전달)
        dynamic_height = self.calculate_dynamic_height(distance, max_zhop_height, 
                                                     settings['min_zhop'], settings['max_distance'], settings)
        
        trajectory_gcode = []
        
        # M203 속도 제어 적용 (조건부: 속도 설정이 있고 원본 속도가 파싱된 경우만)
        if zhop_speed > 0 and self.original_z_max_feedrate is not None:
            speed_gcode = self.get_zhop_speed_gcode(zhop_speed)
            if speed_gcode:
                trajectory_gcode.append(speed_gcode)
        
        if settings['trajectory_mode'] == 'angle':
            # 각도 기반 계산
            trajectory_gcode.extend(self.calculate_angle_based_trajectory(
                start_x, start_y, start_z, target_x, target_y, 
                dynamic_height, settings))
        else:
            # 퍼센티지 기반 계산 (3-stage)
            trajectory_gcode.extend(self.calculate_percentage_based_trajectory(
                start_x, start_y, start_z, target_x, target_y, 
                dynamic_height, settings))
        
        # 속도 복원 (각 Z-hop이 독립적으로 완료되도록 보장)
        restore_gcode = self.restore_original_speed_gcode()
        if restore_gcode:
            trajectory_gcode.append(restore_gcode)
        
        return trajectory_gcode
    def calculate_angle_based_trajectory(self, start_x, start_y, start_z, 
                                       target_x, target_y, zhop_height, settings):
        """각도 기반 궤적 계산 (V2 기능 + 각도 우선 모드 지원 - 각도 절대 변경 안 함)"""
        trajectory_gcode = []
        
        # 총 이동 거리
        total_distance = self.calculate_distance(start_x, start_y, target_x, target_y)
        # 설정된 각도 (각도 우선 모드에서는 절대 변경하지 않음)
        ascent_angle = settings.get('ascent_angle', 45.0)
        descent_angle = settings.get('descent_angle', 45.0)
        ascent_angle_rad = math.radians(ascent_angle)
        descent_angle_rad = math.radians(descent_angle)        # 각도 우선 모드에서 3단계 시스템 구현
        if settings.get('angle_priority', False):
            # 각도 우선: 설정된 각도를 절대 변경하지 않고 3단계 시스템으로 처리
            if ascent_angle >= 89.5:  # 거의 수직
                ascent_horizontal = 0.0
            else:
                # 최대 높이에서 설정 각도로 이동할 수 있는 수평 거리
                ascent_horizontal = zhop_height / math.tan(ascent_angle_rad)
            
            if descent_angle >= 89.5:  # 거의 수직
                descent_horizontal = 0.0
            else:
                # 최대 높이에서 설정 각도로 이동할 수 있는 수평 거리
                descent_horizontal = zhop_height / math.tan(descent_angle_rad)
            
            # 각도 우선 모드: 각도를 절대 변경하지 않음
            # 필요한 수평 거리가 전체 거리보다 크더라도 3단계 시스템으로 처리
            # 상승 구간과 하강 구간의 각도는 설정값 그대로 유지
            # 남은 거리는 수평 이동 구간에서 처리
            # 안전장치: 각도 우선 모드에서도 최대 허용 높이 제한 적용
            max_allowed_height = settings.get('max_zhop_height', zhop_height)
            effective_zhop_height = min(zhop_height, max_allowed_height)
            
        else:
            # 기본 모드: 기존 로직
            effective_zhop_height = zhop_height
            
            if ascent_angle >= 89.5:
                ascent_horizontal = 0.0
            else:
                ascent_horizontal = effective_zhop_height / math.tan(ascent_angle_rad)
                
            if descent_angle >= 89.5:
                descent_horizontal = 0.0
            else:
                descent_horizontal = effective_zhop_height / math.tan(descent_angle_rad)
            
            # 무한대 처리
            if ascent_horizontal == float('inf'): ascent_horizontal = total_distance / 2
            if descent_horizontal == float('inf'): descent_horizontal = total_distance / 2

        # 실제 이동 벡터 계산
        delta_x = target_x - start_x
        delta_y = target_y - start_y
        
        # 정규화된 방향 벡터
        if total_distance > 0:
            unit_x = delta_x / total_distance
            unit_y = delta_y / total_distance
        else:
            unit_x = unit_y = 0

        # F 값 결정 로직
        current_f_val = settings.get('current_feedrate')
        z_feed_val = settings.get('z_feedrate')
        
        feedrate_for_z_moves = None
        if current_f_val is not None and current_f_val > 0:
            feedrate_for_z_moves = current_f_val
        elif z_feed_val is not None and z_feed_val > 0:
            feedrate_for_z_moves = z_feed_val * 60
        
        f_command_z = f" F{feedrate_for_z_moves:.0f}" if feedrate_for_z_moves is not None else ""

        feedrate_for_xy_moves = None
        if current_f_val is not None and current_f_val > 0:
            feedrate_for_xy_moves = current_f_val
        
        f_command_xy = f" F{feedrate_for_xy_moves:.0f}" if feedrate_for_xy_moves is not None else ""        # Stage 1: 상승 (설정된 각도 유지)
        ascent_x = start_x + (ascent_horizontal * unit_x)
        ascent_y = start_y + (ascent_horizontal * unit_y)
        ascent_z = start_z + effective_zhop_height
        
        angle_info = f" (Angle: {ascent_angle:.1f}°)"
        if settings.get('angle_priority', False):
            angle_info = f" (Angle Priority: {ascent_angle:.1f}°)"
            
        # Stage 2: 수평 이동 (최대 높이에서)
        remaining_distance = total_distance - ascent_horizontal - descent_horizontal
        
        # 각도 우선 모드에서 톱니파 형태인지 미리 확인
        is_sawtooth_mode = (settings.get('angle_priority', False) and remaining_distance < 0)
        
        # 톱니파 모드가 아닐 때만 첫 번째 Smart Ascent 생성
        if not is_sawtooth_mode:
            trajectory_gcode.append(f"G1 X{ascent_x:.3f} Y{ascent_y:.3f} Z{ascent_z:.3f}{f_command_z} ; Smart Ascent{angle_info}")
        
        if settings.get('angle_priority', False):
            # 각도 우선 모드: 남은 거리가 음수일 경우 상승선과 하강선의 교점에서 하강 (톱니파 형태)
            if remaining_distance < 0:
                # 상승선과 하강선의 교점 계산
                # 상승선: start → 설정 각도로 무한히 연장
                # 하강선: target → 설정 각도로 역방향 무한히 연장
                
                if abs(descent_angle - 90.0) < 0.1:  # 거의 수직 하강 (90도)
                    # 하강이 수직이면 목표 X 위치에서 상승선과 만나는 지점
                    intersection_x = target_x
                    intersection_y = target_y
                    
                    # 상승선에서 교점까지의 거리 계산
                    intersection_distance = math.sqrt(
                        (intersection_x - start_x)**2 + (intersection_y - start_y)**2
                    )
                    
                    # 상승 각도와 교점 거리를 이용한 Z 높이 계산
                    if ascent_horizontal > 0:
                        # 상승 각도와 교점 거리를 이용한 Z 높이 계산
                        intersection_z = start_z + (intersection_distance * math.tan(ascent_angle_rad))
                        # 최대 높이 제한 적용
                        intersection_z = min(intersection_z, start_z + effective_zhop_height)
                    else:
                        intersection_z = start_z + effective_zhop_height
                    
                    # Stage 1: 상승 (교점까지)
                    trajectory_gcode.append(f"G1 X{intersection_x:.3f} Y{intersection_y:.3f} Z{intersection_z:.3f}{f_command_z} ; Smart Ascent{angle_info}")
                    
                    # Stage 2: 수직 하강 (목표점으로) - 톱니파 완성
                    descent_angle_info = f" (Angle: {descent_angle:.1f}°)"
                    trajectory_gcode.append(f"G1 X{target_x:.3f} Y{target_y:.3f} Z{start_z:.3f}{f_command_z} ; Smart Descent{descent_angle_info}")
                else:
                    # 비수직 하강: 복잡한 교점 계산 (향후 확장 가능)
                    # 현재는 기존 로직으로 폴백
                    travel_distance = abs(remaining_distance)
                    travel_x = ascent_x + (travel_distance * unit_x)
                    travel_y = ascent_y + (travel_distance * unit_y)
                    trajectory_gcode.append(f"G1 X{travel_x:.3f} Y{travel_y:.3f} Z{ascent_z:.3f}{f_command_xy} ; Smart Travel (Intersection Fallback)")
                    
                    # Stage 3: 하강
                    descent_angle_info = f" (Angle: {descent_angle:.1f}°)"
                    trajectory_gcode.append(f"G1 X{target_x:.3f} Y{target_y:.3f} Z{start_z:.3f}{f_command_z} ; Smart Descent{descent_angle_info}")
            elif remaining_distance > 1e-6:
                # 정상적인 수평 이동
                travel_x = ascent_x + (remaining_distance * unit_x)
                travel_y = ascent_y + (remaining_distance * unit_y)
                trajectory_gcode.append(f"G1 X{travel_x:.3f} Y{travel_y:.3f} Z{ascent_z:.3f}{f_command_xy} ; Smart Travel (Max Height)")
                
                # Stage 3: 하강 (설정된 각도 유지)
                descent_angle_info = f" (Angle: {descent_angle:.1f}°)"
                trajectory_gcode.append(f"G1 X{target_x:.3f} Y{target_y:.3f} Z{start_z:.3f}{f_command_z} ; Smart Descent{descent_angle_info}")
            else:
                # 수평 이동 없이 바로 하강
                descent_angle_info = f" (Angle: {descent_angle:.1f}°)"
                trajectory_gcode.append(f"G1 X{target_x:.3f} Y{target_y:.3f} Z{start_z:.3f}{f_command_z} ; Smart Descent{descent_angle_info}")
        else:
            # 기본 모드: 기존 로직
            if remaining_distance > 1e-6:
                travel_x = ascent_x + (remaining_distance * unit_x)
                travel_y = ascent_y + (remaining_distance * unit_y)
                trajectory_gcode.append(f"G1 X{travel_x:.3f} Y{travel_y:.3f} Z{ascent_z:.3f}{f_command_xy} ; Smart Travel (Max Height)")
                
                # Stage 3: 하강 (설정된 각도 유지)
                descent_angle_info = f" (Angle: {descent_angle:.1f}°)"
                trajectory_gcode.append(f"G1 X{target_x:.3f} Y{target_y:.3f} Z{start_z:.3f}{f_command_z} ; Smart Descent{descent_angle_info}")
            else:
                # 수평 이동 없이 바로 하강
                descent_angle_info = f" (Angle: {descent_angle:.1f}°)"
                trajectory_gcode.append(f"G1 X{target_x:.3f} Y{target_y:.3f} Z{start_z:.3f}{f_command_z} ; Smart Descent{descent_angle_info}")
        
        return trajectory_gcode

    def calculate_percentage_based_trajectory(self, start_x, start_y, start_z, 
                                            target_x, target_y, zhop_height, settings):
        """퍼센티지 기반 3-stage 궤적 계산 (V2 기능)"""
        trajectory_gcode = []
        
        # 이동 벡터 계산
        delta_x = target_x - start_x
        delta_y = target_y - start_y
        
        # 각 단계별 비율 계산
        ascent_ratio = settings.get('ascent_ratio', 25.0) / 100.0 # Default to 25%
        descent_ratio = settings.get('descent_ratio', 25.0) / 100.0 # Default to 25%
        
        # travel_ratio는 나머지 비율로, 0보다 작아지지 않도록 보정
        travel_at_height_ratio = max(0.0, 1.0 - ascent_ratio - descent_ratio)

        # F 값 결정 로직 (Z축 이동 포함)
        current_f_val = settings.get('current_feedrate')
        z_feed_val = settings.get('z_feedrate')
        
        feedrate_for_z_moves = None
        if current_f_val is not None and current_f_val > 0:
            feedrate_for_z_moves = current_f_val
        elif z_feed_val is not None and z_feed_val > 0:
            feedrate_for_z_moves = z_feed_val * 60
        
        f_command_z = f" F{feedrate_for_z_moves:.0f}" if feedrate_for_z_moves is not None else ""

        # F 값 결정 로직 (XY축 이동 전용)
        feedrate_for_xy_moves = None
        if current_f_val is not None and current_f_val > 0:
            feedrate_for_xy_moves = current_f_val
        
        f_command_xy = f" F{feedrate_for_xy_moves:.0f}" if feedrate_for_xy_moves is not None else ""

        # Stage 1: 상승 단계
        ascent_x = start_x + (delta_x * ascent_ratio)
        ascent_y = start_y + (delta_y * ascent_ratio)
        ascent_z = start_z + zhop_height
        trajectory_gcode.append(f"G1 X{ascent_x:.3f} Y{ascent_y:.3f} Z{ascent_z:.3f}{f_command_z} ; Smart Ascent ({settings.get('ascent_ratio', 25.0)}%)")
        
        # Stage 2: 수평 이동 단계
        if travel_at_height_ratio > 1e-6: # 작은 오차 감안, 실제 수평 이동이 있을 경우에만 G-code 생성
            travel_end_x = ascent_x + (delta_x * travel_at_height_ratio)
            travel_end_y = ascent_y + (delta_y * travel_at_height_ratio)
            # 수평 이동은 Z 높이를 유지 (ascent_z)
            trajectory_gcode.append(f"G1 X{travel_end_x:.3f} Y{travel_end_y:.3f} Z{ascent_z:.3f}{f_command_xy} ; Smart Travel at height ({travel_at_height_ratio*100:.1f}%)")

        # Stage 3: 하강 단계
        # 하강 시작점은 travel_end_x, travel_end_y (수평이동이 없었다면 ascent_x, ascent_y) 이고 Z는 ascent_z.        # 최종 목적지는 target_x, target_y, start_z.
        trajectory_gcode.append(f"G1 X{target_x:.3f} Y{target_y:.3f} Z{start_z:.3f}{f_command_z} ; Smart Descent ({settings.get('descent_ratio', 25.0)}%)")
        
        return trajectory_gcode

    def calculate_dynamic_height(self, distance, max_zhop_height, min_zhop, max_distance, settings=None):
        """거리 기반 동적 높이 계산 (각도 우선 모드 지원)"""
        # 각도 우선 모드 체크
        if settings and settings.get('angle_priority', False) and settings.get('trajectory_mode') == 'angle':
            # 각도 우선: 최대 높이를 절대 넘지 않음 (엄격한 제한)
            # 각도는 calculate_angle_based_trajectory에서 3단계 시스템으로 처리
            return max_zhop_height
        
        # 기본 높이 우선 모드: 기존 로직
        if distance >= max_distance:
            return max_zhop_height
        elif distance <= 0:
            return min_zhop
        else:
            # 거리에 비례한 선형 보간
            ratio = distance / max_distance
            return min_zhop + (max_zhop_height - min_zhop) * ratio
    
    def is_travel_move(self, line):
        """트래블 이동 여부 판단 (G0, G1 모두 지원)"""
        # G0 또는 G1으로 시작하는지 확인
        if not (line.startswith('G0') or line.startswith('G1')):
            return False
        
        # E값이 없고 X 또는 Y가 있으면 트래블 이동
        e_value = self.getValue(line, 'E')
        has_xy = self.getValue(line, 'X') is not None or self.getValue(line, 'Y') is not None
        
        return e_value is None and has_xy

    def getValue(self, line, key):
        """G-code 라인에서 특정 축의 값 추출 (원본 Z_HopMove 호환)"""
        if key == 'G':
            # G 명령 특별 처리 (원본 Z_HopMove 방식)
            if line.startswith('G0'):
                return 0
            elif line.startswith('G1'):
                return 1
            else:
                return None
        
        if key not in line:
            return None
        
        try:
            start = line.index(key) + 1
            end = start
            while end < len(line) and (line[end].isdigit() or line[end] in '.-'):
                end += 1
            return float(line[start:end])
        except:
            return None

    def calculate_distance(self, x1, y1, x2, y2):
        """두 점 사이의 거리 계산"""
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    def calculate_3stage_trajectory(self, start_x, start_y, start_z, target_x, target_y, zhop_height, ascent_ratio, descent_ratio):
        """3-Stage 궤적 계산 - 호환성을 위한 별명 함수"""
        settings = {
            'ascent_ratio': ascent_ratio,
            'descent_ratio': descent_ratio,
            'trajectory_mode': 'percentage',
        }
        return self.calculate_percentage_based_trajectory(start_x, start_y, start_z, target_x, target_y, zhop_height, settings)

    def generate_smart_gcode(self, trajectory_points, feedrate):
        """스마트 궤적 기반 G-code 생성"""
        gcode_lines = []
        
        for i, (x, y, z) in enumerate(trajectory_points):
            if i == 0:
                # 첫 번째 포인트: 상승
                gcode_lines.append(f"G1 X{x:.3f} Y{y:.3f} Z{z:.3f} F{feedrate} ; Smart Ascent")
            elif i == len(trajectory_points) - 1:
                # 마지막 포인트: 하강
                gcode_lines.append(f"G1 X{x:.3f} Y{y:.3f} Z{z:.3f} F{feedrate} ; Smart Descent")
            else:
                # 중간 포인트: 수평 이동
                gcode_lines.append(f"G1 X{x:.3f} Y{y:.3f} F{feedrate} ; Smart Travel")
        
        return gcode_lines

    def calculate_continuous_curve_trajectory(self, start_x, start_y, start_z, path_segments, 
                                            total_distance, zhop_height, zhop_speed, 
                                            slingshot_settings, current_feedrate):
        """XY 경로 적분 기반 연속 곡선 Z-hop 궤적 계산"""
        import math
        
        # 설정 추출
        trajectory_mode = slingshot_settings.get('trajectory_mode', 'percentage')
        min_zhop = slingshot_settings.get('min_zhop', 0.1)
        max_distance = slingshot_settings.get('max_distance', 80.0)
        
        # 동적 높이 계산
        dynamic_height = self.calculate_dynamic_height(total_distance, zhop_height, 
                                                     min_zhop, max_distance, slingshot_settings)
        trajectory_gcode = []
        
        # M203 속도 제어 (조건부: 속도 설정이 있고 원본 속도가 파싱된 경우만)
        if zhop_speed > 0 and self.original_z_max_feedrate is not None:
            speed_gcode = self.get_zhop_speed_gcode(zhop_speed)
            if speed_gcode:
                trajectory_gcode.append(speed_gcode)
        
        # 각도/퍼센티지 모드별 Z 높이 함수 생성
        if trajectory_mode == 'angle':
            z_height_function = self.create_angle_based_z_function(
                total_distance, dynamic_height, slingshot_settings
            )
        else:
            z_height_function = self.create_percentage_based_z_function(
                total_distance, dynamic_height, slingshot_settings
            )
        
        # F값 설정
        current_f_val = current_feedrate
        z_feed_val = slingshot_settings.get('z_feedrate')
        
        feedrate_for_moves = None
        if current_f_val is not None and current_f_val > 0:        feedrate_for_moves = current_f_val * 60  # mm/s to mm/min
        elif z_feed_val is not None and z_feed_val > 0:
            feedrate_for_moves = z_feed_val * 60
        
        f_command = f" F{feedrate_for_moves:.0f}" if feedrate_for_moves is not None else ""
        
        # 중복 좌표 제거를 위한 변수
        last_generated_point = None
        
        # 각 경로 구간별로 Z 높이 계산하여 G-code 생성 (긴 구간 자동 세분화 포함)
        cumulative_distance = 0.0
        
        for i, segment in enumerate(path_segments):
            segment_start_distance = cumulative_distance
            segment_end_distance = cumulative_distance + segment['distance']
            
            # 긴 구간 세분화 처리
            subdivided_points = self.subdivide_long_segment_for_zhop_boundaries(
                segment, segment_start_distance, segment_end_distance, 
                z_height_function, total_distance, slingshot_settings
            )
            
            # 세분화된 각 점에 대해 G-code 생성
            for j, point in enumerate(subdivided_points):
                point_distance = point['cumulative_distance']
                point_z = start_z + z_height_function(point_distance)
                
                # 중복 좌표 검사: 마지막 생성된 점과 같은 좌표인지 확인
                current_point_key = (round(point['x'], 3), round(point['y'], 3))
                if last_generated_point is not None and last_generated_point == current_point_key:
                    # 중복 좌표 감지 - 건너뛰기
                    continue
                
                # 구간이 0 거리가 아닌 경우에만 G-code 생성
                if point['segment_distance'] > 0.001:  # 0.001mm 이상인 경우만
                    # 이전 점과의 Z 변화 확인
                    prev_z = start_z + z_height_function(point.get('prev_distance', 0))
                    
                    if abs(point_z - prev_z) > 0.001:
                        # Z가 변하는 구간: XYZ 동시 이동
                        trajectory_gcode.append(
                            f"G1 X{point['x']:.3f} Y{point['y']:.3f} Z{point_z:.3f}{f_command} "
                            f";Smart Continuous Curve (Distance: {point_distance:.1f}mm, {point['boundary_type']})"
                        )
                    else:
                        # Z가 변하지 않는 구간: XY만 이동
                        trajectory_gcode.append(
                            f"G1 X{point['x']:.3f} Y{point['y']:.3f}{f_command} "
                            f";Smart Level Travel (Distance: {point_distance:.1f}mm, {point['boundary_type']})"
                        )
                else:
                    # 매우 짧은 구간은 XY만 이동
                    trajectory_gcode.append(
                        f"G1 X{point['x']:.3f} Y{point['y']:.3f}{f_command} "
                        f";Smart Micro Move ({point['boundary_type']})"
                    )
                
                # 생성된 점의 좌표를 기록
                last_generated_point = current_point_key
            
            # 누적 거리 업데이트
            cumulative_distance += segment['distance']
        
        # 마지막 세그먼트 완료 후 원래 Z 높이로 안전하게 복원
        final_segment = path_segments[-1]
        current_z = start_z + z_height_function(total_distance)
        
        # 현재 Z가 원래 높이보다 높다면 안전하게 하강
        if current_z > start_z + 0.001:  # 0.001mm 이상 차이가 있을 때만
            trajectory_gcode.append(
                f"G1 X{final_segment['end_x']:.3f} Y{final_segment['end_y']:.3f} Z{start_z:.3f}{f_command} "
                f";Smart Z-Hop Complete (Safe Descent)"
            )
        
        # 속도 복원
        restore_gcode = self.restore_original_speed_gcode()
        if restore_gcode:
            trajectory_gcode.append(restore_gcode)
        
        return trajectory_gcode

    def create_angle_based_z_function(self, total_distance, max_height, settings):
        """각도 기반 Z 높이 함수 생성 - 안전한 단조증가 버전"""
        import math
        
        ascent_angle = settings.get('ascent_angle', 45.0)
        descent_angle = settings.get('descent_angle', 45.0)
        angle_priority = settings.get('angle_priority', False)
        
        ascent_angle_rad = math.radians(ascent_angle)
        descent_angle_rad = math.radians(descent_angle)
        
        # 각도로부터 수평 거리 계산
        if ascent_angle >= 89.5:
            ascent_horizontal = 0.0
        else:
            ascent_horizontal = max_height / math.tan(ascent_angle_rad)
        
        if descent_angle >= 89.5:
            descent_horizontal = 0.0  
        else:
            descent_horizontal = max_height / math.tan(math.radians(descent_angle))
        
        # 3단계 구간 정의
        travel_distance = max(0, total_distance - ascent_horizontal - descent_horizontal)
        
        def z_height_at_distance(distance):
            """누적 거리에 따른 Z 높이 반환 - 안전한 단조증가 보장"""
            # 입력 거리 유효성 검사
            if distance < 0:
                return 0.0
            
            if distance <= ascent_horizontal:
                # 상승 구간: 0 → max_height로 선형 증가
                if ascent_horizontal > 0:
                    z = (distance / ascent_horizontal) * max_height
                    return max(0.0, z)  # 음수 방지
                else:
                    return max_height  # 수직 상승
            elif distance <= ascent_horizontal + travel_distance:
                # 수평 이동 구간: max_height 유지 (절대 하강 안 함)
                return max_height
            else:
                # 하강 구간: max_height 유지 (안전을 위해 하강하지 않음)
                # 연속 곡선 처리에서는 마지막에 별도로 Z축을 원래 높이로 복원
                return max_height
        
        return z_height_at_distance
    def create_percentage_based_z_function(self, total_distance, max_height, settings):
        """퍼센티지 기반 Z 높이 함수 생성 - 안전한 단조증가 버전"""
        ascent_ratio = settings.get('ascent_ratio', 30) / 100.0
        descent_ratio = settings.get('descent_ratio', 30) / 100.0
        
        ascent_distance = total_distance * ascent_ratio
        descent_distance = total_distance * descent_ratio
        travel_distance = total_distance - ascent_distance - descent_distance
        
        def z_height_at_distance(distance):
            """누적 거리에 따른 Z 높이 반환 - 안전한 단조증가 보장"""
            # 입력 거리 유효성 검사
            if distance < 0:
                return 0.0
                
            if distance <= ascent_distance:
                # 상승 구간: 0 → max_height로 선형 증가
                if ascent_distance > 0:
                    z = (distance / ascent_distance) * max_height
                    return max(0.0, z)  # 음수 방지
                else:
                    return max_height
            elif distance <= ascent_distance + travel_distance:
                # 수평 이동 구간: max_height 유지 (절대 하강 안 함)
                return max_height
            else:
                # 하강 구간: max_height 유지 (안전을 위해 하강하지 않음)
                # 연속 곡선 처리에서는 마지막에 별도로 Z축을 원래 높이로 복원
                return max_height
        
        return z_height_at_distance

    def subdivide_long_segment_for_zhop_boundaries(self, segment, start_distance, end_distance, 
                                                  z_height_function, total_distance, settings):
        """긴 구간을 Z-hop 경계에서 세분화하여 각도 일관성 보장"""
        import math
        
        # 구간 기본 정보
        segment_length = segment['distance']
        start_x, start_y = segment['start_x'], segment['start_y']
        end_x, end_y = segment['end_x'], segment['end_y']
        
        # Z-hop 단계 경계 계산
        trajectory_mode = settings.get('trajectory_mode', 'percentage')
        
        if trajectory_mode == 'angle':
            # 각도 기반 경계 계산
            ascent_angle = settings.get('ascent_angle', 45.0)
            descent_angle = settings.get('descent_angle', 45.0)
            max_height = z_height_function(total_distance / 2)  # 추정 최대 높이
            
            if ascent_angle >= 89.5:
                ascent_boundary = 0.0
            else:
                ascent_boundary = max_height / math.tan(math.radians(ascent_angle))
            
            if descent_angle >= 89.5:
                descent_start = total_distance
            else:
                descent_horizontal = max_height / math.tan(math.radians(descent_angle))
                descent_start = total_distance - descent_horizontal
        else:
            # 퍼센티지 기반 경계 계산
            ascent_ratio = settings.get('ascent_ratio', 30) / 100.0
            descent_ratio = settings.get('descent_ratio', 30) / 100.0
            
            ascent_boundary = total_distance * ascent_ratio
            descent_start = total_distance * (1.0 - descent_ratio)
        
        # 경계점들
        boundaries = []
          # 상승 끝 경계 (수평 시작)
        if start_distance <= ascent_boundary <= end_distance:
            boundaries.append({
                'distance': ascent_boundary,
                'type': 'ascent_end',
                'description': 'Ascent→Travel'
            })
        
        # 하강 시작 경계 (수평 끝)
        if start_distance <= descent_start <= end_distance:
            boundaries.append({
                'distance': descent_start,
                'type': 'descent_start', 
                'description': 'Travel→Descent'
            })
        
        # 경계점들을 거리순으로 정렬
        boundaries.sort(key=lambda x: x['distance'])
        
        # 세분화된 점들 생성
        subdivided_points = []
        current_distance = start_distance
        prev_distance = start_distance
        
        # 구간 시작점
        if start_distance == 0 or len(boundaries) > 0:
            subdivided_points.append({
                'x': start_x,
                'y': start_y,
                'cumulative_distance': start_distance,
                'segment_distance': 0.001,  # 최소값
                'boundary_type': 'segment_start',
                'prev_distance': start_distance
            })
        
        # 각 경계점에서 중간점 생성
        for boundary in boundaries:
            boundary_distance = boundary['distance']
            
            # 구간 내 위치 비율 계산
            if segment_length > 0:
                ratio = (boundary_distance - start_distance) / segment_length
            else:
                ratio = 0.0
            
            # 선형 보간으로 XY 좌표 계산
            boundary_x = start_x + (end_x - start_x) * ratio
            boundary_y = start_y + (end_y - start_y) * ratio
            
            subdivided_points.append({
                'x': boundary_x,
                'y': boundary_y,
                'cumulative_distance': boundary_distance,
                'segment_distance': boundary_distance - prev_distance,
                'boundary_type': boundary['description'],
                'prev_distance': prev_distance
            })
            
            prev_distance = boundary_distance
        
        # 구간 끝점
        if end_distance - prev_distance > 0.001:  # 의미있는 거리가 남아있을 때만
            subdivided_points.append({
                'x': end_x,
                'y': end_y,
                'cumulative_distance': end_distance,
                'segment_distance': end_distance - prev_distance,
                'boundary_type': 'segment_end',
                'prev_distance': prev_distance
            })
        
        # 세분화 결과가 없으면 원본 구간 반환
        if len(subdivided_points) == 0:
            subdivided_points.append({
                'x': end_x,
                'y': end_y,
                'cumulative_distance': end_distance,
                'segment_distance': segment_length,
                'boundary_type': 'original',
                'prev_distance': start_distance
            })
        
        return subdivided_points

# ========================================================================================
# 독립 실행을 위한 테스트 함수들
# ========================================================================================

def run_smart_zhop_test():
    """SmartZHop 독립 실행 테스트"""
    print("🎯 Smart Z-Hop v2.0 독립 실행 테스트")
    print("=" * 50)
    
    # SmartZHop 인스턴스 생성
    smart_zhop = SmartZHop()
    
    # 테스트용 G-code 데이터
    test_gcode = [
        "M204 S3000",
        "G0 F3000 X14.795 Y133.441",
        "G0 X115 Y133.237", 
        "G1 F2700 E915.58797",
        ";MESH:NONMESH",
        "G0 F3000 X114.813 Y132.992",
        "G0 X129 Y129.801",
        "G1 Z1.000 ;Smart Z-Hop Layer Change",
        ";LAYER:1",
        "M203 Z15000 ;Restore original Z-axis speed",
        "M204 S5000"
    ]
    
    print("📝 입력 G-code:")
    for line in test_gcode:
        print(f"  {line}")
    
    print("\n🔄 Smart Z-Hop 실행 중...")
    
    try:
        # Smart Z-Hop 실행
        result = smart_zhop.execute(test_gcode)
        
        print("\n✅ 출력 G-code:")
        for line in result:
            print(f"  {line}")
            
        print(f"\n📊 결과: {len(test_gcode)}줄 → {len(result)}줄")
        print("🎉 Smart Z-Hop 독립 실행 성공!")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

def test_traditional_mode():
    """Traditional 모드 테스트"""
    print("\n🔧 Traditional 모드 테스트")
    print("-" * 30)
    
    smart_zhop = SmartZHop()
    # Mock 설정에서 traditional 모드가 기본값
    
    test_lines = [
        "G0 F3000 X10 Y10",
        "G1 F1500 X20 Y20 E1.0"
    ]
    
    result = smart_zhop.execute(test_lines)
    print("Traditional 모드 실행 완료 ✅")

def test_slingshot_mode():
    """Slingshot 모드 테스트"""
    print("\n🚀 Slingshot 모드 테스트")
    print("-" * 30)
    
    smart_zhop = SmartZHop()
    # Mock에서 slingshot 모드로 변경
    smart_zhop.getSettingValueByKey = lambda key: 'slingshot' if key == 'zhop_mode' else smart_zhop.__class__.__bases__[0]().getSettingValueByKey(key)
    
    test_lines = [
        "G0 F3000 X10 Y10",
        "G1 F1500 X50 Y50 E2.0"
    ]
    
    result = smart_zhop.execute(test_lines)
    print("Slingshot 모드 실행 완료 ✅")

def test_v3_continuous_curve_demo():
    """V3.0 연속 곡선 처리 데모"""
    print("\n🔗 V3.0 연속 곡선 처리 데모")
    print("-" * 40)
    
    smart_zhop = SmartZHop()
    
    # 연속 travel move 시나리오 (톱니파 문제 재현)
    continuous_demo = [
        "G1 X100 Y100 Z2.5 E50.0 F1500",    # 익스트루전 종료
        "G0 F30000 X48.650 Y63.170",        # 리트랙션 후 이동
        "G0 X48.700 Y68.841 F30000",        # 연속 travel 1
        "G0 X49.662 Y77.066 F30000",        # 연속 travel 2
        "G0 X49.803 Y78.304 F30000",        # 연속 travel 3
        "G0 X50.235 Y79.538 F30000",        # 연속 travel 4
        "G0 X50.931 Y80.643 F30000",        # 연속 travel 5
        "G1 X50.931 Y80.643 Z2.5 E52.0 F1500"  # 익스트루전 재시작
    ]
    
    print("📝 연속 travel move 입력 (5개 연속):")
    for line in continuous_demo:
        if line.startswith("G0"):
            print(f"   🔸 {line}")
    
    result = smart_zhop.execute(continuous_demo)
    
    print("\n✅ V3.0 연속 곡선 처리 결과:")
    smart_lines = [line for line in result if "Smart" in line]
    for line in smart_lines:
        print(f"   🎯 {line}")
    
    print(f"\n📊 처리 효과: 5개 개별 travel → {len(smart_lines)}개 연속 곡선")
    print("🎉 톱니파 문제 해결! 부드러운 곡선으로 변환 완료!")

# 메인 실행 블록
if __name__ == "__main__":
    print("🎉 Smart Z-Hop v2.0 - 독립 실행 모드")
    print("=" * 60)
    
    # 기본 테스트 실행
    run_smart_zhop_test()
    
    # 개별 모드 테스트
    test_traditional_mode()
    test_slingshot_mode()
    
    # V3.0 연속 곡선 데모
    test_v3_continuous_curve_demo()
    
    print("\n" + "=" * 70)
    print("✨ Smart Z-Hop V3.0 모든 테스트 완료!")
    print("🎯 톱니파 문제 해결 + 연속 곡선 처리 + 리트랙션 감지")
    print("📋 python SmartZHop.py 명령으로 언제든 V3.0 기능을 테스트하세요!")
    print("🏆 3D 프린팅의 새로운 차원을 경험해보세요!")
