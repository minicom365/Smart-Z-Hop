# -*- coding: utf-8 -*-
"""
Smart Z-Hop v1.0 - Production Ready
Advanced Z-Hop post-processing script combining Traditional and Slingshot algorithms

ORIGINAL SOURCES:
- Z-HopMove v0.3.1 by hawmaru (요래요래)
  Blog: https://blog.naver.com/hawmaru/221576526356
  Traditional vertical Z-hop algorithm foundation

- Slingshot Z-Hop by echo-lalia  
  GitHub: https://github.com/echo-lalia/Slingshot-Z-Hop
  Revolutionary curved trajectory algorithm foundation

SMART Z-HOP INTEGRATION:
- Unified algorithm implementation
- Korean/English internationalization 
- Enhanced user interface
- Speed unit optimization (mm/s)
- Single-file deployment architecture

Features:
- Dual Algorithm Support: Traditional vs Slingshot modes
- Layer Control: Top/Bottom/Custom layer targeting  
- Distance-based Dynamic Height: Adaptive Z-hop based on travel distance
- Consecutive Move Processing: Intelligent multi-move handling
- Complete Internationalization: Korean/English auto-detection
"""

import math
import locale
from ..Script import Script

# 다국어 지원을 위한 번역 딕셔너리
TRANSLATIONS = {
    'ko_KR': {
        'Smart Z-Hop': '스마트 Z-홉',
        'Enable': '활성화',
        'Enable/Disable Smart Z-Hop functionality': '스마트 Z-홉 기능을 활성화하거나 비활성화합니다. 체크하면 설정된 조건에 따라 Z-홉이 실행됩니다.',
        'Z-Hop Mode': 'Z-홉 방식',
        'Select Z-Hop algorithm: Traditional (vertical) or Slingshot (curved)': 'Z-홉 알고리즘을 선택합니다:\\n• 전통적: 수직 상승 후 이동 (기존 방식)\\n• 슬링샷: 곡선 궤적으로 이동 (속도 향상)',
        'Traditional (기존)': '전통적 (수직 이동)',
        'Slingshot (신규)': '슬링샷 (곡선 이동)',
        'Layer Change': '레이어 변경 시',
        'Z-Hop before layer change': '새 레이어로 이동하기 전에 Z-홉을 실행합니다. 레이어 경계에서 노즐과 프린트의 충돌을 방지합니다.',
        'Z-Hop Height': 'Z-홉 높이',
        'Select Z-Hop height (Layer Height uses Quality setting value)': 'Z-홉 높이를 설정합니다:\\n• 레이어 높이: 현재 품질 설정의 레이어 높이 사용\\n• 사용자 지정: 직접 입력한 높이값 사용',
        'Custom Height': '사용자 지정 높이',
        'Custom Z-hop height value': '사용자 지정 Z-홉 높이를 밀리미터 단위로 입력합니다. 일반적으로 0.2~1.0mm 범위를 사용합니다.',
        'Travel': '이동 중',
        'Z-Hop before travel moves': '압출 없는 이동(트래블) 전에 Z-홉을 실행합니다. 프린트된 부분과의 충돌을 방지합니다.',
        'Travel Distance': '최소 이동 거리',
        'Apply Z-Hop only for moves longer than this distance': '설정한 거리보다 긴 이동에서만 Z-홉을 실행합니다. 짧은 이동에서는 Z-홉을 건너뛰어 인쇄 시간을 단축합니다.',
        'Custom Layers': '지정 레이어',
        'Apply Travel Z-Hop only on specified layers (space separated)': '특정 레이어에서만 이동 Z-홉을 적용합니다. 레이어 번호를 공백으로 구분하여 입력 (예: 1 5 10 15)',
        'Top/Bottom Only': '상하단 레이어만',
        'Apply Travel Z-Hop only on top/bottom layers': '첫 번째와 마지막 레이어에서만 이동 Z-홉을 적용합니다. 주요 표면 품질 향상에 집중합니다.',
        'Min Z-Hop (Slingshot)': '최소 Z-홉 높이',
        'Minimum Z-hop height for slingshot mode': '슬링샷 모드에서 사용할 최소 Z-홉 높이입니다. 짧은 거리 이동 시 적용됩니다.',
        'Max Distance (Slingshot)': '기준 최대 거리',
        'Maximum travel distance for height calculation': '높이 계산의 기준이 되는 최대 이동 거리입니다. 이 거리에서 최대 Z-홉 높이가 적용됩니다.',
        'Z Feedrate (Slingshot)': 'Z축 이동속도',
        'Feedrate for Z movements in slingshot mode': '슬링샷 모드에서 Z축 이동 시 사용할 속도입니다. 너무 빠르면 진동이 발생할 수 있습니다.',
        'Second Move % (Slingshot)': '하강 구간 비율',
        'Percentage of travel distance for the second move': '전체 이동 거리 중 하강하면서 이동할 구간의 비율입니다. 작을수록 더 이른 시점에 하강을 시작합니다.'
    },
    'en_US': {
        'Smart Z-Hop': 'Smart Z-Hop',
        'Enable': 'Enable',
        'Enable/Disable Smart Z-Hop functionality': 'Enable/Disable Smart Z-Hop functionality. When checked, Z-hop will be executed according to configured conditions.',
        'Z-Hop Mode': 'Z-Hop Mode',
        'Select Z-Hop algorithm: Traditional (vertical) or Slingshot (curved)': 'Select Z-Hop algorithm:\\n• Traditional: Vertical lift then move (classic method)\\n• Slingshot: Curved trajectory movement (improved speed)',
        'Traditional (기존)': 'Traditional (Vertical)',
        'Slingshot (신규)': 'Slingshot (Curved)',
        'Layer Change': 'Layer Change',
        'Z-Hop before layer change': 'Execute Z-hop before moving to a new layer. Prevents nozzle collision with printed parts at layer boundaries.',
        'Z-Hop Height': 'Z-Hop Height',
        'Select Z-Hop height (Layer Height uses Quality setting value)': 'Set Z-hop height:\\n• Layer Height: Use current quality setting layer height\\n• Custom Height: Use manually entered height value',
        'Custom Height': 'Custom Height',
        'Custom Z-hop height value': 'Enter custom Z-hop height in millimeters. Typically use 0.2-1.0mm range.',
        'Travel': 'Travel Moves',
        'Z-Hop before travel moves': 'Execute Z-hop before non-extruding travel moves. Prevents collision with printed parts.',
        'Travel Distance': 'Minimum Travel Distance',
        'Apply Z-Hop only for moves longer than this distance': 'Execute Z-hop only for moves longer than this distance. Skip Z-hop for short moves to reduce print time.',
        'Custom Layers': 'Custom Layers',
        'Apply Travel Z-Hop only on specified layers (space separated)': 'Apply travel Z-hop only on specific layers. Enter layer numbers separated by spaces (e.g., 1 5 10 15)',
        'Top/Bottom Only': 'Top/Bottom Only',
        'Apply Travel Z-Hop only on top/bottom layers': 'Apply travel Z-hop only on first and last layers. Focus on key surface quality improvement.',
        'Min Z-Hop (Slingshot)': 'Min Z-Hop Height',
        'Minimum Z-hop height for slingshot mode': 'Minimum Z-hop height for slingshot mode. Applied for short distance moves.',
        'Max Distance (Slingshot)': 'Reference Max Distance',
        'Maximum travel distance for height calculation': 'Reference maximum travel distance for height calculation. Maximum Z-hop height is applied at this distance.',
        'Z Feedrate (Slingshot)': 'Z Axis Speed',
        'Feedrate for Z movements in slingshot mode': 'Speed for Z-axis movements in slingshot mode. Too fast may cause vibrations.',
        'Second Move % (Slingshot)': 'Descent Section Ratio',
        'Percentage of travel distance for the second move': 'Percentage of total travel distance for the descending section. Smaller values start descent earlier.'
    }
}

