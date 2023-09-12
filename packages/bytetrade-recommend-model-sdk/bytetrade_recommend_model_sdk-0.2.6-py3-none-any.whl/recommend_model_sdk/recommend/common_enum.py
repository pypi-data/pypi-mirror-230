from enum import IntEnum
class VectorStoreEnum(IntEnum):
    FAISS=0
    WEAVIATE=1

class RecommendSupportLanguageEnum(IntEnum):
    MULTILINGUAL = 0
    ENGLISH = 1
    CHINESE = 2
    
class RecommendSupportLanguageEnumToLangdetectLanguage:
    def __init__(self) -> None:
        self.__recommend_support_language_enum_to_langdetect_language = dict()
        self.__langdetect_language_to_recommend_support_language_enum = dict()
        self.__recommend_support_language_enum_to_langdetect_language[RecommendSupportLanguageEnum.MULTILINGUAL] = 'multilingual'
        self.__langdetect_language_to_recommend_support_language_enum['multilingual'] = RecommendSupportLanguageEnum.MULTILINGUAL
        self.__recommend_support_language_enum_to_langdetect_language[RecommendSupportLanguageEnum.ENGLISH] = 'en'
        self.__langdetect_language_to_recommend_support_language_enum['en'] = RecommendSupportLanguageEnum.ENGLISH
        self.__recommend_support_language_enum_to_langdetect_language[RecommendSupportLanguageEnum.CHINESE] = 'zh-cn'
        self.__langdetect_language_to_recommend_support_language_enum['zh-cn'] = RecommendSupportLanguageEnum.CHINESE
    
    def get_langdetect_language_according_recommend_support_language(self,recommend_support_language):
        if isinstance(recommend_support_language,RecommendSupportLanguageEnum) is False:
            raise ValueError("recommend_support_language is not RecommendSupportLanguageEnum")
        if recommend_support_language not in self.__recommend_support_language_enum_to_langdetect_language:
            raise ValueError("recommend_support_language have no corresponding langdetect language")
        return self.__recommend_support_language_enum_to_langdetect_language[recommend_support_language]
    
    def get_recommend_support_language_according_langdetect_language(self,langdetect_language):
        if isinstance(langdetect_language,str) is False:
            raise ValueError("langdetect_language is not str")
        if langdetect_language not in self.__langdetect_language_to_recommend_support_language_enum:
            raise ValueError("langdetect_language have no corresponding recommend support language")
        return self.__langdetect_language_to_recommend_support_language_enum[langdetect_language]
    
    def get_all_lang_detect_language_set(self):
        return set(self.__langdetect_language_to_recommend_support_language_enum.keys())
        
        

RECOMMEND_SUPPORT_LANGUAGE_TO_LANGDETECT_LANGUAGE_DICT = RecommendSupportLanguageEnumToLangdetectLanguage()
