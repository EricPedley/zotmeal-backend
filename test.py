from api.index import get_diner_json
import json

if __name__=="__main__":
    with open('eatery_dummy.json', 'w', encoding = 'utf-8') as f:
        data = get_diner_json('anteatery')
        json.dump(data, f, ensure_ascii = False, indent = 4)

    with open('brandy_dummy.json', 'w', encoding = 'utf-8') as f:
        data = get_diner_json('brandywine')
        json.dump(data, f, ensure_ascii = False, indent = 4)