# 현재 언어 감지 및 번역 함수
def i18n_catalog_i18nc(context, text, category=""):
    """다국어 지원 함수"""
    try:
        # Cura의 언어 설정 감지 시도
        current_locale = locale.getdefaultlocale()[0]
        if current_locale and current_locale.startswith('ko'):
            lang = 'ko_KR'
        else:
            lang = 'en_US'
    except:
        # 기본값은 한국어 (개발자 환경 기준)
        lang = 'ko_KR'
    
    if lang in TRANSLATIONS and text in TRANSLATIONS[lang]:
        return TRANSLATIONS[lang][text]
    return text

class SmartZHop(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        # 번역 텍스트 생성
        name = i18n_catalog_i18nc("@label", "Smart Z-Hop")
        enable_label = i18n_catalog_i18nc("@label", "Enable")
        enable_desc = i18n_catalog_i18nc("@info:tooltip", "Enable/Disable Smart Z-Hop functionality")
        zhop_mode_label = i18n_catalog_i18nc("@label", "Z-Hop Mode")
        zhop_mode_desc = i18n_catalog_i18nc("@info:tooltip", "Select Z-Hop algorithm: Traditional (vertical) or Slingshot (curved)")
        traditional_opt = i18n_catalog_i18nc("@option:traditional", "Traditional (기존)")
        slingshot_opt = i18n_catalog_i18nc("@option:slingshot", "Slingshot (신규)")
        layer_change_label = i18n_catalog_i18nc("@label", "Layer Change")
        layer_change_desc = i18n_catalog_i18nc("@info:tooltip", "Z-Hop before layer change")
        zhop_height_label = i18n_catalog_i18nc("@label", "Z-Hop Height")
        zhop_height_desc = i18n_catalog_i18nc("@info:tooltip", "Select Z-Hop height (Layer Height uses Quality setting value)")
        custom_height_label = i18n_catalog_i18nc("@label", "Custom Height")
        custom_height_desc = i18n_catalog_i18nc("@info:tooltip", "Custom Z-hop height value")
        travel_label = i18n_catalog_i18nc("@label", "Travel")
        travel_desc = i18n_catalog_i18nc("@info:tooltip", "Z-Hop before travel moves")
        travel_distance_label = i18n_catalog_i18nc("@label", "Travel Distance")
        travel_distance_desc = i18n_catalog_i18nc("@info:tooltip", "Apply Z-Hop only for moves longer than this distance")
        custom_layers_label = i18n_catalog_i18nc("@label", "Custom Layers")
        custom_layers_desc = i18n_catalog_i18nc("@info:tooltip", "Apply Travel Z-Hop only on specified layers (space separated)")
        top_bottom_label = i18n_catalog_i18nc("@label", "Top/Bottom Only")
        top_bottom_desc = i18n_catalog_i18nc("@info:tooltip", "Apply Travel Z-Hop only on top/bottom layers")
        min_zhop_label = i18n_catalog_i18nc("@label", "Min Z-Hop (Slingshot)")
        min_zhop_desc = i18n_catalog_i18nc("@info:tooltip", "Minimum Z-hop height for slingshot mode")
        max_distance_label = i18n_catalog_i18nc("@label", "Max Distance (Slingshot)")
        max_distance_desc = i18n_catalog_i18nc("@info:tooltip", "Maximum travel distance for height calculation")
        z_feedrate_label = i18n_catalog_i18nc("@label", "Z Feedrate (Slingshot)")
        z_feedrate_desc = i18n_catalog_i18nc("@info:tooltip", "Feedrate for Z movements in slingshot mode")
        second_move_label = i18n_catalog_i18nc("@label", "Second Move % (Slingshot)")
        second_move_desc = i18n_catalog_i18nc("@info:tooltip", "Percentage of travel distance for the second move")

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
                "slingshot_min_zhop": {
                    "label": "  > %s",
                    "description": "%s",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 0.1,
                    "minimum_value": "0",
                    "enabled": "zhop_mode == 'slingshot'"
                },
                "slingshot_max_distance": {
                    "label": "  > %s",
                    "description": "%s",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 80.0,
                    "minimum_value": "0",
                    "enabled": "zhop_mode == 'slingshot'"
                },
                "slingshot_z_feedrate": {
                    "label": "  > %s",
                    "description": "%s",
                    "unit": "mm/s",
                    "type": "int",
                    "default_value": 50,
                    "minimum_value": "1",
                    "enabled": "zhop_mode == 'slingshot'"
                },
                "slingshot_second_move_percent": {
                    "label": "  > %s",
                    "description": "%s",
                    "unit": "%%",
                    "type": "int",
                    "default_value": 10,
                    "minimum_value": "1",
                    "maximum_value": "50",
                    "enabled": "zhop_mode == 'slingshot'"
                },
                "layer_change": {
                    "label": "%s",
                    "description": "%s",
                    "type": "bool",
                    "default_value": true
                },
                "lc_z_hop_height": {
                    "label": "  > %s",
                    "description": "%s",
                    "type": "enum",
                    "options": {"layer_height": "Layer Height", "custom_height": "Custom Height"},
                    "default_value": "layer_height",
                    "enabled": "layer_change"
                },
                "lc_custom_height": {
                    "label": "  > %s",
                    "description": "%s",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 0.4,
                    "minimum_value": "0",
                    "minimum_value_warning": "0",
                    "enabled": "layer_change and lc_z_hop_height == 'custom_height'"
                },
                "travel": {
                    "label": "%s",
                    "description": "%s",
                    "type": "bool",
                    "default_value": false
                },
                "tr_z_hop_height": {
                    "label": "  > %s",
                    "description": "%s",
                    "type": "enum",
                    "options": {"layer_height": "Layer Height", "custom_height": "Custom Height"},
                    "default_value": "layer_height",
                    "enabled": "travel"
                },
                "tr_custom_height": {
                    "label": "  > %s",
                    "description": "%s",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 0.4,
                    "minimum_value": "0",
                    "minimum_value_warning": "0",
                    "enabled": "travel and tr_z_hop_height == 'custom_height'"
                },
                "tr_distance": {
                    "label": "  > %s",
                    "description": "%s",
                    "unit": "mm",
                    "type": "float",
                    "default_value": 20,
                    "minimum_value": "0",
                    "minimum_value_warning": "0",
                    "enabled": "travel"
                },
                "tr_custom_layer": {
                    "label": "  > %s",
                    "description": "%s",
                    "type": "str",
                    "default_value": "",
                    "enabled": "travel"
                },
                "tr_top_bottom": {
                    "label": "  > %s",
                    "description": "%s",
                    "type": "bool",
                    "default_value": false,
                    "enabled": "travel"
                }
            }
        }""" % (
            name, enable_label, enable_desc, zhop_mode_label, zhop_mode_desc,
            traditional_opt, slingshot_opt, layer_change_label, layer_change_desc,
            zhop_height_label, zhop_height_desc, custom_height_label, custom_height_desc,
            travel_label, travel_desc, zhop_height_label, zhop_height_desc,
            custom_height_label, custom_height_desc, travel_distance_label, travel_distance_desc,
            custom_layers_label, custom_layers_desc, top_bottom_label, top_bottom_desc,
            min_zhop_label, min_zhop_desc, 
            max_distance_label, max_distance_desc, z_feedrate_label, z_feedrate_desc, 
            second_move_label, second_move_desc
        )

    def execute(self, data):
        # 설정값 가져오기
        enable = self.getSettingValueByKey("enable")
        zhop_mode = self.getSettingValueByKey("zhop_mode")
        layer_change = self.getSettingValueByKey("layer_change")
        lc_z_hop_height = self.getSettingValueByKey("lc_z_hop_height")
        lc_custom_height = self.getSettingValueByKey("lc_custom_height")
        travel = self.getSettingValueByKey("travel")
        tr_z_hop_height = self.getSettingValueByKey("tr_z_hop_height")
        tr_custom_height = self.getSettingValueByKey("tr_custom_height")
        tr_distance = self.getSettingValueByKey("tr_distance")
        tr_custom_layer = self.getSettingValueByKey("tr_custom_layer")
        tr_top_bottom = self.getSettingValueByKey("tr_top_bottom")
        
        # Slingshot 설정
        slingshot_min_zhop = self.getSettingValueByKey("slingshot_min_zhop")
        slingshot_max_distance = self.getSettingValueByKey("slingshot_max_distance")
        slingshot_z_feedrate = self.getSettingValueByKey("slingshot_z_feedrate")
        slingshot_second_move_percent = self.getSettingValueByKey("slingshot_second_move_percent")

        if enable == False:
            return data

        if layer_change == False and travel == False:
            return data

        # 사용자 지정 레이어 파싱
        tr_custom_layer_num = []
        if tr_custom_layer is not None and tr_custom_layer.strip():
            try:
                tr_custom_layer = tr_custom_layer.split()
                tr_custom_layer_num = [int(i) for i in tr_custom_layer]
            except ValueError:
                pass

        # 모드에 따른 실행
        if zhop_mode == "slingshot":
            return self.execute_slingshot_mode(data, {
                'layer_change': layer_change,
                'lc_z_hop_height': lc_z_hop_height,
                'lc_custom_height': lc_custom_height,
                'travel': travel,
                'tr_z_hop_height': tr_z_hop_height,
                'tr_custom_height': tr_custom_height,
                'tr_distance': tr_distance,
                'tr_custom_layer_num': tr_custom_layer_num,
                'tr_top_bottom': tr_top_bottom,
                'min_zhop': slingshot_min_zhop,
                'max_distance': slingshot_max_distance,
                'z_feedrate': slingshot_z_feedrate,
                'second_move_percent': slingshot_second_move_percent
            })
        else:
            return self.execute_traditional_mode(data, {
                'layer_change': layer_change,
                'lc_z_hop_height': lc_z_hop_height,
                'lc_custom_height': lc_custom_height,
                'travel': travel,
                'tr_z_hop_height': tr_z_hop_height,
                'tr_custom_height': tr_custom_height,
                'tr_distance': tr_distance,
                'tr_custom_layer_num': tr_custom_layer_num,
                'tr_top_bottom': tr_top_bottom
            })

    def execute_traditional_mode(self, data, settings):
        """기존 Traditional Z-Hop 방식 실행"""
        index = 0
        
        for layer in data:
            lines = layer.split("\n")
            output_gcode = ""
            x, y = 0, 0
            current_z = 0
            layer_cnt = 1
            current_layer = 1
            lc_z_hop_ht = 0.2
            tr_z_hop_ht = 0.2
            g1_saved = False
            tr_layer = False
            lc_z_hop_saved = False
            tr_z_hop_saved = False
            lc_line = False
            
            for line in lines:
                if ";LAYER_COUNT:" in line:
                    layer_cnt = int(line[(line.index(":") + 1):].strip())

                if ";Layer height:" in line:
                    qaulty_height = float(line[(line.index(":") + 2):].strip())

                    if settings['lc_z_hop_height'] == "layer_height":
                        lc_z_hop_ht = qaulty_height
                    elif settings['lc_z_hop_height'] == "custom_height":
                        lc_z_hop_ht = settings['lc_custom_height']

                    if settings['tr_z_hop_height'] == "layer_height":
                        tr_z_hop_ht = qaulty_height
                    elif settings['tr_z_hop_height'] == "custom_height":
                        tr_z_hop_ht = settings['tr_custom_height']

                if ";LAYER:" in line:
                    tr_layer = True
                    current_layer = int(line[(line.index(":") + 1):].strip()) + 1

                    if settings['tr_top_bottom'] == True:
                        if current_layer > 1 and current_layer < layer_cnt:
                            tr_layer = False
                        else:
                            tr_layer = True

                    if len(settings['tr_custom_layer_num']) >= 1:
                        if current_layer in settings['tr_custom_layer_num']:
                            tr_layer = True
                        elif settings['tr_top_bottom'] == False:
                            tr_layer = False

                if self.getValue(line, "Z") is not None:
                    current_z = self.getValue(line, "Z")

                # 레이어 변경 Z-hop 처리
                if settings['layer_change'] == True and lc_line == True:
                    lc_gcode = "G0 Z%.2f;Script(SmartZHop-LC)\n%s\n" % (current_z + lc_z_hop_ht, line)
                    lc_z_hop_saved = True

                # 이동 Z-hop 처리
                if settings['travel'] == True and tr_layer == True:
                    if self.getValue(line, 'G') == 1:
                        if self.getValue(line, "X") is not None and self.getValue(line, "Y") is not None and self.getValue(line, "E") is not None:
                            x = self.getValue(line, "X")
                            y = self.getValue(line, "Y")
                            g1_saved = True

                    if self.getValue(line, 'G') == 0 and g1_saved == True:
                        g1_saved = False
                        if self.getValue(line, "X") is not None and self.getValue(line, "Y") is not None and self.getValue(line, "Z") is None:
                            tx = self.getValue(line, "X")
                            ty = self.getValue(line, "Y")
                            distance = float(math.sqrt(math.pow(tx - x , 2) + math.pow(ty - y , 2)))
                            if distance >= settings['tr_distance']:
                                tr_gcode = "G0 Z%.2f;Script(SmartZHop-TR Up, D:%.2f)\n" % (current_z + tr_z_hop_ht, distance)
                                tr_gcode += line + "\n"
                                tr_gcode += "G0 Z%.2f;Script(SmartZHop-TR Down)\n" % current_z
                                tr_z_hop_saved = True
                                x = tx
                                y = ty

                # 출력 처리
                if settings['layer_change'] == True and lc_z_hop_saved == True:
                    output_gcode += lc_gcode
                    lc_z_hop_saved = False
                    lc_line = False
                    g1_saved = False
                elif settings['travel'] == True and tr_z_hop_saved == True:
                    output_gcode += tr_gcode
                    tr_z_hop_saved = False
                else:
                    output_gcode += line + "\n"

                if ";MESH:NONMESH" in line:
                    lc_line = True
                    tr_layer = False

            data[index] = output_gcode
            index += 1
        return data

    def execute_slingshot_mode(self, data, settings):
        """새로운 Slingshot Z-Hop 방식 실행"""
        for layer_index, layer in enumerate(data):
            lines = layer.split('\n')
            modified_lines = []
            
            # 변수 초기화
            current_z_height = 0
            current_feedrate = 3000
            target_x = 0
            target_y = 0  
            prev_x = 0
            prev_y = 0
            tr_layer = True
            layer_cnt = 1
            current_layer = 1
            lc_z_hop_ht = 0.2
            tr_z_hop_ht = 0.2
            lc_line = False

            # 레이어 정보 수집
            for line in lines:
                if ";LAYER_COUNT:" in line:
                    layer_cnt = int(line[(line.index(":") + 1):].strip())
                if ";LAYER:" in line:
                    current_layer = int(line[(line.index(":") + 1):].strip()) + 1
                if ";Layer height:" in line:
                    qaulty_height = float(line[(line.index(":") + 2):].strip())
                    if settings['lc_z_hop_height'] == "layer_height":
                        lc_z_hop_ht = qaulty_height
                    elif settings['lc_z_hop_height'] == "custom_height":
                        lc_z_hop_ht = settings['lc_custom_height']
                    
                    if settings['tr_z_hop_height'] == "layer_height":
                        tr_z_hop_ht = qaulty_height
                    elif settings['tr_z_hop_height'] == "custom_height":
                        tr_z_hop_ht = settings['tr_custom_height']

            # 레이어 제한 확인
            if settings['tr_top_bottom']:
                if current_layer > 1 and current_layer < layer_cnt:
                    tr_layer = False

            if settings['tr_custom_layer_num']:
                if current_layer in settings['tr_custom_layer_num']:
                    tr_layer = True
                elif not settings['tr_top_bottom']:
                    tr_layer = False

            # 거리 계수 계산
            second_distance_factor = settings['second_move_percent'] * 0.01
            first_distance_factor = 1.0 - second_distance_factor

            for line in lines:
                # 레이어 변경 처리
                if settings['layer_change'] and lc_line and ";LAYER:" in line:
                    # 슬링샷 스타일 레이어 변경 Z-hop
                    lc_line_gcode = f"G0 Z{current_z_height + lc_z_hop_ht:.2f};Script(SmartZHop-LC-Slingshot)"
                    modified_lines.append(lc_line_gcode)
                    modified_lines.append(line)
                    lc_line = False
                    continue

                # G1 명령 파싱하여 위치 추적
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

                # 이동 명령 처리
                if self.is_travel_move(line) and settings['travel'] and tr_layer:
                    distance = self.calculate_distance(prev_x, prev_y, target_x, target_y)
                    
                    if distance >= settings['tr_distance']:
                        # 거리에 따른 Z-hop 높이 계산 (공통 Z-hop 높이를 최대값으로 사용)
                        max_zhop_height = tr_z_hop_ht  # 공통 tr Z-hop 높이를 최대값으로 사용
                        zhop_height = current_z_height + self.linear_interpolation(
                            distance, 0, settings['max_distance'], settings['min_zhop'], max_zhop_height)

                        # Slingshot 궤적의 피크 위치 계산
                        delta_x = target_x - prev_x
                        peak_x = prev_x + (delta_x * first_distance_factor)
                        delta_y = target_y - prev_y  
                        peak_y = prev_y + (delta_y * first_distance_factor)

                        # Slingshot Z-hop 이동 생성 (속도를 mm/s에서 mm/min으로 변환)
                        zhop_line = f'G1 X{round(peak_x, 5)} Y{round(peak_y, 5)} Z{round(zhop_height, 5)} F{current_feedrate} ; SmartZHop-Slingshot'
                        lower_line = f'G1 X{target_x} Y{target_y} Z{current_z_height} F{settings["z_feedrate"] * 60} ; SmartZHop-Slingshot Lower'
                        
                        modified_lines.append(zhop_line)
                        modified_lines.append(lower_line)
                    else:
                        modified_lines.append(line)
                else:
                    modified_lines.append(line)

                # 레이어 변경 플래그 설정
                if ";MESH:NONMESH" in line:
                    lc_line = True

            data[layer_index] = '\n'.join(modified_lines)
        return data

    def getValue(self, line, key):
        """G-code 라인에서 특정 키의 값을 추출"""
        if key not in line:
            return None
        try:
            start_index = line.index(key) + 1
            end_index = start_index
            while end_index < len(line) and (line[end_index].isdigit() or line[end_index] in '.-'):
                end_index += 1
            return float(line[start_index:end_index])
        except (ValueError, IndexError):
            return None

    def is_travel_move(self, line):
        """이동 명령인지 확인 (압출 없음)"""
        return ('G1' in line or 'G0' in line) and 'E' not in line and ('X' in line or 'Y' in line)

    def calculate_distance(self, x1, y1, x2, y2):
        """두 점 사이의 거리 계산"""
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def linear_interpolation(self, distance, min_dist, max_dist, min_height, max_height):
        """이동 거리에 따른 높이 보간"""
        if distance <= min_dist:
            return min_height
        elif distance >= max_dist:
            return max_height
        else:
            ratio = (distance - min_dist) / (max_dist - min_dist)
            return min_height + ratio * (max_height - min_height)
