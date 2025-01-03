class Utils:
    @staticmethod
    def getList(jsonObject, listName):
        listObject  = jsonObject.get(listName)
        if listObject is None:
            listObject = []
        elif isinstance(listObject, str):
            listObject = [listObject]
        return listObject
    
    @staticmethod
    def getBoolean(jsonObject, fieldName, defaultValue=False):
        item = jsonObject.get(fieldName)
        if item is None:
            item = defaultValue
        elif isinstance(item, str):
            item = item in ['True', 'true', '1']
        return item
    
    @staticmethod
    def getDic(jsonObject, fieldName, defaultValue={}):
        dic = jsonObject.get(fieldName)
        if dic is None:
            dic = defaultValue
        return dic
    
    @staticmethod
    def dictEncode(obj):
        if isinstance(obj, dict):
            objDict = obj
        elif isinstance(obj, list):
            items =[]
            for item in obj:
                items.append(Utils.dictEncode(item))
            return items
        else:
            objDict = vars(obj)
        result = dict(objDict)
        for k in list(result.keys()):
            if k.startswith('_'):
                del result[k]
            elif isinstance(result[k], set):
                result[k] = list(result[k])
        return result