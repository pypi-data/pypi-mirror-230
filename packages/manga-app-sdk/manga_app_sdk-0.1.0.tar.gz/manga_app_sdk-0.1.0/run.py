import manga_app_sdk
import json

if __name__ == "__main__":
    obj = manga_app_sdk.MangaAPI()
    result_json_string = obj.chapter_detail("martial-peak-chapter")
    result_json = json.loads(result_json_string)
    print(result_json)
