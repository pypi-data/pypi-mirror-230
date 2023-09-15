import os


def get_value(value):
    """将java数据转化为python数据。

    目前仅支持有限种类型，根据实际需要进行扩展。
    """
    import java.lang.String
    import java.lang.Integer
    import java.lang.Long
    import java.lang.Float
    import java.util.List
    import java.util.Set
    import java.util.Map
    import jpype

    if value is None:
        return value
    if isinstance(value, java.lang.String):
        return str(value)
    if isinstance(value, java.lang.Integer):
        return int(value)
    if isinstance(value, java.lang.Long):
        return int(value)
    if isinstance(value, java.lang.Float):
        return int(value)
    if isinstance(value, java.util.List):
        result = []
        for item in value:
            result.append(get_value(item))
        return result
    if isinstance(value, java.util.Set):
        result = set()
        for item in value:
            result.add(get_value(item))
        return result
    if isinstance(value, java.util.Map):
        result = {}
        for key in value.keySet():
            result[get_value(key)] = get_value(value[key])
        return result
    if isinstance(value, jpype.JArray):
        if len(value) < 1:
            return []
        else:
            e0 = value[0]
            if isinstance(e0, jpype.JByte):
                return bytes(value)
            elif isinstance(e0, jpype.JChar):
                return str(value)
            else:
                result = []
                for i in range(len(value)):
                    result.append(get_value(value[i]))
                return result
    raise RuntimeError(
        "Can NOT cast java value to python value, type={}, value={}, ".foramt(
            type(value), value
        )
    )


def start_jvm(classpaths=None):
    classpaths = classpaths or [os.getcwd()]

    import jpype
    import jpype.imports

    jpype.startJVM(classpath=classpaths)
