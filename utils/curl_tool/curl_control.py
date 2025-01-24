import re
import json
import pandas as pd


def _parse_curl(curl_data):
    url_match = re.search(r"curl '(.*?)'", curl_data)
    if url_match:
        url = str(url_match.group(1))
    else:
        return None

    header_matches = re.findall(r"-H '(.*?)'", curl_data)
    headers = {}
    for header in header_matches:
        key, value = header.split(": ", 1)
        headers[key] = value

    data_match = re.search(r"--data-raw '(.*)'", curl_data)
    data = json.loads(data_match.group(1)) if data_match else {}

    cookies = {}
    cookie_header = headers.get("cookie", "")
    cookie_matches = re.findall(r"([^=]+)=([^;]+);?", cookie_header)
    for key, value in cookie_matches:
        cookies[key] = value

    method_match = re.search(r"-X\s+([A-Z]+)\s+", curl_data)
    method = method_match.group(1) if method_match else "POST"

    return {
        "url": url,
        "headers": headers,
        "data": data,
        "cookies": cookies,
        "method": method
    }


def curl_to_excel(curl_data, excel_file):
    parsed_data = _parse_curl(curl_data)

    if parsed_data is not None:
        result = {
            "api-case-id": None,
            "项目模块": None,
            "用例标题": None,
            "依赖": {'code': 0, 'exp': [{'use': '', 'key': ''}], 'get': [''], 'set': ['']},
            "url": parsed_data["url"],
            "method": parsed_data["method"],
            "cookies": parsed_data["cookies"],
            "headers": parsed_data["headers"],
            "data_type": "json or form-data",
            "data": parsed_data["data"],
            "response": None,
            "预期结果": {'type': '==', 'key': '', 'value': ''},
            "备注": None
        }

        keys = list(result.keys())
        df = pd.DataFrame(columns=keys)
        df = df._append(result, ignore_index=True)
        writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        header_format = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top', 'border': 1})
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        for i, col in enumerate(df.columns):
            column_len = max(df[col].astype(str).apply(len).max(), len(col)) + 2
            worksheet.set_column(i, i, column_len)
        writer.close()


if __name__ == '__main__':
    excel_file = '../../data/kolsaas/Brands.xlsx'
    data_curl = """
curl 'https://kol.test.55haitao.com/api/brandData/showBrandList' \
  -H 'authority: kol.test.55haitao.com' \
  -H 'accept: */*' \
  -H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6' \
  -H 'authorization: Auth:JDJ5JDEwJFdqaWdGT2RaNGVJY01EVnlqYjlnVHV2S3VRNnhRTXZxbXMxSGdOMmZMNFpMd2hqLjNEem1X' \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -H 'origin: https://kol-saas.test.55haitao.com' \
  -H 'pragma: no-cache' \
  -H 'referer: https://kol-saas.test.55haitao.com/' \
  -H 'sec-ch-ua: "Chromium";v="118", "Microsoft Edge";v="118", "Not=A?Brand";v="99"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.76' \
  --data-raw '{"pageNum":1,"pageSize":10}' \
  --compressed
    """
    curl_to_excel(data_curl, excel_file)
    print(f"Excel 文件已生成: {excel_file}")
