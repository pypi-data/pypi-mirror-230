from .curveData import 基准出力曲线, 基准出力曲线2, 基准出力曲线3, 负荷曲线, 策略曲线

def getCurveData(kind):
    extra_paths = {
        '光伏': 基准出力曲线,
        '风机': 基准出力曲线,
        '燃气': 基准出力曲线2,
        '水电': 基准出力曲线2,
        '常规小火电': 基准出力曲线2,
        '生物质发电': 基准出力曲线2,
        '垃圾电厂': 基准出力曲线2,
        '负荷分类':  负荷曲线,
        '负荷用户':  负荷曲线,
        '储能配置': 策略曲线,
    }
    if kind in extra_paths:
        return extra_paths[kind]
    else :
        return []