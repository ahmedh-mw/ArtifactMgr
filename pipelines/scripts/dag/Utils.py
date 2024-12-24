class Utils:
    @staticmethod
    def getList(jsonObject, listName):
        listObject  = jsonObject.get(listName)
        if listObject is None:
            listObject = []
        return listObject
    
    def getBoolean(jsonObject, fieldName, defaultValue=False):
        item = jsonObject.get(fieldName)
        if item is None:
            item = defaultValue
        return item
    
    def getDic(jsonObject, fieldName, defaultValue={}):
        dic = jsonObject.get(fieldName)
        if dic is None:
            dic = defaultValue
        return dic
    
    def dictEncode(obj):
        if isinstance(obj, dict):
            objDict = obj
        else:
            objDict = vars(obj)
        result = dict(objDict)
        for k in list(result.keys()):
            if k.startswith('_'):
                del result[k]
            elif isinstance(result[k], set):
                result[k] = list(result[k])
        return result